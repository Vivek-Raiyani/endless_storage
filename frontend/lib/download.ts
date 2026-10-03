import * as fflate from 'fflate';
import { api } from './api';
// streamSaver.mitm = 'https://...'; (default is ok for most modern browsers in same origin or localhost)

async function verifyChunksPreFlight(chunks: Array<{ download_url: string; access_token: string }>) {
  // Check chunks in batches of 20 to avoid overwhelming the browser's network queue
  const BATCH_SIZE = 20;
  for (let i = 0; i < chunks.length; i += BATCH_SIZE) {
    const batch = chunks.slice(i, i + BATCH_SIZE);
    await Promise.all(batch.map(async (chunk) => {
      const res = await fetch(chunk.download_url, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${chunk.access_token}`,
          'Range': 'bytes=0-0'
        }
      });
      
      if (!res.ok) {
        throw new Error(`File is corrupted. A required part is missing or inaccessible on Google Drive.`);
      }
      
      // Instantly cancel the body stream since we only wanted to verify existence
      if (res.body) {
        await res.body.cancel();
      }
    }));
  }
}

export async function downloadFile(fileId: string, filename: string) {
  let writer: any = null;
  try {
    // 1. Prepare download (get chunks)
    const res = await api.fetch<{ data: { chunks: Array<{ download_url: string; access_token: string; chunk_index: number }> } }>(`/files/${fileId}/download`);
    const { chunks } = res.data;

    if (!chunks || chunks.length === 0) {
      throw new Error('No chunks found for this file.');
    }

    // Pre-flight check: ensure all chunks exist before starting the download
    await verifyChunksPreFlight(chunks);

    const streamSaver = (await import('streamsaver')).default;

    // 2. Setup StreamSaver
    const fileStream = streamSaver.createWriteStream(filename);
    writer = fileStream.getWriter();

    // 3. Download chunks sequentially to avoid memory issues (or could do limited concurrency)
    for (const chunk of chunks) {
      const chunkRes = await fetch(chunk.download_url, {
        headers: {
          'Authorization': `Bearer ${chunk.access_token}`
        }
      });
      
      if (!chunkRes.ok) {
        throw new Error(`Failed to download chunk ${chunk.chunk_index}`);
      }

      if (chunkRes.body) {
        const reader = chunkRes.body.getReader();
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          await writer.write(value);
        }
      }
    }
    
    await writer.close();
  } catch (error) {
    if (writer) {
      try { await writer.abort(error); } catch (e) {}
    }
    
    // User cancelled the download (stream aborted)
    if (error === undefined || (error instanceof Error && error.name === 'AbortError')) {
      console.log('Download cancelled by user.');
      return;
    }

    console.error('File download failed:', error);
    alert('Download failed: ' + (error instanceof Error ? error.message : 'Unknown error'));
  }
}

export async function downloadFolder(folderId: string, folderName: string) {
  let writer: any = null;
  try {
    // 1. Prepare folder download (get manifest)
    const res = await api.fetch<{ data: { files: Array<{ relative_path: string; chunks: Array<{ download_url: string; access_token: string }> }> } }>(`/folders/${folderId}/download`);
    const manifest = res.data; 

    // manifest should have a flat list of files with relative_path and their chunks.
    if (!manifest || !manifest.files) {
      throw new Error('Invalid folder manifest.');
    }

    // Pre-flight check: ensure all chunks across all files exist
    const allChunks = manifest.files.flatMap(f => f.chunks);
    await verifyChunksPreFlight(allChunks);

    const streamSaver = (await import('streamsaver')).default;

    // 2. Setup StreamSaver for a ZIP file
    const fileStream = streamSaver.createWriteStream(`${folderName}.zip`);
    writer = fileStream.getWriter();

    let writePromise = Promise.resolve();
    let zipError: Error | null = null;

    // 3. Setup fflate Zip instance
    const zip = new fflate.Zip((err, data, final) => {
      if (err) {
        console.error('ZIP Error:', err);
        zipError = err;
        return;
      }
      if (data) {
        writePromise = writePromise.then(() => writer.write(data));
      }
      if (final) {
        writePromise = writePromise.then(() => writer.close());
      }
    });

    // 4. Stream each file into the zip
    for (const file of manifest.files) {
      const zipFile = new fflate.ZipDeflate(file.relative_path, { level: 0 }); // level 0 is faster
      zip.add(zipFile);

      for (const chunk of file.chunks) {
        const chunkRes = await fetch(chunk.download_url, {
          headers: {
            'Authorization': `Bearer ${chunk.access_token}`
          }
        });

        if (!chunkRes.ok) {
          throw new Error(`Failed to download chunk for ${file.relative_path}`);
        }

        if (chunkRes.body) {
          const reader = chunkRes.body.getReader();
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            if (zipError) throw zipError;
            
            // Push chunk to zip file
            zipFile.push(value, false);
            // Wait for backpressure to resolve before reading the next chunk
            await writePromise;
          }
        }
      }
      // Finish this file
      zipFile.push(new Uint8Array(0), true);
      await writePromise;
    }
    
    // 5. Finalize the ZIP
    zip.end();
    await writePromise;
    
  } catch (error) {
    if (writer) {
      try { await writer.abort(error); } catch (e) {}
    }

    // User cancelled the download (stream aborted)
    if (error === undefined || (error instanceof Error && error.name === 'AbortError')) {
      console.log('Folder download cancelled by user.');
      return;
    }

    console.error('Folder download failed:', error);
    alert('Folder download failed: ' + (error instanceof Error ? error.message : 'Unknown error'));
  }
}
