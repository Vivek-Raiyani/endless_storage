import React from 'react';
import { Clock } from 'lucide-react';

export function ComingSoonSection() {
  return (
    <div className="mt-32 bg-gray-50 border border-gray-200 rounded-3xl p-10 md:p-16 text-gray-900 relative overflow-hidden">
      <div className="absolute top-0 right-0 p-8 opacity-40 text-gray-200">
        <Clock className="w-64 h-64" />
      </div>
      <div className="relative z-10 max-w-3xl">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white border border-gray-200 text-gray-600 text-sm font-medium mb-6">
          <Clock className="w-4 h-4" />
          <span>Coming Soon / Roadmap</span>
        </div>
        <h2 className="text-3xl md:text-5xl font-bold mb-6 text-gray-900">The journey is just beginning.</h2>
        <p className="text-xl text-gray-600 mb-12">We are constantly improving Endless Storage. Here is what we are building next to make your cloud storage even more powerful.</p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <h4 className="text-lg font-semibold mb-2 flex items-center gap-2 text-gray-900">
              <span className="w-2 h-2 bg-blue-500 rounded-full"></span> Data Mirroring (RAID 1)
            </h4>
            <p className="text-gray-600">Store file chunks on multiple drives for redundancy. If one Google account goes down, your files remain completely safe and intact.</p>
          </div>
          <div>
            <h4 className="text-lg font-semibold mb-2 flex items-center gap-2 text-gray-900">
              <span className="w-2 h-2 bg-purple-500 rounded-full"></span> Native Media Streaming
            </h4>
            <p className="text-gray-600">Stream your uploaded movies and audio directly from the UI without needing to download the entire file first.</p>
          </div>
          <div>
            <h4 className="text-lg font-semibold mb-2 flex items-center gap-2 text-gray-900">
              <span className="w-2 h-2 bg-green-500 rounded-full"></span> Public Sharing Links
            </h4>
            <p className="text-gray-600">Generate secure, temporary download links for your files to share with anyone, straight from your pooled drives.</p>
          </div>
          <div>
            <h4 className="text-lg font-semibold mb-2 flex items-center gap-2 text-gray-900">
              <span className="w-2 h-2 bg-orange-500 rounded-full"></span> Mobile Application
            </h4>
            <p className="text-gray-600">Manage your endless pool on the go with dedicated iOS and Android applications.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
