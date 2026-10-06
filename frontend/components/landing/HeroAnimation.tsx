'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

export function HeroAnimation() {
  const [stage, setStage] = useState('incoming');

  useEffect(() => {
    let isMounted = true;
    const runSequence = async () => {
      while (isMounted) {
        setStage('incoming');
        await new Promise(r => setTimeout(r, 1200));
        if (!isMounted) break;
        
        setStage('chunking');
        await new Promise(r => setTimeout(r, 600));
        if (!isMounted) break;
        
        setStage('distributing');
        await new Promise(r => setTimeout(r, 1000));
        if (!isMounted) break;
        
        setStage('stored');
        await new Promise(r => setTimeout(r, 600));
        if (!isMounted) break;
        
        setStage('success');
        await new Promise(r => setTimeout(r, 2000));
      }
    };
    
    runSequence();
    return () => { isMounted = false; };
  }, []);

  const drives = [
    { cx: 220, cy: 50 },
    { cx: 390, cy: 220 },
    { cx: 220, cy: 390 },
    { cx: 50, cy: 220 },
  ];

  const lines = [
    "M220,175 L220,80",
    "M265,220 L360,220",
    "M220,265 L220,360",
    "M175,220 L80,220"
  ];

  const chunkTargets = [
    { x: 220, y: 50, color: '#4285F4' },
    { x: 390, y: 220, color: '#34A853' },
    { x: 220, y: 390, color: '#EA4335' },
    { x: 50, y: 220, color: '#FBBC05' },
  ];

  return (
    <div className="w-full max-w-[440px] mx-auto aspect-square select-none">
      <svg viewBox="0 0 440 440" className="w-full h-full" style={{ display: 'block', overflow: 'visible' }}>
        <defs>
          <filter id="shadowBlur">
            <feGaussianBlur stdDeviation="4" />
          </filter>
          <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="4" stdDeviation="4" floodColor="rgba(0,0,0,0.1)" />
          </filter>
          <linearGradient id="folderBack" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#fcd34d" />
            <stop offset="100%" stopColor="#fbbf24" />
          </linearGradient>
          <linearGradient id="folderTab" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#fcd34d" />
            <stop offset="100%" stopColor="#fbbf24" />
          </linearGradient>
          <linearGradient id="folderFront" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#fbbf24" />
            <stop offset="100%" stopColor="#f59e0b" />
          </linearGradient>
          <linearGradient id="file1" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#818cf8" />
            <stop offset="100%" stopColor="#6366f1" />
          </linearGradient>
          <linearGradient id="file2" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#38bdf8" />
            <stop offset="100%" stopColor="#0ea5e9" />
          </linearGradient>
          <linearGradient id="fileIncoming" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#a855f7" />
            <stop offset="100%" stopColor="#6366f1" />
          </linearGradient>
        </defs>

        {/* Lines */}
        {lines.map((d, i) => (
          <path key={`line-${i}`} d={d} fill="none" stroke="#E2E8F0" strokeWidth="2" strokeDasharray="4 4" />
        ))}

        {/* Drives */}
        {drives.map((d, i) => (
          <motion.g key={`drive-${i}`}
            animate={stage === 'stored' ? { scale: [1, 1.15, 1] } : { scale: 1 }}
            transition={{ duration: 0.4 }}
            style={{ transformOrigin: `${d.cx}px ${d.cy}px` }}
          >
            <circle cx={d.cx} cy={d.cy} r={30} fill="white" filter="url(#shadow)" />
            <g transform={`translate(${d.cx - 21}, ${d.cy - 19}) scale(0.48)`}>
              <path d="m6.6 66.85 3.85 6.65c.8 1.4 1.95 2.5 3.3 3.3l13.75-23.8h-27.5c0 1.55.4 3.1 1.2 4.5z" fill="#0066da"/>
              <path d="m43.65 25-13.75-23.8c-1.35.8-2.5 1.9-3.3 3.3l-25.4 44a9.06 9.06 0 0 0 -1.2 4.5h27.5z" fill="#00ac47"/>
              <path d="m73.55 76.8c1.35-.8 2.5-1.9 3.3-3.3l1.6-2.75 7.65-13.25c.8-1.4 1.2-2.95 1.2-4.5h-27.502l5.852 11.5z" fill="#ea4335"/>
              <path d="m43.65 25 13.75-23.8c-1.35-.8-2.9-1.2-4.5-1.2h-18.5c-1.6 0-3.15.45-4.5 1.2z" fill="#00832d"/>
              <path d="m59.8 53h-32.3l-13.75 23.8c1.35.8 2.9 1.2 4.5 1.2h50.8c1.6 0 3.15-.45 4.5-1.2z" fill="#2684fc"/>
              <path d="m73.4 26.5-12.7-22c-.8-1.4-1.95-2.5-3.3-3.3l-13.75 23.8 16.15 28h27.45c0-1.55-.4-3.1-1.2-4.5z" fill="#ffba00"/>
            </g>
          </motion.g>
        ))}

        {/* Folder Back */}
        <motion.g
          animate={stage === 'chunking' ? { scale: [1, 1.08, 1] } : { scale: 1 }}
          transition={{ duration: 0.4 }}
          style={{ transformOrigin: "220px 220px" }}
        >
          {/* Shadow */}
          <ellipse cx={220} cy={252} rx={35} ry={6} fill="rgba(245,158,11,0.35)" filter="url(#shadowBlur)" />
          
          <g transform="translate(175, 182)">
            {/* Back body */}
            <rect x={0} y={12} width={90} height={60} rx={10} fill="url(#folderBack)" />
            {/* Tab */}
            <rect x={8} y={0} width={32} height={14} rx={4} fill="url(#folderTab)" />
          </g>
        </motion.g>

        {/* Incoming File (Drops into folder) */}
        <motion.g
          initial={{ y: -20, x: 220, opacity: 0, scale: 0.8 }}
          animate={
            stage === 'incoming' 
              ? { y: 194, opacity: [0, 1, 1, 0], scale: 0.45 } 
              : { opacity: 0, y: -20, scale: 0.8 }
          }
          transition={{ duration: 1, ease: "easeIn" }}
        >
          <rect x={-24} y={-32} width={48} height={64} rx={8} fill="url(#fileIncoming)" />
          <circle cx={0} cy={0} r={10} fill="white" opacity={0.5} />
        </motion.g>

        {/* Folder Front */}
        <motion.g
          animate={stage === 'chunking' ? { scale: [1, 1.08, 1] } : { scale: 1 }}
          transition={{ duration: 0.4 }}
          style={{ transformOrigin: "220px 220px" }}
        >
          <g transform="translate(175, 182)">
            {/* Fanned Files inside folder */}
            <rect x={14} y={3} width={46} height={34} rx={6} fill="url(#file1)" transform="rotate(-10 37 20)" />
            <rect x={28} y={2} width={46} height={34} rx={6} fill="url(#file2)" transform="rotate(8 51 19)" />

            {/* Front body */}
            <rect x={0} y={16} width={90} height={56} rx={10} fill="url(#folderFront)" />
            <rect x={6} y={20} width={78} height={1} fill="rgba(255,255,255,0.4)" rx={0.5} />
          </g>
        </motion.g>

        {/* Distributed Chunks */}
        {chunkTargets.map((t, i) => (
          <motion.circle
            key={`chunk-${i}`}
            r={6}
            fill={t.color}
            initial={{ cx: 220, cy: 220, opacity: 0, scale: 0.5 }}
            animate={
              stage === 'distributing' 
                ? { cx: t.x, cy: t.y, opacity: [0, 1, 1, 0], scale: 1 }
                : { opacity: 0, cx: 220, cy: 220, scale: 0.5 }
            }
            transition={{ duration: 0.8, ease: "easeOut" }}
          />
        ))}

        {/* Success Checkmark */}
        <motion.g
          initial={{ scale: 0, opacity: 0 }}
          animate={stage === 'success' ? { scale: 1, opacity: 1 } : { scale: 0, opacity: 0 }}
          transition={{ type: 'spring', stiffness: 300, damping: 20 }}
          style={{ transformOrigin: "220px 220px" }}
        >
          <circle cx={220} cy={220} r={16} fill="#22c55e" />
          <polyline points="214,220 218,224 226,216" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
        </motion.g>
      </svg>
    </div>
  );
}
