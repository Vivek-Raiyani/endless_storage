'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

export function HeroAnimation() {
  const [pulse, setPulse] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      setPulse((prev) => !prev);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const drives = [
    { x: 70, y: 80, delay: 0 },
    { x: 70, y: 220, delay: 0.5 },
    { x: 70, y: 360, delay: 1 },
  ];

  const paths = [
    "M100,80 C180,80 220,220 310,220",
    "M100,220 L310,220",
    "M100,360 C180,360 220,220 310,220"
  ];

  return (
    <div className="w-full max-w-[500px] mx-auto aspect-square select-none relative">
      <svg viewBox="0 0 440 440" className="w-full h-full" style={{ display: 'block', overflow: 'visible' }}>
        <defs>
          <filter id="glow">
            <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
          
          <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="4" stdDeviation="4" floodColor="rgba(0,0,0,0.1)" />
          </filter>
          
          <linearGradient id="lineGrad" x1="100" y1="0" x2="310" y2="0" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#94a3b8" stopOpacity="0.2" />
            <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.8" />
          </linearGradient>

          <linearGradient id="orbGrad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#60a5fa" />
            <stop offset="100%" stopColor="#2563eb" />
          </linearGradient>
        </defs>

        {/* Connection Lines */}
        {paths.map((d, i) => (
          <path 
            key={`bg-line-${i}`} 
            d={d} 
            fill="none" 
            stroke="url(#lineGrad)" 
            strokeWidth="3" 
            strokeLinecap="round"
          />
        ))}

        {/* Animated Particles flowing through pipelines */}
        {paths.map((d, i) => (
          <motion.circle
            key={`orb-${i}`}
            r="4"
            fill="url(#orbGrad)"
            filter="url(#glow)"
            initial={{ offsetDistance: "0%", opacity: 0 }}
            animate={{ 
              offsetDistance: ["0%", "100%"],
              opacity: [0, 1, 1, 0],
            }}
            transition={{
              duration: 2.5,
              repeat: Infinity,
              ease: "easeInOut",
              delay: drives[i].delay,
            }}
            style={{ offsetPath: `path('${d}')` }}
          />
        ))}

        {/* Source Google Drives */}
        {drives.map((d, i) => (
          <g key={`drive-${i}`} transform={`translate(${d.x}, ${d.y})`}>
            {/* 15GB Label */}
            <rect x="-24" y="-45" width="48" height="20" rx="10" fill="#f1f5f9" />
            <text x="0" y="-31" fontSize="10" fontWeight="bold" fill="#64748b" textAnchor="middle">15 GB</text>
            
            <circle cx="0" cy="0" r="28" fill="white" filter="url(#shadow)" />
            <g transform="translate(-18, -16) scale(0.42)">
              <path d="m6.6 66.85 3.85 6.65c.8 1.4 1.95 2.5 3.3 3.3l13.75-23.8h-27.5c0 1.55.4 3.1 1.2 4.5z" fill="#0066da"/>
              <path d="m43.65 25-13.75-23.8c-1.35.8-2.5 1.9-3.3 3.3l-25.4 44a9.06 9.06 0 0 0 -1.2 4.5h27.5z" fill="#00ac47"/>
              <path d="m73.55 76.8c1.35-.8 2.5-1.9 3.3-3.3l1.6-2.75 7.65-13.25c.8-1.4 1.2-2.95 1.2-4.5h-27.502l5.852 11.5z" fill="#ea4335"/>
              <path d="m43.65 25 13.75-23.8c-1.35-.8-2.9-1.2-4.5-1.2h-18.5c-1.6 0-3.15.45-4.5 1.2z" fill="#00832d"/>
              <path d="m59.8 53h-32.3l-13.75 23.8c1.35.8 2.9 1.2 4.5 1.2h50.8c1.6 0 3.15-.45 4.5-1.2z" fill="#2684fc"/>
              <path d="m73.4 26.5-12.7-22c-.8-1.4-1.95-2.5-3.3-3.3l-13.75 23.8 16.15 28h27.45c0-1.55-.4-3.1-1.2-4.5z" fill="#ffba00"/>
            </g>
          </g>
        ))}

        {/* Plus symbols between drives to show chaining */}
        <text x="70" y="155" fontSize="20" fontWeight="bold" fill="#cbd5e1" textAnchor="middle">+</text>
        <text x="70" y="295" fontSize="20" fontWeight="bold" fill="#cbd5e1" textAnchor="middle">+</text>

        {/* Endless Storage Master Drive */}
        <motion.g 
          initial={{ x: 350, y: 220 }}
          animate={{ x: 350, y: 220, scale: [1, 1.05, 1] }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
        >
          {/* Glowing Aura */}
          <motion.circle 
            cx="0" cy="0" r="45" 
            fill="rgba(59, 130, 246, 0.2)" 
            filter="url(#glow)"
            animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0.8, 0.5] }}
            transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
          />
          
          {/* The Standard App Logo */}
          <rect x="-30" y="-30" width="60" height="60" rx="16" fill="white" filter="url(#shadow)" />
          <text x="0" y="11" fontSize="32" fontWeight="800" fill="#2563eb" textAnchor="middle" style={{ fontFamily: 'sans-serif' }}>E</text>

          {/* Infinity Symbol Label */}
          <rect x="-24" y="45" width="48" height="24" rx="12" fill="#eff6ff" />
          <text x="0" y="61" fontSize="16" fontWeight="bold" fill="#2563eb" textAnchor="middle">∞</text>
        </motion.g>

      </svg>
    </div>
  );
}
