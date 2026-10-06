'use client';

import React from 'react';
import { HeroSection } from '@/components/landing/HeroSection';
import { StatsBar } from '@/components/landing/StatsBar';
import { FeaturesGrid } from '@/components/landing/FeaturesGrid';
import { UseCasesSection } from '@/components/landing/UseCasesSection';
import { RoadmapSection } from '@/components/landing/RoadmapSection';
import { FaqSection } from '@/components/landing/FaqSection';
import { FinalCtaSection } from '@/components/landing/FinalCtaSection';
import { LandingLayout } from '@/components/landing/LandingLayout';
import { api } from '@/lib/api';

export default function LandingPage() {
  const handleOpenAuth = () => {
    // This is handled by LandingLayout, but if a sub-component needs it, we can trigger it.
    // For simplicity, we can dispatch a custom event to open the auth modal if needed from inner components.
    window.dispatchEvent(new Event('open-auth-modal'));
  };

  return (
    <LandingLayout>
      <div className="w-full max-w-7xl mx-auto flex flex-col px-6 md:px-12">
        <div id="home" className="scroll-mt-32">
          <HeroSection onOpenAuth={handleOpenAuth} />
          <StatsBar />
        </div>
        <div id="features" className="scroll-mt-32">
          <FeaturesGrid />
          <UseCasesSection />
          <RoadmapSection />
        </div>
        <div id="faq" className="scroll-mt-32">
          <FaqSection />
        </div>
        <FinalCtaSection onOpenAuth={handleOpenAuth} />
      </div>
    </LandingLayout>
  );
}
