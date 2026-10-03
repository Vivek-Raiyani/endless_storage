'use client';
import React, { useEffect, useState } from 'react';
import { Search, HelpCircle, Settings, LayoutGrid, LogOut, HardDrive, Plus, X, AlertTriangle } from 'lucide-react';
import { api } from '@/lib/api';
import { toast } from 'sonner';

export function Header() {
  const [user, setUser] = useState<{ email: string; first_name: string; last_name: string } | null>(null);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [storageAccounts, setStorageAccounts] = useState<Array<{ id: string; provider_account_email: string; total_bytes: number; used_bytes: number; available_bytes: number }>>([]);
  const [accountToDisconnect, setAccountToDisconnect] = useState<any>(null);
  const [disconnectPreview, setDisconnectPreview] = useState<{ can_migrate: boolean; affected_files_count: number; total_bytes_to_move: number; available_bytes_elsewhere: number } | null>(null);

  useEffect(() => {
    async function fetchUser() {
      try {
        const res = await api.auth.me();
        setUser(res.data);
      } catch {
        // User not logged in, ignore
      }
    }
    fetchUser();

    const handleOpenStorageSettings = () => {
      setIsSettingsOpen(true);
      loadStorageAccounts();
    };
    
    window.addEventListener('openStorageSettings', handleOpenStorageSettings);
    return () => window.removeEventListener('openStorageSettings', handleOpenStorageSettings);
  }, []);

  const loadStorageAccounts = async () => {
    try {
      const res = await api.storage.list();
      setStorageAccounts(res.data);
    } catch {
      console.error('Failed to load storage accounts');
    }
  };

  const handleLogout = async () => {
    try {
      await api.auth.signout();
      window.location.assign('/');
    } catch {
      console.error('Logout failed');
    }
  };

  return (
    <>
      <header className="h-16 flex items-center justify-between px-4 shrink-0 bg-gray-50 relative z-30">
        <div className="flex-1 flex items-center max-w-2xl">
          <div className="w-full relative group">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-500" />
            </div>
            <input
              type="text"
              className="w-full block pl-12 pr-4 py-3 bg-[#eef2f6] border-transparent rounded-full text-gray-900 placeholder-gray-500 focus:bg-white focus:border-transparent focus:ring-0 focus:shadow-md transition-all outline-none"
              placeholder="Search in Drive"
            />
          </div>
        </div>
        
        <div className="flex items-center gap-3 ml-4 relative">
          <button className="p-2.5 rounded-full hover:bg-gray-200 transition-colors text-gray-600">
            <HelpCircle className="h-5 w-5" />
          </button>
          <button 
            className="p-2.5 rounded-full hover:bg-gray-200 transition-colors text-gray-600"
            onClick={() => {
              setIsSettingsOpen(true);
              loadStorageAccounts();
            }}
            title="Storage Settings"
          >
            <Settings className="h-5 w-5" />
          </button>
          <button className="p-2.5 rounded-full hover:bg-gray-200 transition-colors text-gray-600">
            <LayoutGrid className="h-5 w-5" />
          </button>
          
          <div 
            className="ml-2 w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center text-white font-medium cursor-pointer ring-2 ring-transparent hover:ring-gray-300 transition-all select-none"
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
          >
            {user?.first_name?.[0]?.toUpperCase() || 'U'}
          </div>

          {/* User Dropdown */}
          {isDropdownOpen && (
            <div className="absolute top-12 right-0 w-64 bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden py-2 animate-in fade-in slide-in-from-top-2 duration-200">
              {user ? (
                <div className="px-4 py-3 border-b border-gray-100">
                  <p className="text-sm font-medium text-gray-900 truncate">{user.first_name} {user.last_name}</p>
                  <p className="text-xs text-gray-500 truncate mt-0.5">{user.email}</p>
                </div>
              ) : (
                <div className="px-4 py-3 border-b border-gray-100">
                  <p className="text-sm font-medium text-gray-900">Not signed in</p>
                </div>
              )}
              <button 
                onClick={handleLogout}
                className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center gap-2 transition-colors mt-1"
              >
                <LogOut className="w-4 h-4" />
                Sign out
              </button>
            </div>
          )}
        </div>
      </header>

      {/* Storage Settings Modal */}
      {isSettingsOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm transition-all duration-300">
          <div className="relative w-full max-w-2xl bg-white rounded-3xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200 flex flex-col max-h-[85vh]">
            <div className="flex items-center justify-between p-6 border-b border-gray-100">
              <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
                <HardDrive className="w-6 h-6 text-blue-600" />
                Storage Accounts
              </h2>
              <button 
                onClick={() => setIsSettingsOpen(false)}
                className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="p-6 overflow-y-auto flex-1">
              <p className="text-sm text-gray-500 mb-6">
                Connect your Google Drive accounts here. Your files will be intelligently striped and pooled across all connected accounts, giving you unlimited total storage.
              </p>

              <div className="space-y-4 mb-8">
                {storageAccounts.length === 0 ? (
                  <div className="text-center py-8 bg-gray-50 rounded-2xl border border-dashed border-gray-200">
                    <p className="text-gray-500 text-sm">No storage accounts connected yet.</p>
                  </div>
                ) : (
                  storageAccounts.map((account) => (
                    <div key={account.id} className="flex flex-col sm:flex-row items-start sm:items-center justify-between p-4 bg-white border border-gray-200 rounded-2xl shadow-sm hover:border-gray-300 transition-colors gap-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center shrink-0">
                          <HardDrive className="w-5 h-5" />
                        </div>
                        <div className="min-w-0">
                          <p className="font-medium text-gray-900 truncate">{account.provider_account_email}</p>
                          <p className="text-xs text-gray-500 mt-0.5">
                            Google Drive • {((account.available_bytes || 0) / 1e9).toFixed(2)} GB free
                          </p>
                        </div>
                      </div>
                      <div className="w-full sm:w-auto shrink-0 flex items-center gap-4">
                        <div className="flex-1 sm:w-32 h-2 bg-gray-100 rounded-full overflow-hidden hidden sm:block">
                          <div 
                            className="h-full bg-blue-500 rounded-full" 
                            style={{ width: `${Math.min(100, ((account.used_bytes || 0) / Math.max(1, (account.total_bytes || 1))) * 100)}%` }}
                          />
                        </div>
                        <button 
                          onClick={async () => {
                            setAccountToDisconnect(account);
                            setDisconnectPreview(null);
                            try {
                              const res = await api.storage.getDisconnectPreview(account.id);
                              setDisconnectPreview(res.data);
                            } catch (e) {
                              console.error('Failed to load disconnect preview', e);
                            }
                          }}
                          className="px-3 py-1.5 text-xs font-medium text-red-600 hover:bg-red-50 rounded-lg transition-colors border border-transparent hover:border-red-100"
                        >
                          Disconnect
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>

              <div className="flex justify-center">
                <a
                  href={process.env.NEXT_PUBLIC_API_URL ? `${process.env.NEXT_PUBLIC_API_URL}/storage-accounts/connect/google` : 'http://localhost:8000/api/storage-accounts/connect/google'}
                  className="flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-full font-medium hover:bg-blue-700 transition-colors shadow-sm"
                >
                  <Plus className="w-5 h-5" />
                  Connect Google Drive
                </a>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Disconnect Modal */}
      {accountToDisconnect && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in-95 duration-200">
            <div className="p-6">
              <div className="flex items-center gap-3 text-red-600 mb-4">
                <AlertTriangle className="w-6 h-6" />
                <h2 className="text-xl font-semibold text-gray-900">Disconnect Account</h2>
              </div>
              <p className="text-gray-600 mb-2">
                You are about to disconnect <span className="font-medium text-gray-900">{accountToDisconnect.provider_account_email}</span>.
              </p>
              {disconnectPreview ? (
                <div className="bg-orange-50 border border-orange-100 rounded-lg p-3 mb-6">
                  <p className="text-sm text-gray-700">
                    This action will affect <strong>{disconnectPreview.affected_files_count} files</strong> ({((disconnectPreview.total_bytes_to_move || 0) / 1e9).toFixed(2)} GB) currently stored on this drive.
                  </p>
                </div>
              ) : (
                <p className="text-sm text-gray-500 mb-6">
                  Loading impact analysis...
                </p>
              )}
              
              <div className="space-y-3 mb-6">
                <button
                  disabled={!disconnectPreview || !disconnectPreview.can_migrate}
                  onClick={async () => {
                    try {
                      await api.storage.disconnect(accountToDisconnect.id, 'migrate');
                      toast.success('Migration queued for disconnected account.');
                      setAccountToDisconnect(null);
                      loadStorageAccounts();
                    } catch (error: any) {
                      toast.error(error.response?.data?.detail || 'Failed to migrate and disconnect');
                    }
                  }}
                  className={`w-full text-left px-4 py-3 rounded-xl border transition-colors ${
                    !disconnectPreview || !disconnectPreview.can_migrate
                      ? 'border-gray-200 bg-gray-50 opacity-50 cursor-not-allowed'
                      : 'border-blue-200 hover:border-blue-300 hover:bg-blue-50'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <p className={`font-medium ${!disconnectPreview || !disconnectPreview.can_migrate ? 'text-gray-500' : 'text-blue-900'}`}>Migrate and Disconnect</p>
                    {disconnectPreview?.can_migrate && (
                      <span className="bg-blue-100 text-blue-700 text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider">
                        Recommended
                      </span>
                    )}
                  </div>
                  <p className={`text-xs mt-1 ${!disconnectPreview || !disconnectPreview.can_migrate ? 'text-gray-400' : 'text-blue-700'}`}>
                    {!disconnectPreview 
                      ? 'Loading...' 
                      : !disconnectPreview.can_migrate 
                        ? 'Not enough space in other accounts to migrate.' 
                        : 'Move files to other connected accounts before disconnecting.'}
                  </p>
                </button>
                
                <button
                  onClick={async () => {
                    try {
                      await api.storage.disconnect(accountToDisconnect.id, 'delete');
                      toast.success('Account disconnected and files cleared.');
                      setAccountToDisconnect(null);
                      loadStorageAccounts();
                    } catch (error) {
                      toast.error('Failed to disconnect');
                    }
                  }}
                  className="w-full text-left px-4 py-3 rounded-xl border border-red-200 hover:border-red-300 hover:bg-red-50 transition-colors"
                >
                  <p className="font-medium text-red-900">Disconnect and Clear Files</p>
                  <p className="text-xs text-red-700 mt-1">Files stored exclusively on this drive will be lost.</p>
                </button>
              </div>

              <div className="flex justify-end gap-3">
                <button
                  onClick={() => setAccountToDisconnect(null)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-full transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
