'use client';

import React from 'react';
import { motion } from 'framer-motion';

import { AnimatedIcon } from './AnimatedTablerIcon';

const noiseSvg = `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`;

export function FeaturesGrid() {
  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
  };

  return (
    <div className="mt-16 md:mt-32 w-full relative">
      {/* Ambient background for glass effect */}
      <div className="absolute top-0 left-10 w-96 h-96 bg-blue-100/50 rounded-full blur-[100px] -z-10 pointer-events-none" />
      <div className="absolute bottom-0 right-10 w-96 h-96 bg-purple-100/50 rounded-full blur-[100px] -z-10 pointer-events-none" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-pink-100/30 rounded-full blur-[100px] -z-10 pointer-events-none" />

      <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-3 md:mb-4">Built different. Built better.</h2>
      <p className="text-base md:text-lg text-gray-600 mb-8 md:mb-12 max-w-2xl">Under the hood it's sophisticated. For you, it's completely effortless.</p>
      
      <motion.div 
        className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8 w-full"
        variants={containerVariants}
        initial="hidden"
        whileInView="show"
        viewport={{ once: true, margin: "-100px" }}
      >
        
        {/* Pooled Storage */}
        <motion.div variants={itemVariants} className="relative bg-gradient-to-br from-blue-50/90 to-blue-50/30 p-6 md:p-8 rounded-3xl border border-white/80 shadow-[0_4px_24px_rgba(0,0,0,0.02)] hover:shadow-[0_8px_32px_rgba(59,130,246,0.1)] backdrop-blur-xl transition-all cursor-default group overflow-hidden" whileHover="hover" initial="rest" animate="rest">
          <div className="absolute inset-0 z-0 pointer-events-none opacity-[0.08] mix-blend-multiply" style={{ backgroundImage: noiseSvg }} />
          <div className="relative z-10 flex flex-col h-full">
            <AnimatedIcon name="database" className="w-10 h-10 text-blue-600 mb-6" />
            <h3 className="text-xl font-bold text-gray-900 mb-3">Pooled Storage Engine</h3>
            <p className="text-gray-600 leading-relaxed text-sm">
              Connect as many Google accounts as you want. Every account's free 15GB is combined into one seamless pool.
            </p>
          </div>
        </motion.div>
        
        {/* Infinite Sizes */}
        <motion.div variants={itemVariants} className="relative bg-gradient-to-br from-purple-50/90 to-purple-50/30 p-6 md:p-8 rounded-3xl border border-white/80 shadow-[0_4px_24px_rgba(0,0,0,0.02)] hover:shadow-[0_8px_32px_rgba(168,85,247,0.1)] backdrop-blur-xl transition-all cursor-default group overflow-hidden" whileHover="hover" initial="rest" animate="rest">
          <div className="absolute inset-0 z-0 pointer-events-none opacity-[0.08] mix-blend-multiply" style={{ backgroundImage: noiseSvg }} />
          <div className="relative z-10 flex flex-col h-full">
            <AnimatedIcon name="infinity" className="w-10 h-10 text-purple-600 mb-6" />
            <h3 className="text-xl font-bold text-gray-900 mb-3">Infinite File Sizes</h3>
            <p className="text-gray-600 leading-relaxed text-sm">
              Upload a 40GB file even if none of your individual drives have that much free space. Our chunking algorithm handles it.
            </p>
          </div>
        </motion.div>
        
        {/* Secure */}
        <motion.div variants={itemVariants} className="relative bg-gradient-to-br from-green-50/90 to-green-50/30 p-6 md:p-8 rounded-3xl border border-white/80 shadow-[0_4px_24px_rgba(0,0,0,0.02)] hover:shadow-[0_8px_32px_rgba(34,197,94,0.1)] backdrop-blur-xl transition-all cursor-default group overflow-hidden" whileHover="hover" initial="rest" animate="rest">
          <div className="absolute inset-0 z-0 pointer-events-none opacity-[0.08] mix-blend-multiply" style={{ backgroundImage: noiseSvg }} />
          <div className="relative z-10 flex flex-col h-full">
            <AnimatedIcon name="shieldCheck" className="w-10 h-10 text-green-600 mb-6" />
            <h3 className="text-xl font-bold text-gray-900 mb-3">Secure by Design</h3>
            <p className="text-gray-600 leading-relaxed text-sm">
              Files flow directly from your browser to Google Drive. Our servers never touch your data. Tokens are encrypted at rest.
            </p>
          </div>
        </motion.div>

        {/* Auto-Recovery */}
        <motion.div variants={itemVariants} className="relative bg-gradient-to-br from-orange-50/90 to-orange-50/30 p-6 md:p-8 rounded-3xl border border-white/80 shadow-[0_4px_24px_rgba(0,0,0,0.02)] hover:shadow-[0_8px_32px_rgba(249,115,22,0.1)] backdrop-blur-xl transition-all cursor-default group overflow-hidden" whileHover="hover" initial="rest" animate="rest">
          <div className="absolute inset-0 z-0 pointer-events-none opacity-[0.08] mix-blend-multiply" style={{ backgroundImage: noiseSvg }} />
          <div className="relative z-10 flex flex-col h-full">
            <AnimatedIcon name="refresh" className="w-10 h-10 text-orange-600 mb-6" />
            <h3 className="text-xl font-bold text-gray-900 mb-3">Smart Auto-Recovery</h3>
            <p className="text-gray-600 leading-relaxed text-sm">
              Remove a connected account? Our bin-packing algorithm instantly re-plans and migrates chunks to remaining drives.
            </p>
          </div>
        </motion.div>

        {/* Familiar Interface */}
        <motion.div variants={itemVariants} className="relative bg-gradient-to-br from-pink-50/90 to-pink-50/30 p-6 md:p-8 rounded-3xl border border-white/80 shadow-[0_4px_24px_rgba(0,0,0,0.02)] hover:shadow-[0_8px_32px_rgba(236,72,153,0.1)] backdrop-blur-xl transition-all cursor-default group overflow-hidden" whileHover="hover" initial="rest" animate="rest">
          <div className="absolute inset-0 z-0 pointer-events-none opacity-[0.08] mix-blend-multiply" style={{ backgroundImage: noiseSvg }} />
          <div className="relative z-10 flex flex-col h-full">
            <AnimatedIcon name="layoutGrid" className="w-10 h-10 text-pink-600 mb-6" />
            <h3 className="text-xl font-bold text-gray-900 mb-3">Familiar Interface</h3>
            <p className="text-gray-600 leading-relaxed text-sm">
              A clean, Google Drive-like interface with folders, trash, file management, and drag-and-drop support.
            </p>
          </div>
        </motion.div>

        {/* Zero Bandwidth */}
        <motion.div variants={itemVariants} className="relative bg-gradient-to-br from-teal-50/90 to-teal-50/30 p-6 md:p-8 rounded-3xl border border-white/80 shadow-[0_4px_24px_rgba(0,0,0,0.02)] hover:shadow-[0_8px_32px_rgba(20,184,166,0.1)] backdrop-blur-xl transition-all cursor-default group overflow-hidden" whileHover="hover" initial="rest" animate="rest">
          <div className="absolute inset-0 z-0 pointer-events-none opacity-[0.08] mix-blend-multiply" style={{ backgroundImage: noiseSvg }} />
          <div className="relative z-10 flex flex-col h-full">
            <AnimatedIcon name="bolt" className="w-10 h-10 text-teal-600 mb-6" />
            <h3 className="text-xl font-bold text-gray-900 mb-3">Zero-Bandwidth Migrations</h3>
            <p className="text-gray-600 leading-relaxed text-sm">
              Files don't download to our servers during migrations. They move natively on Google's infrastructure. Fast and lossless.
            </p>
          </div>
        </motion.div>

      </motion.div>
    </div>
  );
}
