import React from 'react';
import { Database, Cloud, Lock, RefreshCcw, Grid, Shield } from 'lucide-react';

export function FeaturesGrid() {
  return (
    <div className="mt-32">
      <h2 className="text-3xl font-bold text-gray-900 mb-4">Built different. Built better.</h2>
      <p className="text-lg text-gray-600 mb-12 max-w-2xl">Under the hood it's sophisticated. For you, it's completely effortless.</p>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="bg-gray-50/50 p-8 rounded-3xl border border-gray-100">
          <div className="w-12 h-12 bg-blue-100 rounded-2xl flex items-center justify-center mb-6">
            <Database className="w-6 h-6 text-blue-600" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-3">Pooled Storage Engine</h3>
          <p className="text-gray-600 leading-relaxed">
            Connect as many Google accounts as you want. Every account's free 15GB is combined into one seamless pool.
          </p>
        </div>
        
        <div className="bg-gray-50/50 p-8 rounded-3xl border border-gray-100">
          <div className="w-12 h-12 bg-purple-100 rounded-2xl flex items-center justify-center mb-6">
            <Cloud className="w-6 h-6 text-purple-600" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-3">Infinite File Sizes</h3>
          <p className="text-gray-600 leading-relaxed">
            Upload a 40GB file even if none of your individual drives have that much free space. Our chunking algorithm handles it.
          </p>
        </div>
        
        <div className="bg-gray-50/50 p-8 rounded-3xl border border-gray-100">
          <div className="w-12 h-12 bg-green-100 rounded-2xl flex items-center justify-center mb-6">
            <Lock className="w-6 h-6 text-green-600" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-3">Secure by Design</h3>
          <p className="text-gray-600 leading-relaxed">
            Files flow directly from your browser to Google Drive. Our servers never touch your data. Tokens are encrypted at rest.
          </p>
        </div>

        <div className="bg-gray-50/50 p-8 rounded-3xl border border-gray-100">
          <div className="w-12 h-12 bg-orange-100 rounded-2xl flex items-center justify-center mb-6">
            <RefreshCcw className="w-6 h-6 text-orange-600" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-3">Smart Auto-Recovery</h3>
          <p className="text-gray-600 leading-relaxed">
            Remove a connected account? Our bin-packing algorithm instantly re-plans and migrates chunks to remaining drives.
          </p>
        </div>

        <div className="bg-gray-50/50 p-8 rounded-3xl border border-gray-100">
          <div className="w-12 h-12 bg-pink-100 rounded-2xl flex items-center justify-center mb-6">
            <Grid className="w-6 h-6 text-pink-600" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-3">Familiar Interface</h3>
          <p className="text-gray-600 leading-relaxed">
            A clean, Google Drive-like interface with folders, trash, file management, and drag-and-drop support.
          </p>
        </div>

        <div className="bg-gray-50/50 p-8 rounded-3xl border border-gray-100">
          <div className="w-12 h-12 bg-teal-100 rounded-2xl flex items-center justify-center mb-6">
            <Shield className="w-6 h-6 text-teal-600" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-3">Zero-Bandwidth Migrations</h3>
          <p className="text-gray-600 leading-relaxed">
            Files don't download to our servers during migrations. They move natively on Google's infrastructure. Fast and lossless.
          </p>
        </div>
      </div>
    </div>
  );
}
