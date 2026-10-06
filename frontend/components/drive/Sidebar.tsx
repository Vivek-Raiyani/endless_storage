'use client';
import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { HardDrive, Users, Clock, Trash2, Plus, Settings } from 'lucide-react';
import { api } from '@/lib/api';
import { GoogleDriveLogo } from '../landing/StackedProviders';

export function Sidebar() {
  const pathname = usePathname();
  const [summary, setSummary] = useState<{ total_bytes: number; used_bytes: number } | null>(null);
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  useEffect(() => {
    const handleToggle = () => setIsMobileOpen(prev => !prev);
    const handleClose = () => setIsMobileOpen(false);
    window.addEventListener('toggleMobileSidebar', handleToggle);
    // Close sidebar when navigating on mobile
    window.addEventListener('closeMobileSidebar', handleClose);
    return () => {
      window.removeEventListener('toggleMobileSidebar', handleToggle);
      window.removeEventListener('closeMobileSidebar', handleClose);
    };
  }, []);

  useEffect(() => {
    // Close mobile sidebar when route changes
    setIsMobileOpen(false);
  }, [pathname]);

  useEffect(() => {
    async function loadSummary() {
      try {
        const res = await api.storage.getSummary();
        setSummary(res.data);
      } catch (error) {
        if (error instanceof Error && (error.message.includes('Not authenticated') || error.message.includes('Unauthorized') || error.message.includes('Could not validate credentials'))) {
          try { await api.auth.signout(); } catch (e) { }
          window.location.assign('/');
        } else {
          console.error('Failed to load storage summary', error);
        }
      }
    }
    loadSummary();

    // Periodically refresh summary
    const interval = setInterval(loadSummary, 30000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { name: 'My Drive', icon: HardDrive, href: '/drive' },
    { name: 'Shared with me', icon: Users, href: '/drive/shared' },
    { name: 'Recent', icon: Clock, href: '/drive/recent' },
    { name: 'Trash', icon: Trash2, href: '/drive/trash' },
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {isMobileOpen && (
        <div 
          className="md:hidden fixed inset-0 bg-black/50 z-[60]" 
          onClick={() => setIsMobileOpen(false)}
        />
      )}

      {/* Sidebar Container */}
      <div className={`
        fixed inset-y-0 left-0 z-[70] md:z-0 w-64 bg-gray-50 flex flex-col pt-2 px-3 shrink-0 
        md:relative md:translate-x-0 transition-none
        ${isMobileOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
      <Link href="/" className="flex items-center gap-1 mb-2 hover:opacity-80 transition-opacity">
        <img src="/logo.png" alt="Endless Storage Logo" className="w-12 h-12 shrink-0 object-contain drop-shadow-sm" />
        <span className="text-[1.2rem] font-semibold text-gray-800 whitespace-nowrap tracking-tight">Endless Storage</span>
      </Link>

      <div className="relative group/new-btn mb-6">
        <button className="flex items-center gap-3 bg-white border border-gray-200 shadow-sm rounded-2xl py-3 px-4 w-full hover:bg-gray-50 transition-colors">
          <Plus className="w-6 h-6 text-gray-700" />
          <span className="text-sm font-medium text-gray-700">New</span>
        </button>
        {/* Dropdown menu */}
        <div className="absolute top-full left-0 mt-1 w-full bg-white border border-gray-100 rounded-xl shadow-lg opacity-0 invisible group-hover/new-btn:opacity-100 group-hover/new-btn:visible transition-all z-50 py-1">
          <button
            className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-3"
            onClick={() => window.dispatchEvent(new Event('openNewFolderModal'))}
          >
            <Plus className="w-4 h-4" /> New Folder
          </button>
          <div className="h-px bg-gray-100 my-1"></div>
          <button
            className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-3"
            onClick={() => {
              const fileInput = document.getElementById('global-file-upload');
              if (fileInput) fileInput.click();
            }}
          >
            <HardDrive className="w-4 h-4" /> File Upload
          </button>
        </div>
      </div>

      <nav className="flex-1 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href || (item.href === '/drive' && pathname.startsWith('/drive/folders'));
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center gap-4 px-4 py-2.5 rounded-full text-sm font-medium transition-colors ${isActive
                  ? 'bg-blue-100 text-blue-900'
                  : 'text-gray-700 hover:bg-gray-200/50'
                }`}
            >
              <item.icon className={`w-5 h-5 ${isActive ? 'text-blue-900' : 'text-gray-500'}`} />
              {item.name}
            </Link>
          );
        })}
      </nav>

      <div className="pb-6 px-1">
        <div className="w-full bg-gray-200 h-1.5 rounded-full overflow-hidden mb-2">
          <div
            className="bg-blue-600 h-full rounded-full transition-all duration-500"
            style={{ width: summary ? `${Math.min(100, (summary.used_bytes / Math.max(1, summary.total_bytes)) * 100)}%` : '0%' }}
          ></div>
        </div>
        <p className="text-xs text-gray-600 mb-4 px-2">
          {summary ? (
            `${(summary.used_bytes / 1e9).toFixed(2)} GB of ${(summary.total_bytes / 1e9).toFixed(2)} GB used`
          ) : (
            'Loading storage...'
          )}
        </p>
        <button
          onClick={() => {
            window.dispatchEvent(new Event('openStorageSettings'));
            window.dispatchEvent(new Event('closeMobileSidebar'));
          }}
          className="w-full flex items-center justify-center gap-2 py-3 rounded-full text-md font-medium text-white bg-blue-600 hover:bg-blue-700 transition-colors shadow-sm"
        >
          <GoogleDriveLogo className="w-8 h-8 shrink-0" />
          Connect Drives
        </button>
      </div>
    </div>
    </>
  );
}
