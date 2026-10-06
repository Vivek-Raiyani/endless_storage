import React from 'react';

export function StatsBar() {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-8 py-6 md:py-8 border-y border-gray-100">
      <div>
        <p className="text-gray-500 text-xs md:text-sm font-medium mb-1">Free Storage per Account</p>
        <p className="text-2xl md:text-3xl font-bold text-gray-900">15 GB</p>
      </div>
      <div>
        <p className="text-gray-500 text-xs md:text-sm font-medium mb-1">Accounts Supported</p>
        <p className="text-2xl md:text-3xl font-bold text-gray-900">Unlimited</p>
      </div>
      <div>
        <p className="text-gray-500 text-xs md:text-sm font-medium mb-1">Max Theoretical Pool</p>
        <p className="text-2xl md:text-3xl font-bold text-gray-900">∞ GB</p>
      </div>
      <div>
        <p className="text-gray-500 text-xs md:text-sm font-medium mb-1">File Size Limit</p>
        <p className="text-2xl md:text-3xl font-bold text-gray-900">None</p>
      </div>
    </div>
  );
}
