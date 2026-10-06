import React from 'react';
import { LandingLayout } from '@/components/landing/LandingLayout';

export default function TermsOfUse() {
  return (
    <LandingLayout>
      <div className="w-full max-w-4xl mx-auto flex flex-col px-6 md:px-12 py-12 text-left items-start">
        <h1 className="text-4xl font-bold tracking-tight mb-4 text-left w-full">Terms of Use</h1>
        <p className="text-gray-500 mb-10 w-full text-left">Last updated: {new Date().toLocaleDateString()}</p>

        <div className="text-gray-700 leading-relaxed space-y-6">
          
          <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">1. Acceptance of Terms</h2>
          <p>
            By accessing and using Endless Storage, you accept and agree to be bound by the terms and provision of this agreement. 
            If you do not agree to abide by these terms, please do not use this service.
          </p>

          <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">2. Description of Service</h2>
          <p>
            Endless Storage provides a client-side interface that allows users to pool storage from multiple authenticated Google Drive accounts. 
            The service chunks and uploads files directly to your personal Google Drive accounts using Google's API.
          </p>

          <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">3. Google Drive Integration and Acceptable Use</h2>
          <p>
            Our service heavily relies on the Google Drive API. By using Endless Storage, you agree to comply with Google's Terms of Service and Google Drive's Acceptable Use Policy. 
            You must not use this service to store, share, or distribute any illegal, pirated, or malicious content. 
            Endless Storage is not responsible for the content you store in your Google Drive accounts.
          </p>

          <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">4. No Storage of Your Files</h2>
          <p>
            As explicitly stated in our Privacy Policy, Endless Storage <strong>does not host or store your actual files</strong>. 
            We only store lightweight metadata necessary to locate your file chunks across your Google accounts. 
            You retain full ownership, control, and responsibility for all data uploaded through our interface.
          </p>

          <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">5. Disclaimer of Warranties</h2>
          <p>
            This service is provided on an &quot;as is&quot; and &quot;as available&quot; basis. 
            Endless Storage makes no warranties, expressed or implied, and hereby disclaims all warranties, including without limitation, 
            implied warranties of merchantability, fitness for a particular purpose, or non-infringement. 
            We do not guarantee that the service will be uninterrupted, secure, or error-free.
          </p>

          <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">6. Limitation of Liability</h2>
          <p>
            In no event shall Endless Storage be liable for any data loss, account suspension by Google, or any indirect, incidental, 
            consequential, or punitive damages arising out of your use of or inability to use the service. 
            You are strongly encouraged to keep backups of your important data.
          </p>

          <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">7. Changes to Terms</h2>
          <p>
            We reserve the right to modify these terms at any time. We will notify users of any significant changes. 
            Your continued use of the service after such modifications constitutes your acknowledgment and acceptance of the updated terms.
          </p>
        </div>
      </div>
    </LandingLayout>
  );
}
