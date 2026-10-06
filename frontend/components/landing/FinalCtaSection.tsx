import { ArrowRight } from 'lucide-react';
import React from 'react';

export function FinalCtaSection({ onOpenAuth }: { onOpenAuth: () => void }) {
  return (
    <div className="mt-32 mb-10 text-center">
      <h2 className="text-4xl font-bold text-gray-900 mb-6">Ready for endless storage?</h2>
      <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto">Join thousands of users who stopped paying for cloud storage. Get started in 30 seconds.</p>
      <div className="flex items-center gap-4 mb-8">
          <button
            onClick={onOpenAuth}
            className="flex items-center mx-auto gap-1 bg-gray-900 hover:bg-black text-white px-6 py-3 rounded-full text-md font-medium transition-all shadow-lg cursor-pointer group"
          >
            Start for free
            <ArrowRight className="w-4 h-4 -rotate-45 group-hover:rotate-0 duration-300" />
          </button>
        </div>
    </div>
  );
}
