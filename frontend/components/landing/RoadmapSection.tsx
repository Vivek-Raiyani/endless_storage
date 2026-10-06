import React from 'react';
import { motion } from 'framer-motion';
import { Map } from 'lucide-react';
import { AnimatedIcon } from './AnimatedTablerIcon';
import { StackedProviders } from './StackedProviders';

const noiseSvg = `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`;

export function RoadmapSection() {
  return (
    <div className="w-full mt-16 md:mt-32 mb-16 md:mb-20 relative">
      
      {/* Ambient background for glass effect */}
      <div className="absolute top-0 left-10 w-96 h-96 bg-orange-100/40 rounded-full blur-[100px] -z-10 pointer-events-none" />
      <div className="absolute bottom-0 right-10 w-96 h-96 bg-gray-200/50 rounded-full blur-[100px] -z-10 pointer-events-none" />

      {/* Section Header */}
      <div className="flex flex-col mb-4 md:mb-10">
        <h2 className="text-2xl md:text-4xl font-bold text-gray-900 mb-3 md:mb-4">The journey is just beginning.</h2>
        <p className="text-base md:text-lg text-gray-600 mb-8 md:mb-12 max-w-2xl">We are constantly building. Here is what is coming next to make your cloud storage even more powerful.</p>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full">
        
        {/* Card 1: More Providers */}
        <motion.div className="relative bg-gradient-to-br from-orange-50/90 to-orange-50/30 p-6 md:p-8 rounded-3xl border border-white/80 shadow-[0_4px_24px_rgba(0,0,0,0.02)] hover:shadow-[0_8px_32px_rgba(249,115,22,0.1)] backdrop-blur-xl transition-all cursor-default group overflow-hidden" whileHover="hover" initial="rest" animate="rest">
          <div className="absolute inset-0 z-0 pointer-events-none opacity-[0.08] mix-blend-multiply" style={{ backgroundImage: noiseSvg }} />
          <div className="relative z-10 flex flex-col h-full justify-between">
            <AnimatedIcon name="cloud" className="w-10 h-10 text-orange-600 mb-6 md:mb-8" />
            <div>
              <h3 className="text-xl md:text-2xl font-bold text-gray-900 mb-2 md:mb-3">More Cloud Providers</h3>
              <p className="text-gray-600 leading-relaxed text-sm md:text-base max-w-md">
                We currently support Google Drive, but we are actively working on adding Microsoft OneDrive, Dropbox, and more to your unified pool in the very near future.
              </p>
              <StackedProviders />
            </div>
          </div>
        </motion.div>

        {/* Card 2: Sharing */}
        <motion.div className="relative bg-gradient-to-br from-gray-50/90 to-gray-50/30 p-6 md:p-8 rounded-3xl border border-white/80 shadow-[0_4px_24px_rgba(0,0,0,0.02)] hover:shadow-[0_8px_32px_rgba(0,0,0,0.05)] backdrop-blur-xl transition-all cursor-default group overflow-hidden" whileHover="hover" initial="rest" animate="rest">
          <div className="absolute inset-0 z-0 pointer-events-none opacity-[0.08] mix-blend-multiply" style={{ backgroundImage: noiseSvg }} />
          <div className="relative z-10 flex flex-col h-full justify-between">
            <div className="flex items-center justify-between mb-6 md:mb-8">
              <AnimatedIcon name="share" className="w-10 h-10 text-gray-700" />
              <div className="px-3 py-1.5 bg-gray-200/50 backdrop-blur-md text-gray-700 font-medium text-xs rounded-full shrink-0 border border-gray-300/50">
                In Development
              </div>
            </div>
            <div>
              <h3 className="text-xl md:text-2xl font-bold text-gray-900 mb-2 md:mb-3">Public Sharing Links</h3>
              <p className="text-gray-600 leading-relaxed text-sm md:text-base max-w-md">
                Generate secure, temporary download links for your files to share with anyone, straight from your pooled drives without requiring them to have an account.
              </p>
            </div>
          </div>
        </motion.div>

      </div>
    </div>
  );
}
