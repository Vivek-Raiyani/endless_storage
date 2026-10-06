import React from 'react';
import { LandingLayout } from '@/components/landing/LandingLayout';

export default function CookiePolicy() {
  return (
    <LandingLayout>
      <div className="w-full max-w-4xl mx-auto flex flex-col px-6 md:px-12 py-12 text-left items-start">
        <h1 className="text-4xl font-bold tracking-tight mb-4 text-left w-full">Cookie Policy</h1>
        <p className="text-gray-500 mb-10 w-full text-left">Last updated: {new Date().toLocaleDateString()}</p>

        <div className="text-gray-700 leading-relaxed space-y-6">
          
          <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">1. What Are Cookies?</h2>
          <p>
            Cookies are small text files that are placed on your computer or mobile device when you visit a website. 
            They are widely used to make websites work, or work more efficiently, as well as to provide information to the owners of the site.
          </p>

          <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">2. How We Use Cookies</h2>
          <p>
            Endless Storage uses cookies strictly for essential operational purposes. We do <strong>not</strong> use cookies for tracking, advertising, or selling your data to third parties.
          </p>
          <ul className="list-disc pl-6 space-y-2">
            <li>
              <strong>Authentication (Essential):</strong> We use secure, HTTP-only cookies to manage your login session. When you sign in via Google OAuth, a session cookie is generated so you do not have to repeatedly log in as you navigate the app.
            </li>
            <li>
              <strong>Security (Essential):</strong> Cookies help us protect your account and data from unauthorized access, such as preventing Cross-Site Request Forgery (CSRF) attacks.
            </li>
          </ul>

          <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">3. Third-Party Cookies</h2>
          <p>
            Because we use Google OAuth for authentication, Google may set cookies on your device during the login flow. These cookies are governed by Google's own Privacy Policy and Cookie Policy. Endless Storage does not have access to read or modify these Google cookies.
          </p>

          <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">4. Managing Cookies</h2>
          <p>
            You can control and/or delete cookies as you wish. You can delete all cookies that are already on your computer and you can set most browsers to prevent them from being placed. However, if you do this, you will not be able to log into Endless Storage or use its features, as our session cookies are essential for the application to function.
          </p>

          <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">5. Contact Us</h2>
          <p>
            If you have any questions about our use of cookies, please contact us.
          </p>
        </div>
      </div>
    </LandingLayout>
  );
}
