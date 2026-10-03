'use client';

import React, { useState } from 'react';
import { AuthModal } from '@/components/landing/AuthModal';
import { Cloud, Shield, Zap, ArrowRight, Database } from 'lucide-react';
import Link from 'next/link';

export default function LandingPage() {
  const [isAuthModalOpen, setAuthModalOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#fafafa] font-sans selection:bg-blue-100 selection:text-blue-900">
      {/* Navbar */}
      <nav className="fixed top-0 inset-x-0 h-20 bg-white/80 backdrop-blur-md border-b border-gray-100 z-40 flex items-center justify-between px-6 md:px-12">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/30">
            <span className="text-white font-bold text-xl leading-none">E</span>
          </div>
          <span className="text-xl font-semibold text-gray-900 tracking-tight">Endless Storage</span>
        </div>
        <div className="flex items-center gap-4">
          <button 
            onClick={() => setAuthModalOpen(true)}
            className="text-gray-600 hover:text-gray-900 font-medium px-4 py-2 transition-colors"
          >
            Sign in
          </button>
          <button 
            onClick={() => setAuthModalOpen(true)}
            className="bg-gray-900 hover:bg-black text-white px-5 py-2.5 rounded-full font-medium transition-all shadow-sm"
          >
            Get Started
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="pt-32 pb-20 px-6 md:px-12 max-w-7xl mx-auto flex flex-col items-center text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-50 border border-blue-100 text-blue-700 text-sm font-medium mb-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <Zap className="w-4 h-4" />
          <span>The next generation of cloud storage</span>
        </div>
        
        <h1 className="text-5xl md:text-7xl font-bold text-gray-900 tracking-tight max-w-4xl mb-6 animate-in fade-in slide-in-from-bottom-6 duration-700">
          Combine all your drives into one <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">endless</span> cloud.
        </h1>
        
        <p className="text-lg md:text-xl text-gray-600 max-w-2xl mb-10 animate-in fade-in slide-in-from-bottom-8 duration-700 delay-100">
          Connect multiple Google Drive accounts and pool their storage together seamlessly. Upload massive folders, bypass individual drive limits, and manage it all from a single beautiful interface.
        </p>
        
        <div className="flex flex-col sm:flex-row items-center gap-4 animate-in fade-in slide-in-from-bottom-10 duration-700 delay-200">
          <button 
            onClick={() => setAuthModalOpen(true)}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-full text-lg font-medium transition-all shadow-lg shadow-blue-500/30 hover:shadow-blue-500/40 hover:-translate-y-0.5"
          >
            Start your free pool
            <ArrowRight className="w-5 h-5" />
          </button>
          <Link 
            href="/drive"
            className="flex items-center gap-2 bg-white hover:bg-gray-50 text-gray-700 border border-gray-200 px-8 py-4 rounded-full text-lg font-medium transition-all"
          >
            Go to Drive
          </Link>
        </div>

        {/* Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-32 w-full max-w-5xl">
          <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-100 flex flex-col items-center text-center">
            <div className="w-14 h-14 bg-blue-50 rounded-2xl flex items-center justify-center mb-6">
              <Database className="w-7 h-7 text-blue-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-3">Pooled Storage</h3>
            <p className="text-gray-500 leading-relaxed">
              Connect 10 free Google Drive accounts and get 150GB of unified storage space. Files are intelligently split and placed automatically.
            </p>
          </div>
          
          <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-100 flex flex-col items-center text-center">
            <div className="w-14 h-14 bg-purple-50 rounded-2xl flex items-center justify-center mb-6">
              <Cloud className="w-7 h-7 text-purple-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-3">Infinite File Sizes</h3>
            <p className="text-gray-500 leading-relaxed">
              Upload a 40GB file even if none of your individual drives have that much free space. Our placement engine handles the rest.
            </p>
          </div>
          
          <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-100 flex flex-col items-center text-center">
            <div className="w-14 h-14 bg-green-50 rounded-2xl flex items-center justify-center mb-6">
              <Shield className="w-7 h-7 text-green-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-3">Secure & Private</h3>
            <p className="text-gray-500 leading-relaxed">
              Your files never pass through our servers. Chunks are streamed directly from your browser to your connected Google Drives.
            </p>
          </div>
        </div>
      </main>

      <AuthModal isOpen={isAuthModalOpen} onClose={() => setAuthModalOpen(false)} />
    </div>
  );
}
