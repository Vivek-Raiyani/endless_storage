import { api } from './api';

export type UploadProgressCallback = (progress: number, totalChunks: number, uploadedChunks: number) => void;

export class UploadManager {
  private file: File;
  private folderId?: string | null;
  private onProgress?: UploadProgressCallback;

  private aborted: boolean = false;
  private activeXhrs: XMLHttpRequest[] = [];

  constructor(file: File, folderId?: string | null, onProgress?: UploadProgressCallback) {
    this.file = file;
    this.folderId = folderId;
    this.onProgress = onProgress;
  }

  abort() {
    this.aborted = true;
    for (const xhr of this.activeXhrs) {
      xhr.abort();
    }
  }

  async upload(): Promise<string> {
    // Step 1: Initiate upload with the backend
    const initiateRes = await api.files.upload({
      name: this.file.name,
      size: this.file.size,
      mime_type: this.file.type || 'application/octet-stream',
      folder_id: this.folderId,
    });

    const { file_id, chunks } = initiateRes.data;

    let uploadedChunks = 0;

    // We can upload chunks in parallel to speed things up.
    // However, to avoid overloading the browser or network, we limit concurrency to 3.
    const concurrency = 3;
    let i = 0;

    // Track the bytes uploaded for each chunk separately
    const chunkProgress: number[] = new Array(chunks.length).fill(0);

    const worker = async () => {
      while (i < chunks.length) {
        if (this.aborted) {
          throw new Error('Upload aborted');
        }

        const chunkIndex = i++;
        const chunk = chunks[chunkIndex];

        const endByte = Math.min(chunk.offset + chunk.size, this.file.size);
        const chunkBlob = this.file.slice(chunk.offset, endByte);

        // Upload using XMLHttpRequest to get real-time upload progress
        const providerFileId = await new Promise<string>((resolve, reject) => {
          const xhr = new XMLHttpRequest();
          this.activeXhrs.push(xhr);

          xhr.open('PUT', chunk.upload_url, true);
          
          xhr.upload.onprogress = (event) => {
            if (event.lengthComputable) {
              chunkProgress[chunkIndex] = event.loaded;
              if (this.onProgress) {
                const totalLoaded = chunkProgress.reduce((a, b) => a + b, 0);
                this.onProgress(totalLoaded / this.file.size, chunks.length, uploadedChunks);
              }
            }
          };

          xhr.onload = () => {
            this.activeXhrs = this.activeXhrs.filter(x => x !== xhr);
            if (xhr.status >= 200 && xhr.status < 300) {
              try {
                const driveData = JSON.parse(xhr.responseText);
                resolve(driveData.id);
              } catch (e) {
                reject(new Error('Failed to parse Google Drive response'));
              }
            } else {
              reject(new Error(`Failed to upload chunk ${chunk.index} to Google Drive`));
            }
          };

          xhr.onerror = () => {
             this.activeXhrs = this.activeXhrs.filter(x => x !== xhr);
             reject(new Error('Network error during upload'));
          };

          xhr.onabort = () => {
             this.activeXhrs = this.activeXhrs.filter(x => x !== xhr);
             reject(new Error('Upload aborted'));
          };
          
          xhr.send(chunkBlob);
        });

        if (this.aborted) {
           throw new Error('Upload aborted');
        }

        // Confirm with our backend that the chunk is uploaded
        await api.files.confirmChunk(file_id, {
          chunk_index: chunk.index,
          provider_file_id: providerFileId,
        });

        uploadedChunks++;
        chunkProgress[chunkIndex] = chunkBlob.size; // Ensure it's marked exactly 100%
        if (this.onProgress) {
          const totalLoaded = chunkProgress.reduce((a, b) => a + b, 0);
          this.onProgress(totalLoaded / this.file.size, chunks.length, uploadedChunks);
        }
      }
    };

    const workers = [];
    for (let w = 0; w < concurrency; w++) {
      workers.push(worker());
    }

    try {
      await Promise.all(workers);
    } catch (e) {
      if (this.aborted && file_id) {
        // Clean up the partially uploaded file from the database permanently
        try {
          await api.files.delete(file_id, true);
        } catch (cleanupErr) {
          console.error('Failed to clean up aborted file:', cleanupErr);
        }
      }
      throw e;
    }

    return file_id;
  }
}
