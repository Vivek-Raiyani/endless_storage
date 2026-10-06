'use client';

import React from 'react';
import { motion } from 'framer-motion';

export const iconPaths = {
  database: [
    "M4 6a8 3 0 1 0 16 0a8 3 0 1 0 -16 0",
    "M4 6v6a8 3 0 0 0 16 0v-6",
    "M4 12v6a8 3 0 0 0 16 0v-6"
  ],
  infinity: [
    "M9.828 9.172a4 4 0 1 0 0 5.656a10 10 0 0 0 2.172 -2.828a10 10 0 0 1 2.172 -2.828a4 4 0 1 1 0 5.656a10 10 0 0 1 -2.172 -2.828a10 10 0 0 0 -2.172 -2.828"
  ],
  shieldCheck: [
    "M11.46 20.846a12 12 0 0 1 -7.96 -14.846a12 12 0 0 0 8.5 -3a12 12 0 0 0 8.5 3a12 12 0 0 1 -.09 7.06",
    "M15 19l2 2l4 -4"
  ],
  refresh: [
    "M20 11a8.1 8.1 0 0 0 -15.5 -2m-.5 -4v4h4",
    "M4 13a8.1 8.1 0 0 0 15.5 2m.5 4v-4h-4"
  ],
  layoutGrid: [
    "M4 5a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v4a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1l0 -4",
    "M14 5a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v4a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1l0 -4",
    "M4 15a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v4a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1l0 -4",
    "M14 15a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v4a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1l0 -4"
  ],
  bolt: [
    "M13 3l0 7l6 0l-8 11l0 -7l-6 0l8 -11"
  ],
  layoutDashboard: [
    "M5 4h4a1 1 0 0 1 1 1v6a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1v-6a1 1 0 0 1 1 -1",
    "M5 16h4a1 1 0 0 1 1 1v2a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1v-2a1 1 0 0 1 1 -1",
    "M15 12h4a1 1 0 0 1 1 1v6a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1v-6a1 1 0 0 1 1 -1",
    "M15 4h4a1 1 0 0 1 1 1v2a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1v-2a1 1 0 0 1 1 -1"
  ],
  palette: [
    "M12 21a9 9 0 0 1 0 -18c4.97 0 9 3.582 9 8c0 1.06 -.474 2.078 -1.318 2.828c-.844 .75 -1.989 1.172 -3.182 1.172h-2.5a2 2 0 0 0 -1 3.75a1.3 1.3 0 0 1 -1 2.25",
    "M7.5 10.5a1 1 0 1 0 2 0a1 1 0 1 0 -2 0",
    "M11.5 7.5a1 1 0 1 0 2 0a1 1 0 1 0 -2 0",
    "M15.5 10.5a1 1 0 1 0 2 0a1 1 0 1 0 -2 0"
  ],
  cloud: [
    "M6.657 18c-2.572 0 -4.657 -2.007 -4.657 -4.483c0 -2.475 2.085 -4.482 4.657 -4.482c.393 -1.762 1.794 -3.2 3.675 -3.773c1.88 -.572 3.956 -.193 5.444 1c1.488 1.19 2.162 3.007 1.77 4.769h.99c1.913 0 3.464 1.56 3.464 3.486c0 1.927 -1.551 3.487 -3.465 3.487h-11.878"
  ],
  share: [
    "M3 12a3 3 0 1 0 6 0a3 3 0 1 0 -6 0",
    "M15 6a3 3 0 1 0 6 0a3 3 0 1 0 -6 0",
    "M15 18a3 3 0 1 0 6 0a3 3 0 1 0 -6 0",
    "M8.7 10.7l6.6 -3.4",
    "M8.7 13.3l6.6 3.4"
  ]
};

export function AnimatedIcon({ name, className }: { name: keyof typeof iconPaths, className?: string }) {
  const paths = iconPaths[name];
  
  const pathVariants = {
    rest: { pathLength: 1, opacity: 1 },
    hover: { 
      pathLength: [0, 1],
      transition: { 
        duration: 0.8, 
        ease: "circOut"
      }
    }
  };

  return (
    <svg 
      xmlns="http://www.w3.org/2000/svg" 
      viewBox="0 0 24 24" 
      fill="none" 
      stroke="currentColor" 
      strokeWidth="1.5" 
      strokeLinecap="round" 
      strokeLinejoin="round" 
      className={className}
    >
      {paths.map((p, i) => (
        <motion.path 
          key={i} 
          d={p} 
          variants={pathVariants}
        />
      ))}
    </svg>
  );
}
