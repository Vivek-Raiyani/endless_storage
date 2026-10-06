'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { AuthModal } from '@/components/landing/AuthModal';
import { Footer } from '@/components/landing/Footer';
import { api } from '@/lib/api';
import { NotchNav, NotchItemData } from '@/components/ui/adaptive-notch-navigation-bar';
import { ArrowRight } from 'lucide-react';
import { useRouter, usePathname } from 'next/navigation';

const NAV_ITEMS: NotchItemData[] = [
  { id: "home", label: "Home" },
  { id: "features", label: "Features" },
  { id: "faq", label: "FAQ" },
];

export function LandingLayout({ children }: { children: React.ReactNode }) {
  const [isAuthModalOpen, setAuthModalOpen] = useState(false);
  const [activeTab, setActiveTab] = useState("home");
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const router = useRouter();
  const pathname = usePathname();

  // Check auth state to show correct nav button
  useEffect(() => {
    api.auth.me()
      .then(() => setIsLoggedIn(true))
      .catch(() => setIsLoggedIn(false));
  }, []);

  const handleOpenAuth = () => setAuthModalOpen(true);

  useEffect(() => {
    const handleOpenAuthEvent = () => setAuthModalOpen(true);
    window.addEventListener('open-auth-modal', handleOpenAuthEvent);
    return () => window.removeEventListener('open-auth-modal', handleOpenAuthEvent);
  }, []);

  // Sync active tab with pathname
  useEffect(() => {
    if (pathname === '/') {
      setActiveTab('home');
    } else {
      setActiveTab('');
    }
  }, [pathname]);

  const handleTabChange = (id: string) => {
    setActiveTab(id);
    // Scroll to section on the same page
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  // Logo links to /home — works for both logged-in and logged-out users
  const LogoSlot = (
    <Link href="/" className="flex items-center gap-2 h-8">
      <div className="w-7 h-7 bg-white rounded-lg flex items-center justify-center shadow-lg">
        <span className="text-blue-600 font-bold text-sm leading-none">E</span>
      </div>
      <span className="hidden sm:inline text-sm font-bold tracking-tight text-white">
        Endless Storage
      </span>
    </Link>
  );

  const RightContentSlot = (
    <div className="flex items-center gap-3 h-8">
      {isLoggedIn ? (
        <Link
          href="/drive"
          className="flex items-center gap-1.5 bg-white text-blue-900 px-4 py-1.5 rounded-full text-xs font-semibold transition-transform"
        >
          Dashboard
        </Link>
      ) : (
        <button
          onClick={handleOpenAuth}
          className="flex items-center gap-1.5 bg-white text-blue-900 px-4 py-1.5 rounded-full text-xs font-semibold transition-transform"
        >
          Sign in
        </button>
      )}
    </div>
  );

  return (
    <div className="bg-white text-gray-900 font-sans selection:bg-blue-100 selection:text-blue-900">
      <NotchNav
        items={NAV_ITEMS}
        activeId={activeTab}
        onActiveChange={handleTabChange}
        logo={LogoSlot}
        rightContent={RightContentSlot}
        position="top"
      >
        <main className="w-full flex flex-col items-center pt-8">
          {children}
          <Footer onOpenAuth={handleOpenAuth} />
        </main>
      </NotchNav>

      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setAuthModalOpen(false)}
      />
    </div>
  );
}
