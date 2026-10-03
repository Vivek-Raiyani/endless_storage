import React from 'react';
import { Sidebar } from '@/components/drive/Sidebar';
import { Header } from '@/components/drive/Header';

export default function DriveLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen bg-gray-50 text-gray-900 font-sans overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Header />
        <main className="flex-1 overflow-auto bg-white rounded-tl-2xl p-6 shadow-sm border border-gray-200 m-2 mt-0 ml-0">
          {children}
        </main>
      </div>
    </div>
  );
}
