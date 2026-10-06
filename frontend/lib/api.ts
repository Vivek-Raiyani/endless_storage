const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export interface VirtualFolder {
  id: string;
  name: string;
  parent_id: string | null;
  owner_id: string;
  color: string | null;
  starred: boolean;
  shared: boolean;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface VirtualFile {
  id: string;
  name: string;
  folder_id: string | null;
  size: number;
  thumbnail?: string | null;
  mime_type: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface DataResponse<T> {
  data: T;
  message?: string;
}

export const api = {
  async fetch<T>(endpoint: string, options: RequestInit & { _retry?: boolean } = {}): Promise<T> {
    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      credentials: 'include', // Important for sending session cookies
    });
    
    if (res.status === 401 && !options._retry && endpoint !== '/auth/refresh' && endpoint !== '/auth/signin') {
      try {
        // Attempt to refresh the token
        const refreshRes = await fetch(`${API_BASE_URL}/auth/refresh`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
        });
        
        if (refreshRes.ok) {
          // Retry the original request
          return api.fetch<T>(endpoint, { ...options, _retry: true });
        }
      } catch (e) {
        // Fall through to regular error handling
      }
    }

    if (!res.ok) {
      let error = 'API Error';
      try {
        const data = await res.json();
        error = data.detail || (typeof data === 'object' ? JSON.stringify(data) : data);
      } catch {
        // ignore
      }
      throw new Error(typeof error === 'string' ? error : JSON.stringify(error));
    }
    
    return res.json() as Promise<T>;
  },

  auth: {
    signin: (data: Record<string, string>) => {
      return api.fetch<void>('/auth/signin', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },
    signup: (data: Record<string, string | boolean>) => {
      return api.fetch<void>('/auth/signup', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },
    me: () => {
      return api.fetch<{ data: { id: string; email: string; first_name: string; last_name: string } }>('/users/profile');
    },
    signout: () => {
      return api.fetch<void>('/auth/signout', { method: 'POST' });
    }
  },

  storage: {
    list: () => {
      return api.fetch<{ data: Array<{ id: string; provider_account_email: string; total_bytes: number; used_bytes: number; available_bytes: number }> }>('/storage-accounts');
    },
    getSummary: () => {
      return api.fetch<{ data: { accounts_count: number; active_accounts_count: number; total_bytes: number; used_bytes: number; available_bytes: number; trash_bytes: number } }>('/storage-accounts/summary');
    },
    getDisconnectPreview: (accountId: string) => {
      return api.fetch<{ data: { can_migrate: boolean; affected_files_count: number; total_bytes_to_move: number; available_bytes_elsewhere: number } }>(`/storage-accounts/${accountId}/disconnect-preview`);
    },
    disconnect: (accountId: string, action: 'migrate' | 'delete') => {
      return api.fetch<void>(`/storage-accounts/${accountId}/disconnect`, {
        method: 'POST',
        body: JSON.stringify({ action }),
      });
    }
  },

  folders: {
    search: (q: string) => {
      return api.fetch<DataResponse<VirtualFolder[]>>(`/folders/search?q=${encodeURIComponent(q)}`);
    },
    list: (parentId?: string | null) => {
      const qs = parentId ? `?parent_id=${parentId}` : '';
      return api.fetch<DataResponse<VirtualFolder[]>>(`/folders/${qs}`);
    },
    create: (name: string, parentId?: string | null) => {
      return api.fetch<DataResponse<VirtualFolder>>('/folders/', {
        method: 'POST',
        body: JSON.stringify({ name, parent_id: parentId }),
      });
    },
    get: (folderId: string) => {
      return api.fetch<DataResponse<VirtualFolder>>(`/folders/${folderId}`);
    },
    update: (folderId: string, data: { name?: string; parent_id?: string | null; color?: string | null; starred?: boolean }) => {
      return api.fetch<DataResponse<VirtualFolder>>(`/folders/${folderId}`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      });
    },
    delete: (folderId: string) => {
      return api.fetch<void>(`/folders/${folderId}`, { method: 'DELETE' });
    },
    share: (folderId: string, target_user_email: string, role: 'viewer' | 'editor' = 'viewer') => {
      return api.fetch<{ message: string }>(`/folders/${folderId}/share`, {
        method: 'POST',
        body: JSON.stringify({ target_user_email, role })
      });
    },
    listShares: (folderId: string) => {
      return api.fetch<{ data: Array<{ user_id: string; email: string; role: string; first_name?: string; last_name?: string }> }>(`/folders/${folderId}/share`);
    },
    unshare: (folderId: string, target_user_email: string) => {
      return api.fetch<{ message: string }>(`/folders/${folderId}/share/${target_user_email}`, { method: 'DELETE' });
    }
  },

  files: {
    search: (q: string) => {
      return api.fetch<DataResponse<VirtualFile[]>>(`/files/search?q=${encodeURIComponent(q)}`);
    },
    list: (folderId?: string | null) => {
      const qs = folderId ? `?folder_id=${folderId}` : '';
      return api.fetch<DataResponse<VirtualFile[]>>(`/files/${qs}`);
    },
    update: (fileId: string, data: { name?: string; folder_id?: string | null; starred?: boolean }) => {
      return api.fetch<{ data: VirtualFile }>(`/files/${fileId}`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      });
    },
    delete: (fileId: string, permanent: boolean = false) => {
      const qs = permanent ? '?permanent=true' : '';
      return api.fetch<void>(`/files/${fileId}${qs}`, { method: 'DELETE' });
    },
    restore: (fileId: string) => {
      return api.fetch<{ data: VirtualFile }>(`/files/${fileId}/restore`, { method: 'POST' });
    },
    upload: (data: { name: string; size: number;
  thumbnail?: string | null; mime_type: string; folder_id?: string | null }) => {
      return api.fetch<{ data: { upload_id: string; file_id: string; chunk_size: number;
  thumbnail?: string | null; total_chunks: number; chunks: Array<{ chunk_id: string; index: number; offset: number; size: number;
  thumbnail?: string | null; upload_url: string; storage_account_id: string }> } }>('/files/upload', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },
    confirmChunk: (fileId: string, data: { chunk_index: number; provider_file_id: string; checksum?: string }) => {
      return api.fetch<{ message: string }>(`/files/${fileId}/chunks/confirm`, {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },
    getStatus: (fileId: string) => {
      return api.fetch<{ data: { id: string; file_id: string; total_chunks: number; completed_chunks: number; status: string } }>(`/files/${fileId}/upload-status`);
    }
  }
};
