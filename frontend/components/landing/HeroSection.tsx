import React from 'react';
import { Sparkles, ArrowRight, ArrowUpRight } from 'lucide-react';
import Link from 'next/link';

export function HeroSection({ onOpenAuth }: { onOpenAuth: () => void }) {
  return (
    <div className="flex flex-col items-start max-w-4xl pt-10">
      <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-50 text-blue-700 text-sm font-semibold mb-8">
        <span className="text-base leading-none translate-y-[-1px]">✦</span>
        <span>Stop paying for cloud storage</span>
      </div>
      
      <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-4 leading-[1.1] text-gray-900">
        Your free Google storage is actually <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">unlimited.</span>
      </h1>
      
      <p className="text-md md:text-lg text-gray-600 max-w-2xl mb-6">
        Connect your Google accounts. Pool their free storage. Upload anything, no matter the size. It works like magic, and it&apos;s completely free.
      </p>
      
      <div className="flex flex-col sm:flex-row items-center gap-4 mb-8">
        <button 
          onClick={onOpenAuth}
          className="flex items-center gap-1 bg-gray-900 hover:bg-black text-white px-6 py-3 rounded-full text-md font-medium transition-all shadow-lg cursor-pointer group"
        >
          Start for free
          <ArrowRight className="w-4 h-4 -rotate-45 group-hover:rotate-0 duration-300" />
        </button>
        {/* <Link 
          href="/drive"
          className="flex items-center gap-2 bg-white hover:bg-gray-50 text-gray-700 border border-gray-200 px-8 py-4 rounded-full text-lg font-medium transition-all"
        >
          Open my drive
          <ArrowUpRight className="w-5 h-5" />
        </Link> */}
      </div>

      <div className="flex items-center gap-2 text-gray-500 text-sm font-medium">
        <span>🔒</span>
        <span>Secured with Google OAuth · No files touch our servers · Open source</span>
      </div>
    </div>
  );
}
