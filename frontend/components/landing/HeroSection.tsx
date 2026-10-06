import React from 'react';
import { ArrowRight } from 'lucide-react';
import { HeroAnimation } from './HeroAnimation';

export function HeroSection({ onOpenAuth }: { onOpenAuth: () => void }) {
  return (
    <div className="flex flex-col lg:flex-row items-center gap-10 lg:gap-8 pb-4 min-h-[70vh]">

      {/* ── Left: Copy (50%) ── */}
      <div className="flex flex-col items-start w-full lg:w-1/2">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-50 text-blue-500 text-sm font-semibold mb-8">
          <span className="text-base leading-none translate-y-[-1px]">✦</span>
          <span>Stop paying for cloud storage</span>
        </div>

        <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-4 leading-[1.1] text-gray-900">
          Your free Google storage is actually{' '}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-blue-700">
            unlimited.
          </span>
        </h1>

        <p className="text-md md:text-lg text-gray-600 max-w-lg mb-6 leading-relaxed">
          Connect your Google accounts. Pool their free storage. Upload anything, no matter the size. It works like magic, and it&apos;s completely free.
        </p>

        <div className="flex items-center gap-4 mb-8">
          <button
            onClick={onOpenAuth}
            className="flex items-center gap-1 bg-gray-900 hover:bg-black text-white px-6 py-3 rounded-full text-md font-medium transition-all shadow-lg cursor-pointer group"
          >
            Start for free
            <ArrowRight className="w-4 h-4 -rotate-45 group-hover:rotate-0 duration-300" />
          </button>
        </div>

        <div className="flex items-center gap-2 text-gray-500 text-sm font-medium">
          <span>🔒</span>
          <span>Secured with Google OAuth · No files touch our servers</span>
        </div>
      </div>

      {/* ── Right: Animation (50%) ── */}
      <div className="w-full lg:w-1/2">
        <HeroAnimation />
      </div>

    </div>
  );
}
