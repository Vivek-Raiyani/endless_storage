import React from 'react';

export function Footer({ onOpenAuth }: { onOpenAuth: () => void }) {
  return (
    <footer className="bg-gray-50 border-t border-gray-100 py-12 px-6 md:px-12 text-center text-gray-500 text-sm">
      <p className="mb-4">© {new Date().getFullYear()} Endless Storage. Unlimited cloud storage, powered by your Google accounts.</p>
      <div className="flex items-center justify-center gap-6">
        <a href="https://github.com/yourusername/endless_storage" className="hover:text-gray-900 transition-colors">GitHub</a>
        <button onClick={onOpenAuth} className="hover:text-gray-900 transition-colors">Sign In</button>
      </div>
    </footer>
  );
}
