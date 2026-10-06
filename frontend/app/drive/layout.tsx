import React from 'react';
import { Sidebar } from '@/components/drive/Sidebar';
import { Header } from '@/components/drive/Header';

export default function DriveLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen bg-gray-50 text-gray-900 font-sans overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0 w-full">
        <Header />
        <main className="flex-1 overflow-auto bg-white sm:rounded-tl-2xl p-4 sm:p-6 shadow-sm border-t sm:border border-gray-200 m-0 sm:m-2 sm:mt-0 sm:ml-0">
          {children}
        </main>
      </div>
    </div>
  );
}
