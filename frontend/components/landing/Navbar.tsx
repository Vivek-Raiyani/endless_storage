import React from 'react';

export function Navbar({ onOpenAuth }: { onOpenAuth: () => void }) {
  return (
    <nav className="fixed top-0 inset-x-0 h-20 bg-white/80 backdrop-blur-md border-b border-gray-100 z-40 flex items-center justify-between px-6 md:px-12">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/30">
          <span className="text-white font-bold text-xl leading-none">E</span>
        </div>
        <span className="text-xl font-semibold text-gray-900 tracking-tight">Endless Storage</span>
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
