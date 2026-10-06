import React, { useEffect, useState } from 'react';
import { X, Download, Loader2 } from 'lucide-react';
import { VirtualFile } from '../../lib/api';
import { getFileBlob, downloadFile } from '../../lib/download';
import { toast } from 'sonner';

interface Props {
  file: VirtualFile;
  onClose: () => void;
}

export function FilePreviewModal({ file, onClose }: Props) {
  const [blobUrl, setBlobUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const isImage = file.mime_type.startsWith('image/');
  const isVideo = file.mime_type.startsWith('video/');

  useEffect(() => {
    let activeUrl: string | null = null;
    let isMounted = true;

    async function loadPreview() {
      // Hard limit for preview to avoid browser memory crash (e.g. 500MB)
      if (file.size > 500 * 1024 * 1024) {
        setError('File is too large for browser preview. Please download it.');
        setLoading(false);
        return;
      }

      try {
        const blob = await getFileBlob(file.id, file.mime_type, (p) => {
          if (isMounted) setProgress(p);
        });
        if (!isMounted) return;
        
        activeUrl = URL.createObjectURL(blob);
        setBlobUrl(activeUrl);
      } catch (err) {
        if (!isMounted) return;
        console.error('Preview error:', err);
        setError('Failed to load preview. The file might be corrupted.');
      } finally {
        if (isMounted) setLoading(false);
      }
    }

    if (isImage || isVideo) {
      loadPreview();
    } else {
      setError('Preview is not available for this file type.');
      setLoading(false);
    }

    return () => {
      isMounted = false;
      if (activeUrl) {
        URL.revokeObjectURL(activeUrl);
      }
    };
  }, [file]);

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/90 backdrop-blur-sm p-4 sm:p-8 animate-in fade-in duration-200">
      <div className="absolute top-4 right-4 flex items-center gap-4 z-10">
        <button
          onClick={() => downloadFile(file.id, file.name)}
          className="p-2 text-white/70 hover:text-white bg-black/50 hover:bg-black/70 rounded-full transition-colors"
          title="Download"
        >
          <Download className="w-6 h-6" />
        </button>
        <button
          onClick={onClose}
          className="p-2 text-white/70 hover:text-white bg-black/50 hover:bg-black/70 rounded-full transition-colors"
          title="Close"
        >
          <X className="w-6 h-6" />
        </button>
      </div>

      <div className="absolute top-4 left-4 z-10">
        <p className="text-white font-medium drop-shadow-md truncate max-w-[250px] sm:max-w-md">
          {file.name}
        </p>
        <p className="text-white/70 text-sm drop-shadow-md">
          {(file.size / 1024 / 1024).toFixed(2)} MB
        </p>
      </div>

      <div className="w-full h-full flex items-center justify-center relative">
        {loading ? (
          <div className="flex flex-col items-center gap-4 text-white">
            <Loader2 className="w-10 h-10 animate-spin text-white/50" />
            <div className="text-center">
              <p className="font-medium mb-1">Loading preview...</p>
              <div className="w-48 h-2 bg-white/20 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-white rounded-full transition-all duration-300"
                  style={{ width: `${progress * 100}%` }}
                />
              </div>
            </div>
          </div>
        ) : error ? (
          <div className="bg-white/10 p-6 rounded-2xl border border-white/20 text-center max-w-sm backdrop-blur-md">
            <p className="text-white font-medium mb-4">{error}</p>
            <button
              onClick={() => {
                onClose();
                downloadFile(file.id, file.name);
              }}
              className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-full font-medium transition-colors"
            >
              Download File
            </button>
          </div>
        ) : blobUrl && isImage ? (
          <img 
            src={blobUrl} 
            alt={file.name}
            className="max-w-full max-h-full object-contain rounded-lg shadow-2xl animate-in zoom-in-95 duration-300"
          />
        ) : blobUrl && isVideo ? (
          <video 
            src={blobUrl} 
            controls 
            autoPlay 
            className="max-w-full max-h-full rounded-lg shadow-2xl animate-in zoom-in-95 duration-300 outline-none"
          />
        ) : null}
      </div>
    </div>
  );
}
