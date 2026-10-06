import React from 'react';
import { LandingLayout } from '@/components/landing/LandingLayout';

export default function PrivacyPolicy() {
  return (
    <LandingLayout>
      <div className="w-full max-w-4xl mx-auto flex flex-col px-6 md:px-12 py-12 text-left items-start">
        <h1 className="text-4xl font-bold tracking-tight mb-4 text-left w-full">Privacy Policy</h1>
        <p className="text-gray-500 mb-10 w-full text-left">Last updated: {new Date().toLocaleDateString()}</p>

        <div className="text-gray-700 leading-relaxed space-y-6">
          
          <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">1. Introduction</h2>
          <p>
            Welcome to Endless Storage. We respect your privacy and are committed to protecting your personal data. 
            This Privacy Policy explains how we collect, use, and safeguard your information when you use our service.
          </p>

          <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">2. How We Access and Use Your Data (Google OAuth)</h2>
          <p>
            Endless Storage connects to your Google Drive accounts using Google OAuth. We request specific scopes to manage your files effectively across multiple drives.
          </p>
          <div className="bg-blue-50 border border-blue-100 rounded-xl p-6 my-6">
            <h3 className="text-lg font-bold text-blue-900 mb-2">Crucial Data Storage Guarantee</h3>
            <p className="text-blue-800">
              <strong>We do NOT store your files, folders, or document contents on our servers.</strong><br/>
              Our service acts purely as a client-side interface and routing mechanism. When you upload a file, it is chunked and streamed directly to your own authenticated Google Drive accounts. Your files always remain within your Google infrastructure. We only store lightweight metadata (such as file IDs, chunk maps, and your email address) in our database to reassemble the files when you request a download.
            </p>
          </div>

          <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">3. Information We Collect</h2>
          <ul className="list-disc pl-6 space-y-2">
            <li><strong>Account Information:</strong> We store your Google email address, name, and profile picture to identify your account and display it in the UI.</li>
            <li><strong>OAuth Tokens:</strong> We securely store the OAuth access and refresh tokens provided by Google to maintain your connection.</li>
            <li><strong>File Metadata:</strong> We store metadata such as file names, sizes, chunk distributions, and Google Drive File IDs to know where your data is located.</li>
          </ul>

          <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">4. Data Sharing and Disclosure</h2>
          <p>
            We do not sell, trade, or otherwise transfer your personal information or file metadata to outside parties. All your data is kept strictly confidential and is used solely to provide the Endless Storage service to you.
          </p>

          <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">5. Data Security</h2>
          <p>
            We implement a variety of security measures to maintain the safety of your personal information. Our database is secured, and all communication between your browser, our server, and Google APIs happens over encrypted HTTPS connections.
          </p>

          <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">6. Contact Us</h2>
          <p>
            If you have any questions about this Privacy Policy or need to request account deletion, please contact us.
          </p>
        </div>
      </div>
    </LandingLayout>
  );
}
