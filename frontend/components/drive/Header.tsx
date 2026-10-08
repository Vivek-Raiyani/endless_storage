'use client';
import React, { useEffect, useState } from 'react';
import { Search, HelpCircle, Settings, LayoutGrid, LogOut, HardDrive, Plus, X, AlertTriangle, Menu, Unplug } from 'lucide-react';
import { api } from '@/lib/api';
import { useRouter, useSearchParams } from 'next/navigation';
import { toast } from 'sonner';
import { GoogleDriveLogo } from '@/components/landing/StackedProviders';

export function Header() {
  const [user, setUser] = useState<{ email: string; first_name: string; last_name: string } | null>(null);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [storageAccounts, setStorageAccounts] = useState<Array<{ id: string; provider_account_email: string; total_bytes: number; used_bytes: number; available_bytes: number }>>([]);
  const [accountToDisconnect, setAccountToDisconnect] = useState<any>(null);
  const [disconnectPreview, setDisconnectPreview] = useState<{ can_migrate: boolean; affected_files_count: number; total_bytes_to_move: number; available_bytes_elsewhere: number } | null>(null);
  const [isHelpModalOpen, setIsHelpModalOpen] = useState(false);
  const router = useRouter();
  const searchParams = useSearchParams();
  const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || '');
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    if (!isTyping) {
      setSearchQuery(searchParams.get('q') || '');
    }
  }, [searchParams, isTyping]);

  useEffect(() => {
    const handler = setTimeout(() => {
      if (isTyping) {
        if (searchQuery.trim()) {
          router.push(`/drive/search?q=${encodeURIComponent(searchQuery.trim())}`);
        } else if (searchParams.get('q') !== null) {
          router.push('/drive');
        }
        setIsTyping(false);
      }
    }, 400);
    return () => clearTimeout(handler);
  }, [searchQuery, isTyping, router, searchParams]);

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
    
    const handleGlobalClick = () => setIsDropdownOpen(false);
    
    window.addEventListener('openStorageSettings', handleOpenStorageSettings);
    window.addEventListener('click', handleGlobalClick);
    
    return () => {
      window.removeEventListener('openStorageSettings', handleOpenStorageSettings);
      window.removeEventListener('click', handleGlobalClick);
    };
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
      <header className="h-16 flex items-center justify-between px-2 sm:px-4 shrink-0 bg-gray-50 relative z-30">
        <div className="flex-1 flex items-center gap-2 sm:gap-4 max-w-2xl">
          <button 
            className="md:hidden p-2 rounded-full hover:bg-gray-200 transition-colors text-gray-600 shrink-0"
            onClick={() => window.dispatchEvent(new Event('toggleMobileSidebar'))}
            title="Menu"
          >
            <Menu className="h-6 w-6" />
          </button>
          
          <form 
            className="w-full relative group hidden sm:block"
            onSubmit={(e) => {
              e.preventDefault();
              if (searchQuery.trim()) {
                router.push(`/drive/search?q=${encodeURIComponent(searchQuery.trim())}`);
              } else {
                router.push('/drive');
              }
            }}
          >
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-500" />
            </div>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => { setIsTyping(true); setSearchQuery(e.target.value); }}
              className="w-full block pl-12 pr-4 py-3 bg-[#eef2f6] border-transparent rounded-full text-gray-900 placeholder-gray-500 focus:bg-white focus:border-transparent focus:ring-0 focus:shadow-md transition-all outline-none"
              placeholder="Search in Drive"
            />
          </form>
        </div>
        
        <div className="flex items-center  relative">
          <button 
            className="md:hidden flex items-center gap-1 p-1.5 px-3 rounded-full hover:bg-blue-100 transition-colors text-blue-700 bg-blue-50"
            onClick={() => setIsSettingsOpen(true)}
            title="Connect Drive"
          >
            <Plus className="w-4 h-4 shrink-0" />
            <GoogleDriveLogo className="w-5 h-5 shrink-0" />
          </button>
          <button 
            className="p-2.5 rounded-full hover:bg-gray-200 transition-colors text-gray-600"
            onClick={() => setIsHelpModalOpen(true)}
            title="Help & How it works"
          >
            <HelpCircle className="h-5 w-5" />
          </button>
          
          <div 
            className="ml-2 w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center text-white font-medium cursor-pointer ring-2 ring-transparent hover:ring-gray-300 transition-all select-none"
            onClick={(e) => {
              e.stopPropagation();
              setIsDropdownOpen(!isDropdownOpen);
            }}
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
                className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2 transition-colors sm:hidden"
                onClick={() => {
                  window.dispatchEvent(new Event('openStorageSettings'));
                  setIsDropdownOpen(false);
                }}
              >
                <Settings className="w-4 h-4" />
                Storage Settings
              </button>
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

      {/* Help Modal */}
      {isHelpModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-xl overflow-hidden animate-in fade-in zoom-in-95 duration-200 flex flex-col max-h-[85vh]">
            <div className="flex items-center justify-between p-4 sm:p-5 border-b border-gray-100 shrink-0">
              <div className="flex items-center gap-2 sm:gap-3">
                <div className="w-8 h-8 bg-blue-100 text-blue-600 rounded-lg flex items-center justify-center shrink-0">
                  <HelpCircle className="w-5 h-5" />
                </div>
                <h2 className="text-lg sm:text-xl font-semibold text-gray-900 leading-tight">How Endless Storage Works</h2>
              </div>
              <button onClick={() => setIsHelpModalOpen(false)} className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-colors shrink-0 ml-2">
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="p-4 sm:p-6 overflow-y-auto">
              <p className="text-sm sm:text-base text-gray-600 mb-5 sm:mb-6 leading-relaxed">
                Endless Storage combines all your connected cloud accounts into one seamless, unlimited virtual drive. Here is what happens under the hood:
              </p>
              
              <div className="space-y-4 sm:space-y-6">
                <div className="flex gap-3 sm:gap-4">
                  <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center shrink-0 font-bold text-sm">1</div>
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-1 text-sm sm:text-base">Smart File Chunking</h3>
                    <p className="text-xs sm:text-sm text-gray-600 leading-relaxed">When you upload a file, it is automatically sliced into chunks right inside your browser. These chunks are scattered across your connected Google Drive accounts to maximize space.</p>
                  </div>
                </div>

                <div className="flex gap-3 sm:gap-4">
                  <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center shrink-0 font-bold text-sm">2</div>
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-1 text-sm sm:text-base">Direct Secure Uploads</h3>
                    <p className="text-xs sm:text-sm text-gray-600 leading-relaxed">The file bytes travel directly from your browser to Google Drive's servers. Our servers never touch, intercept, or store your actual file bytes, ensuring total privacy.</p>
                  </div>
                </div>

                <div className="flex gap-3 sm:gap-4">
                  <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-red-50 text-red-600 flex items-center justify-center shrink-0">
                    <AlertTriangle className="w-4 h-4 text-red-500" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-red-700 mb-1 text-sm sm:text-base">Warning: Do Not Delete Raw Chunks</h3>
                    <p className="text-xs sm:text-sm text-red-600/90 leading-relaxed">
                      Because your files are chunked and distributed, if you open Google Drive directly and manually delete one of the raw ".chunk" files, <span className="font-bold">the entire file inside Endless Storage will become corrupted and unrecoverable</span>. Always manage and delete your files exclusively through this Endless Storage dashboard!
                    </p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="p-4 sm:p-5 border-t border-gray-100 bg-gray-50 flex justify-end shrink-0">
              <button
                onClick={() => setIsHelpModalOpen(false)}
                className="w-full sm:w-auto px-6 py-2.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-full transition-colors shadow-sm"
              >
                I understand
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Storage Settings Modal */}
      {isSettingsOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm transition-all duration-300">
          <div className="relative w-full max-w-2xl bg-white rounded-3xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200 flex flex-col max-h-[85vh]">
            <div className="flex items-center justify-between px-6 pt-4 pb-2 border-b border-gray-100">
              <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
                <GoogleDriveLogo className="w-6 h-6 shrink-0" />
                Drive Accounts
              </h2>
              <button 
                onClick={() => setIsSettingsOpen(false)}
                className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="px-6 pt-2 sm:pt-4 overflow-y-auto flex-1">
              <p className="text-xs sm:text-sm text-gray-500 mb-3">
                Connect your Google Drive accounts here. Your files will be intelligently striped and pooled across all connected accounts, giving you unlimited total storage.
              </p>

              <div className="space-y-4 mb-2">
                {storageAccounts.length === 0 ? (
                  <div className="text-center py-8 bg-gray-50 rounded-2xl border border-dashed border-gray-200">
                    <p className="text-gray-500 text-sm">No storage accounts connected yet.</p>
                  </div>
                ) : (
                  storageAccounts.map((account) => (
                    <div key={account.id} className="flex flex-row items-center justify-between p-4 bg-white border border-gray-200 rounded-2xl shadow-sm hover:border-gray-300 transition-colors gap-2 sm:gap-4">
                      <div className="flex items-center gap-3 min-w-0">
                        <div className="w-10 h-10 bg-blue-50 rounded-full flex items-center justify-center shrink-0">
                          <GoogleDriveLogo className="w-5 h-5 shrink-0" />
                        </div>
                        <div className="min-w-0">
                          <p className="font-medium text-gray-900 truncate">{account.provider_account_email}</p>
                          <p className="text-xs text-gray-500 mt-0.5">
                            Google Drive • {((account.available_bytes || 0) / 1e9).toFixed(2)} GB free
                          </p>
                        </div>
                      </div>
                      <div className="w-auto shrink-0 flex items-center gap-4 min-w-0">
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
                          className=" flex items-center justify-center text-red-600 hover:bg-red-50 rounded-lg transition-colors border border-transparent hover:border-red-100"
                          title="Disconnect Account"
                        >
                          <Unplug className="w-5 h-5 sm:hidden shrink-0" />
                          <span className="hidden sm:inline text-xs font-medium">Disconnect</span>
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
            <div className="p-4 sm:p-6 border-t border-gray-100 bg-gray-50 flex justify-center shrink-0">
              <a
                href={process.env.NEXT_PUBLIC_API_URL ? `${process.env.NEXT_PUBLIC_API_URL}/storage-accounts/connect/google` : '/api/storage-accounts/connect/google'}
                className="flex items-center gap-2 bg-white text-gray-700 border border-gray-300 px-6 py-3 rounded-full font-medium hover:bg-gray-50 hover:border-gray-400 transition-all shadow-sm"
              >
                <Plus className="w-5 h-5 shrink-0" />
                Connect More Drive
              </a>
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
