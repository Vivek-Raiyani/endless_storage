import React from 'react';
import Link from 'next/link';
import { ArrowRight } from 'lucide-react';

export function Footer({ onOpenAuth }: { onOpenAuth: () => void }) {
  return (
    <footer className="w-full bg-blue-600 text-blue-50 pt-16 px-6 md:px-12 rounded-t-[1rem] relative overflow-hidden shadow-2xl">
      {/* Decorative background elements */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-blue-400/30 rounded-full blur-[100px] -z-10 pointer-events-none translate-x-1/3 -translate-y-1/3" />
      <div className="absolute bottom-[50vh] left-0 w-96 h-96 bg-indigo-900/30 rounded-full blur-[100px] -z-10 pointer-events-none -translate-x-1/3 translate-y-1/3" />
      
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between gap-12 relative z-10">
        
        {/* Left Side: Logo & Description */}
        <div className="flex flex-col gap-6 max-w-sm">
          <div className="flex items-center gap-3">
            {/* Logo */}
            <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center shadow-lg shrink-0">
              <img src="/logo.png" alt="Endless Storage Logo" className="w-7 h-7 object-contain" />
            </div>
            <span className="text-2xl font-bold text-white tracking-tight whitespace-nowrap">Endless Storage</span>
          </div>
          <p className="text-blue-100 leading-relaxed text-sm md:text-base opacity-90">
            The intelligent storage engine that pools your scattered free cloud accounts into one seamless, unlimited drive.
          </p>
         
        </div>

        {/* Right Side: Links */}
        <div className="grid grid-cols-2 gap-12 md:gap-24">
          <div className="flex flex-col gap-4">
            <h4 className="font-bold text-white mb-2">Product</h4>
            <a href="/#features" className="text-blue-100 hover:text-white transition-colors text-sm">Features</a>
            <a href="/#faq" className="text-blue-100 hover:text-white transition-colors text-sm">FAQ</a>
            <button onClick={onOpenAuth} className="text-blue-100 hover:text-white transition-colors text-sm text-left">Sign in</button>
          </div>
          <div className="flex flex-col gap-4">
            <h4 className="font-bold text-white mb-2">Legal</h4>
            <Link href="/privacy" className="text-blue-100 hover:text-white transition-colors text-sm">Privacy Policy</Link>
            <Link href="/terms" className="text-blue-100 hover:text-white transition-colors text-sm">Terms of Use</Link>
            <Link href="/cookies" className="text-blue-100 hover:text-white transition-colors text-sm">Cookie Policy</Link>
          </div>
        </div>

      </div>

      {/* Bottom Footer */}
      <div className="max-w-7xl mx-auto my-8 pt-8 border-t border-blue-400/30 flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-blue-200 relative z-10">
        <p>© {new Date().getFullYear()} Endless Storage. All rights reserved.</p>
        <p className="flex items-center gap-1.5">
          Built with precision by 
          <a href="https://trivven.com" target="_blank" rel="noopener noreferrer" className="inline-flex items-center hover:opacity-80 transition-opacity translate-y-[1px]">
            <img src="/trivven.svg" alt="Trivven" className="h-4 w-auto object-contain" />
          </a>
        </p>
      </div>
    </footer>
  );
}
