import React from 'react';

export function Navbar({ onOpenAuth }: { onOpenAuth: () => void }) {
  return (
    <nav className="fixed top-0 inset-x-0 h-20 bg-white/80 backdrop-blur-md border-b border-gray-100 z-40 flex items-center justify-between px-6 md:px-12">
      <div className="flex items-center gap-3">
        <img src="/logo.png" alt="Endless Storage Logo" className="w-12 h-12 shrink-0 object-contain drop-shadow-md" />
        <span className="text-xl font-semibold text-gray-900 tracking-tight whitespace-nowrap">Endless Storage</span>
      </div>
      <div className="flex items-center gap-4">
        <button 
          onClick={onOpenAuth}
          className="text-gray-600 hover:text-gray-900 font-medium px-4 py-2 transition-colors"
        >
          Sign in
        </button>
        <button 
          onClick={onOpenAuth}
          className="bg-gray-900 hover:bg-black text-white px-5 py-2.5 rounded-full font-medium transition-all shadow-sm"
        >
          Get Started
        </button>
      </div>
    </nav>
  );
}
