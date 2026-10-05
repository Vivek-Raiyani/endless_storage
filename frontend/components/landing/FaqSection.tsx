import React from 'react';

export function FaqSection() {
  return (
    <div className="mt-32 max-w-3xl mx-auto w-full">
      <h2 className="text-3xl font-bold text-gray-900 mb-10 text-center">Frequently asked questions</h2>
      <div className="space-y-6">
        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
          <h4 className="text-lg font-semibold text-gray-900 mb-2">Is this against Google's Terms of Service?</h4>
          <p className="text-gray-600">No. We use the official Google Drive API with standard OAuth. You're simply authorizing an application to access your own Drive accounts, just like connecting apps like Zapier or Notion.</p>
        </div>
        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
          <h4 className="text-lg font-semibold text-gray-900 mb-2">What happens if I lose access to a connected Google account?</h4>
          <p className="text-gray-600">Currently, it operates like RAID 0. If a Google account gets disabled or deleted, the chunks stored on it are lost, corrupting the associated virtual files. We recommend only using accounts you fully control. Redundancy (Mirroring) is coming soon.</p>
        </div>
        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
          <h4 className="text-lg font-semibold text-gray-900 mb-2">Are my files private?</h4>
          <p className="text-gray-600">Yes. Files never pass through our backend servers. They are uploaded directly from your browser to Google's servers. We only store the metadata (filenames and chunk maps) required to stitch them back together.</p>
        </div>
        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
          <h4 className="text-lg font-semibold text-gray-900 mb-2">What's the catch? Is it really free?</h4>
          <p className="text-gray-600">Endless Storage is entirely free and open source. It relies on the free 15GB tier provided by Google accounts. The only "cost" is taking 2 minutes to create a new Google account whenever you need another 15GB of space!</p>
        </div>
      </div>
    </div>
  );
}
