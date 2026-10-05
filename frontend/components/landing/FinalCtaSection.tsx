import React from 'react';

export function FinalCtaSection({ onOpenAuth }: { onOpenAuth: () => void }) {
  return (
    <div className="mt-32 mb-20 text-center">
      <h2 className="text-4xl font-bold text-gray-900 mb-6">Ready for endless storage?</h2>
      <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto">Join thousands of users who stopped paying for cloud storage. Get started in 30 seconds.</p>
      <button 
        onClick={onOpenAuth}
        className="bg-blue-600 hover:bg-blue-700 text-white px-10 py-4 rounded-full text-lg font-medium transition-all shadow-xl shadow-blue-500/20 hover:-translate-y-1"
      >
        Start your free pool now
      </button>
    </div>
  );
}
