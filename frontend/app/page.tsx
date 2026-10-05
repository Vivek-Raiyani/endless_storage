'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { AuthModal } from '@/components/landing/AuthModal';
import { HeroSection } from '@/components/landing/HeroSection';
import { StatsBar } from '@/components/landing/StatsBar';
import { FeaturesGrid } from '@/components/landing/FeaturesGrid';
import { ComingSoonSection } from '@/components/landing/ComingSoonSection';
import { FaqSection } from '@/components/landing/FaqSection';
import { FinalCtaSection } from '@/components/landing/FinalCtaSection';
import { Footer } from '@/components/landing/Footer';
import { api } from '@/lib/api';

import { NotchNav, NotchItemData } from '@/components/ui/adaptive-notch-navigation-bar';
import { ArrowRight } from 'lucide-react';

const NAV_ITEMS: NotchItemData[] = [
  { id: "home", label: "Home" },
  { id: "features", label: "Features" },
  { id: "faq", label: "FAQ" },
];

export default function LandingPage() {
  const [isAuthModalOpen, setAuthModalOpen] = useState(false);
  const [activeTab, setActiveTab] = useState("home");
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isLoadingAuth, setIsLoadingAuth] = useState(true);
  
  const handleOpenAuth = () => setAuthModalOpen(true);

  const checkAuth = () => {
    api.auth.me()
      .then(() => setIsLoggedIn(true))
      .catch(() => setIsLoggedIn(false))
      .finally(() => setIsLoadingAuth(false));
  };

  useEffect(() => {
    checkAuth();
  }, []);

  const LogoSlot = (
    <div className="flex items-center gap-2 h-8">
      <div className="w-7 h-7 bg-white rounded-lg flex items-center justify-center shadow-lg">
        <span className="text-blue-600 font-bold text-sm leading-none">E</span>
      </div>
      <span className="hidden sm:inline text-sm font-bold tracking-tight text-white">
        Endless Storage
      </span>
    </div>
  );

  const RightContentSlot = (
    <div className="flex items-center gap-3 h-8">
      {!isLoadingAuth && (
        isLoggedIn ? (
          <Link 
            href="/drive"
            className="flex items-center gap-1.5 bg-white text-blue-900 px-4 py-1.5 rounded-full text-xs font-bold transition-transform hover:scale-105"
          >
            Dashboard <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        ) : (
          <button 
            onClick={handleOpenAuth}
            className="flex items-center gap-1.5 bg-white text-blue-900 px-4 py-1.5 rounded-full text-xs font-bold transition-transform hover:scale-105"
          >
            Sign in
          </button>
        )
      )}
    </div>
  );

  return (
    <div className="bg-white text-gray-900 font-sans selection:bg-blue-100 selection:text-blue-900">
      
      <NotchNav
        items={NAV_ITEMS}
        activeId={activeTab}
        onActiveChange={setActiveTab}
        logo={LogoSlot}
        rightContent={RightContentSlot}
        position="top"
      >
        <main className="w-full flex flex-col items-center pt-8">
          <div className="w-full max-w-7xl mx-auto flex flex-col px-6 md:px-12">
            <HeroSection onOpenAuth={handleOpenAuth} />
            <StatsBar />
            <FeaturesGrid />
            <ComingSoonSection />
            <FaqSection />
            <FinalCtaSection onOpenAuth={handleOpenAuth} />
            <Footer onOpenAuth={handleOpenAuth} />
          </div>
        </main>
      </NotchNav>

      <AuthModal 
        isOpen={isAuthModalOpen} 
        onClose={() => {
          setAuthModalOpen(false);
          checkAuth();
        }} 
      />
    </div>
  );
}
