'use client';

import React, { useEffect, useState } from 'react';
import { api, VirtualFolder, VirtualFile } from '@/lib/api';
import { Folder, File as FileIcon, MoreVertical, FileDown, Trash2, FolderDown, FolderPlus, X, RotateCcw } from 'lucide-react';
import Link from 'next/link';
import { downloadFile, downloadFolder } from '@/lib/download';
import { UploadManager } from '@/lib/upload';
import { Upload } from 'lucide-react';
import { toast } from 'sonner';

export function DriveView({ currentFolderId }: { currentFolderId: string | null }) {
  const [folders, setFolders] = useState<VirtualFolder[]>([]);
  const [files, setFiles] = useState<VirtualFile[]>([]);
  const [currentFolder, setCurrentFolder] = useState<VirtualFolder | null>(null);
  const [loading, setLoading] = useState(true);
  const [authError, setAuthError] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<{ [key: string]: { progress: number; name: string; abort: () => void } }>({});
  const [isNewFolderModalOpen, setIsNewFolderModalOpen] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');
  
  const [fileToDelete, setFileToDelete] = useState<string | null>(null);
  const [fileToDeleteForever, setFileToDeleteForever] = useState<string | null>(null);

  const handleCreateFolder = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newFolderName.trim()) return;

    try {
      await api.folders.create(newFolderName, currentFolderId);
      setIsNewFolderModalOpen(false);
      setNewFolderName('');
      toast.success('Folder created successfully');

      // Refresh folders
      const foldersRes = await api.folders.list(currentFolderId);
      setFolders(foldersRes.data);
    } catch (error) {
      console.error('Failed to create folder:', error);
      toast.error('Failed to create folder');
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Reset input so the same file can be uploaded again if needed
    e.target.value = '';

    const tempId = Math.random().toString(36).substring(7);

    const manager = new UploadManager(file, currentFolderId, (progress) => {
      setUploadProgress(prev => {
        if (!prev[tempId]) return prev;
        return { ...prev, [tempId]: { ...prev[tempId], progress } };
      });
    });

    setUploadProgress(prev => ({ ...prev, [tempId]: { progress: 0, name: file.name, abort: () => manager.abort() } }));

    try {
      await manager.upload();

      // Refresh the file list
      const filesRes = await api.files.list(currentFolderId);
      setFiles(filesRes.data);
      toast.success(`Uploaded ${file.name}`);
    } catch (error) {
      if (error instanceof Error && error.message === 'Upload aborted') {
        toast.info(`Cancelled upload of ${file.name}`);
      } else {
        console.error('Upload failed:', error);
        toast.error('Upload failed. Do you have connected storage accounts?');
      }
    } finally {
      setUploadProgress(prev => {
        const newProgress = { ...prev };
        delete newProgress[tempId];
        return newProgress;
      });
    }
  };

  const isSpecialView = currentFolderId === 'shared' || currentFolderId === 'recent' || currentFolderId === 'trash';

  const handleDrop = async (e: React.DragEvent, targetFolderId: string | null) => {
    e.preventDefault();
    e.currentTarget.classList.remove('ring-4', 'ring-blue-400', 'ring-opacity-50');

    try {
      const data = e.dataTransfer.getData('application/json');
      if (!data) return;
      const { type, id } = JSON.parse(data);

      if (id === targetFolderId) return; // Can't move a folder into itself

      if (type === 'file') {
        await api.files.update(id, { folder_id: targetFolderId });
        setFiles(prev => prev.filter(f => f.id !== id));
        toast.success('File moved successfully');
      } else if (type === 'folder') {
        await api.folders.update(id, { parent_id: targetFolderId });
        setFolders(prev => prev.filter(f => f.id !== id));
        toast.success('Folder moved successfully');
      }
    } catch (error) {
      console.error('Failed to move item:', error);
      toast.error('Failed to move item');
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.currentTarget.classList.add('ring-4', 'ring-blue-400', 'ring-opacity-50');
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.currentTarget.classList.remove('ring-4', 'ring-blue-400', 'ring-opacity-50');
  };

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        if (isSpecialView) {
          const filesRes = await api.fetch<{ data: any[] }>(`/files/${currentFolderId}`);
          setFolders([]); // Special views only show files for now
          setFiles(filesRes.data);
          setCurrentFolder(null);
        } else {
          const [foldersRes, filesRes, currentFolderRes] = await Promise.all([
            api.folders.list(currentFolderId),
            api.files.list(currentFolderId),
            currentFolderId ? api.folders.get(currentFolderId) : Promise.resolve({ data: null })
          ]);
          setFolders(foldersRes.data);
          setFiles(filesRes.data);
          setCurrentFolder(currentFolderRes.data);
        }
      } catch (error) {
        if (error instanceof Error && (error.message.includes('Not authenticated') || error.message.includes('Unauthorized') || error.message.includes('Could not validate credentials'))) {
          try { await api.auth.signout(); } catch (e) { }
          setAuthError(true);
        } else {
          console.error('Failed to load drive contents:', error);
        }
      } finally {
        setLoading(false);
      }
    }
    loadData();

    const handleOpenFolderModal = () => setIsNewFolderModalOpen(true);
    window.addEventListener('openNewFolderModal', handleOpenFolderModal);

    return () => window.removeEventListener('openNewFolderModal', handleOpenFolderModal);
  }, [currentFolderId, isSpecialView]);

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (authError) {
    if (typeof window !== 'undefined') {
      window.location.assign('/');
    }
    return null;
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-normal text-gray-800 flex items-center gap-2 capitalize">
          {isSpecialView ? (
            currentFolderId === 'shared' ? 'Shared with me' : currentFolderId
          ) : currentFolderId ? (
            <>
              <Link
                href="/drive"
                className="hover:underline text-gray-600 px-2 py-1 rounded-lg transition-colors"
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={(e) => handleDrop(e, null)}
              >
                My Drive
              </Link>
              <span className="text-gray-400">/</span>
              <span
                className="px-2 py-1 rounded-lg transition-colors"
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={(e) => handleDrop(e, currentFolder?.parent_id || null)}
                title="Drop items here to move them up one level"
              >
                {currentFolder?.name || 'Loading...'}
              </span>
            </>
          ) : (
            'My Drive'
          )}
        </h1>
        {!isSpecialView && (
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsNewFolderModalOpen(true)}
              className="flex items-center gap-2 bg-white text-gray-700 border border-gray-200 px-4 py-2 rounded-full font-medium hover:bg-gray-50 transition-colors shadow-sm cursor-pointer text-sm"
            >
              <FolderPlus className="w-4 h-4" />
              New Folder
            </button>
            <label className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-full font-medium hover:bg-blue-700 transition-colors shadow-sm cursor-pointer text-sm">
              <Upload className="w-4 h-4" />
              Upload File
              <input type="file" id="global-file-upload" className="hidden" onChange={handleFileUpload} />
            </label>
          </div>
        )}
      </div>

      <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
        {Object.entries(uploadProgress).map(([id, upload]) => (
          <div key={id} className="bg-white border border-gray-200 rounded-xl shadow-lg p-4 flex items-center justify-between w-80 animate-in slide-in-from-bottom-5">
            <div className="flex items-center gap-3 overflow-hidden">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center shrink-0">
                <Upload className="w-4 h-4 text-blue-600 animate-bounce" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-800 truncate" title={upload.name}>Uploading {upload.name}</p>
                <div className="w-full h-1.5 bg-gray-100 rounded-full mt-1.5 overflow-hidden">
                  <div
                    className="h-full bg-blue-500 rounded-full transition-all duration-300"
                    style={{ width: `${Math.max(5, upload.progress * 100)}%` }}
                  />
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2 shrink-0 ml-3">
              <span className="text-xs font-medium text-blue-600 w-8 text-right">{Math.round(upload.progress * 100)}%</span>
              <button
                onClick={() => upload.abort()}
                className="p-1 hover:bg-gray-100 rounded-full transition-colors text-gray-400 hover:text-red-500"
                title="Cancel upload"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {folders.length === 0 && files.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center text-gray-400">
          <Folder className="w-20 h-20 mb-4 text-gray-200" />
          <p className="text-lg">This folder is empty</p>
        </div>
      ) : (
        <div className="flex-1 overflow-auto">
          {folders.length > 0 && (
            <div className="mb-8">
              <h2 className="text-sm font-medium text-gray-600 mb-4">Folders</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {folders.map(folder => (
                  <Link href={`/drive/${folder.id}`} key={folder.id} draggable onDragStart={(e) => {
                    e.dataTransfer.setData('application/json', JSON.stringify({ type: 'folder', id: folder.id }));
                  }}>
                    <div
                      className="flex items-center gap-3 p-3 bg-gray-50 hover:bg-gray-100 border border-transparent hover:border-gray-300 rounded-xl transition-all cursor-pointer group"
                      onDragOver={handleDragOver}
                      onDragLeave={handleDragLeave}
                      onDrop={(e) => handleDrop(e, folder.id)}
                    >
                      <Folder className="w-6 h-6 text-gray-600 fill-gray-500/20 pointer-events-none" />
                      <span className="flex-1 font-medium text-sm text-gray-800 truncate pointer-events-none">{folder.name}</span>

                      <button
                        className="p-1.5 opacity-0 group-hover:opacity-100 hover:bg-gray-200 rounded-full transition-all"
                        onClick={(e) => {
                          e.preventDefault();
                          downloadFolder(folder.id, folder.name);
                        }}
                        title="Download Folder"
                      >
                        <FolderDown className="w-4 h-4 text-gray-600" />
                      </button>
                      <button className="p-1.5 opacity-0 group-hover:opacity-100 hover:bg-gray-200 rounded-full transition-all">
                        <MoreVertical className="w-4 h-4 text-gray-600" />
                      </button>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          )}

          {files.length > 0 && (
            <div>
              <h2 className="text-sm font-medium text-gray-600 mb-4">Files</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {files.map(file => (
                  <div
                    key={file.id}
                    className="flex flex-col bg-gray-50 hover:bg-gray-100 border border-transparent hover:border-gray-300 rounded-xl transition-all cursor-pointer group overflow-hidden"
                    draggable={file.status !== 'uploading'}
                    onDragStart={(e) => {
                      e.dataTransfer.setData('application/json', JSON.stringify({ type: 'file', id: file.id }));
                    }}
                  >
                    <div className="h-32 bg-white border-b border-gray-100 flex items-center justify-center relative">
                      <FileIcon className={`w-12 h-12 pointer-events-none ${file.status === 'uploading' ? 'text-gray-300' : 'text-blue-500/50'}`} />
                      <div className="absolute inset-0 bg-black/5 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                        {currentFolderId === 'trash' ? (
                          <>
                            <button
                              className="p-2 bg-white rounded-full hover:scale-110 transition-transform shadow-sm"
                              title="Restore File"
                              onClick={async (e) => {
                                e.preventDefault();
                                e.stopPropagation();
                                try {
                                  await api.files.restore(file.id);
                                  setFiles(prev => prev.filter(f => f.id !== file.id));
                                  toast.success('File restored');
                                } catch (error) {
                                  toast.error('Failed to restore file');
                                }
                              }}
                            >
                              <RotateCcw className="w-5 h-5 text-blue-600" />
                            </button>
                            <button
                              className="p-2 bg-white rounded-full hover:scale-110 transition-transform shadow-sm"
                              title="Delete Forever"
                              onClick={(e) => {
                                e.preventDefault();
                                e.stopPropagation();
                                setFileToDeleteForever(file.id);
                              }}
                            >
                              <Trash2 className="w-5 h-5 text-red-600" />
                            </button>
                          </>
                        ) : (
                          <>
                            <button
                              className="p-2 bg-white rounded-full hover:scale-110 transition-transform shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
                              onClick={(e) => {
                                e.preventDefault();
                                e.stopPropagation();
                                downloadFile(file.id, file.name);
                              }}
                              title="Download File"
                              disabled={file.status === 'uploading'}
                            >
                              <FileDown className="w-5 h-5 text-gray-700" />
                            </button>
                            <button
                              className="p-2 bg-white rounded-full hover:scale-110 transition-transform shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
                              title="Delete File"
                              disabled={file.status === 'uploading'}
                              onClick={async (e) => {
                                e.preventDefault();
                                e.stopPropagation();
                                setFileToDelete(file.id);
                              }}
                            >
                              <Trash2 className="w-5 h-5 text-red-600" />
                            </button>
                          </>
                        )}
                      </div>
                    </div>
                    <div className="p-3 flex items-center gap-3">
                      <FileIcon className={`w-5 h-5 shrink-0 ${file.status === 'uploading' ? 'text-gray-400' : 'text-blue-500'}`} />
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-sm text-gray-800 truncate">{file.name}</p>
                        <p className="text-xs text-gray-500 mt-0.5">
                          {(file.size / 1024 / 1024).toFixed(2)} MB
                          {file.status === 'uploading' && <span className="ml-2 text-blue-500">Uploading...</span>}
                        </p>
                      </div>
                      <button className="p-1.5 opacity-0 group-hover:opacity-100 hover:bg-gray-200 rounded-full transition-all shrink-0">
                        <MoreVertical className="w-4 h-4 text-gray-600" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* New Folder Modal */}
      {isNewFolderModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between p-4 border-b border-gray-100">
              <h2 className="text-lg font-semibold text-gray-900">New Folder</h2>
              <button onClick={() => setIsNewFolderModalOpen(false)} className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-colors">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleCreateFolder} className="p-4">
              <input
                type="text"
                autoFocus
                placeholder="Folder Name"
                className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={newFolderName}
                onChange={(e) => setNewFolderName(e.target.value)}
              />
              <div className="flex justify-end gap-3 mt-6">
                <button
                  type="button"
                  onClick={() => setIsNewFolderModalOpen(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-full transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={!newFolderName.trim()}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded-full transition-colors"
                >
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      {/* Delete File Modal */}
      {fileToDelete && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in-95 duration-200">
            <div className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Delete File</h2>
              <p className="text-gray-500 mb-6">Are you sure you want to move this file to trash? It can be restored later.</p>
              <div className="flex justify-end gap-3">
                <button
                  onClick={() => setFileToDelete(null)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-full transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={async () => {
                    try {
                      await api.files.delete(fileToDelete);
                      setFiles(prev => prev.filter(f => f.id !== fileToDelete));
                      toast.success('File moved to trash');
                    } catch (error) {
                      toast.error('Failed to delete file');
                    } finally {
                      setFileToDelete(null);
                    }
                  }}
                  className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-full transition-colors"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
      {/* Delete File Forever Modal */}
      {fileToDeleteForever && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in-95 duration-200">
            <div className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Delete Forever</h2>
              <p className="text-gray-500 mb-6">This file will be permanently deleted and its chunks queued for removal from Google Drive. You cannot undo this action.</p>
              <div className="flex justify-end gap-3">
                <button
                  onClick={() => setFileToDeleteForever(null)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-full transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={async () => {
                    try {
                      await api.files.delete(fileToDeleteForever, true);
                      setFiles(prev => prev.filter(f => f.id !== fileToDeleteForever));
                      toast.success('File deleted permanently');
                    } catch (error) {
                      toast.error('Failed to permanently delete file');
                    } finally {
                      setFileToDeleteForever(null);
                    }
                  }}
                  className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-full transition-colors"
                >
                  Delete Forever
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
