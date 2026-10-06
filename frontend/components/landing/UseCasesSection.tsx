import React from 'react';
import { motion } from 'framer-motion';
import { Users } from 'lucide-react';
import { AnimatedIcon } from './AnimatedTablerIcon';

const noiseSvg = `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`;

export function UseCasesSection() {
  return (
    <div className="w-full mt-16 md:mt-32 relative">
      
      {/* Ambient background for glass effect */}
      <div className="absolute top-0 right-10 w-96 h-96 bg-gray-200/50 rounded-full blur-[100px] -z-10 pointer-events-none" />
      <div className="absolute bottom-0 left-10 w-96 h-96 bg-blue-100/50 rounded-full blur-[100px] -z-10 pointer-events-none" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-purple-100/30 rounded-full blur-[100px] -z-10 pointer-events-none" />

      {/* Section Header */}
      <div className="flex flex-col mb-4 md:mb-10">
        <h2 className="text-2xl md:text-4xl font-bold text-gray-900 mb-3 md:mb-4">One single interface for all your files.</h2>
        <p className="text-base md:text-lg text-gray-600 mb-8 md:mb-12 max-w-2xl">Stop switching between tabs and accounts. Endless Storage gives you a unified view of your entire scattered digital life.</p>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full">
        
        {/* Card 1: Unified Dashboard */}
        <motion.div className="relative bg-gradient-to-br from-gray-50/90 to-gray-50/30 p-6 md:p-8 rounded-3xl border border-white/80 shadow-[0_4px_24px_rgba(0,0,0,0.02)] hover:shadow-[0_8px_32px_rgba(0,0,0,0.05)] backdrop-blur-xl transition-all cursor-default group overflow-hidden" whileHover="hover" initial="rest" animate="rest">
          <div className="absolute inset-0 z-0 pointer-events-none opacity-[0.08] mix-blend-multiply" style={{ backgroundImage: noiseSvg }} />
          <div className="relative z-10 flex flex-col h-full">
            <AnimatedIcon name="layoutDashboard" className="w-10 h-10 text-gray-900 mb-6" />
            <div>
              <h3 className="text-xl font-bold text-gray-900 mb-2 md:mb-3">A Unified Dashboard</h3>
              <p className="text-gray-600 leading-relaxed text-sm md:text-base">
                Manage everything in one place. Upload a 50GB file, and we seamlessly split and route the chunks across your connected drives automatically. You only see the final, single file.
              </p>
            </div>
          </div>
        </motion.div>

        {/* Card 2: Digital Creators */}
        <motion.div className="relative bg-gradient-to-br from-blue-50/90 to-blue-50/30 p-6 md:p-8 rounded-3xl border border-white/80 shadow-[0_4px_24px_rgba(0,0,0,0.02)] hover:shadow-[0_8px_32px_rgba(59,130,246,0.1)] backdrop-blur-xl transition-all cursor-default group overflow-hidden" whileHover="hover" initial="rest" animate="rest">
          <div className="absolute inset-0 z-0 pointer-events-none opacity-[0.08] mix-blend-multiply" style={{ backgroundImage: noiseSvg }} />
          <div className="relative z-10 flex flex-col h-full">
            <AnimatedIcon name="palette" className="w-10 h-10 text-blue-600 mb-6" />
            <div>
              <h3 className="text-xl font-bold text-gray-900 mb-2 md:mb-3">For Digital Creators</h3>
              <p className="text-gray-600 leading-relaxed text-sm md:text-base">
                Pool your client accounts, personal accounts, and workspace accounts into one massive drive to store heavy video and design project files.
              </p>
            </div>
          </div>
        </motion.div>

        {/* Card 3: Data Hoarders */}
        <motion.div className="relative bg-gradient-to-br from-purple-50/90 to-purple-50/30 p-6 md:p-8 rounded-3xl border border-white/80 shadow-[0_4px_24px_rgba(0,0,0,0.02)] hover:shadow-[0_8px_32px_rgba(168,85,247,0.1)] backdrop-blur-xl transition-all cursor-default group overflow-hidden" whileHover="hover" initial="rest" animate="rest">
          <div className="absolute inset-0 z-0 pointer-events-none opacity-[0.08] mix-blend-multiply" style={{ backgroundImage: noiseSvg }} />
          <div className="relative z-10 flex flex-col h-full">
            <AnimatedIcon name="database" className="w-10 h-10 text-purple-600 mb-6" />
            <div>
              <h3 className="text-xl font-bold text-gray-900 mb-2 md:mb-3">For Data Hoarders</h3>
              <p className="text-gray-600 leading-relaxed text-sm md:text-base">
                Stop paying monthly subscriptions just to archive your backups. Connect multiple free Google accounts and scale capacity infinitely.
              </p>
            </div>
          </div>
        </motion.div>

      </div>
    </div>
  );
}
