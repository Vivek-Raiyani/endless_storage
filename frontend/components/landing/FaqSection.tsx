'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, HelpCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

const faqs = [
  {
    question: "Is this against Google's Terms of Service?",
    answer: "No. We use the official Google Drive API with standard OAuth. You're simply authorizing an application to access your own Drive accounts, just like connecting apps like Zapier or Notion."
  },
  {
    question: "What happens if I lose access to a connected Google account?",
    answer: "Currently, it operates like RAID 0. If a Google account gets disabled or deleted, the chunks stored on it are lost, corrupting the associated virtual files. We recommend only using accounts you fully control. Redundancy (Mirroring) is coming soon."
  },
  {
    question: "Are my files private?",
    answer: "Yes. Files never pass through our backend servers. They are uploaded directly from your browser to Google's servers. We only store the metadata (filenames and chunk maps) required to stitch them back together."
  },
  {
    question: "What's the catch? Is it really free?",
    answer: "Endless Storage is entirely free and open source. It relies on the free 15GB tier provided by Google accounts. The only \"cost\" is taking 2 minutes to create a new Google account whenever you need another 15GB of space!"
  }
];

export function FaqSection() {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  const toggleAccordion = (index: number) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <div className="mt-16 w-full max-w-3xl mx-auto">
      
      {/* Section Header */}
      <div className="flex flex-col items-center mb-8 md:mb-12 text-center">
        <h2 className="text-2xl md:text-4xl font-bold text-gray-900 mb-4">Got questions? We've got answers.</h2>
      </div>

      {/* Accordion */}
      <div className="space-y-4 w-full">
        {faqs.map((faq, index) => {
          const isOpen = openIndex === index;
          return (
            <div 
              key={index} 
              className={cn(
                "border rounded-2xl overflow-hidden transition-all duration-200",
                isOpen ? "border-blue-200 bg-blue-50/30 shadow-sm" : "border-gray-200 bg-white hover:border-gray-300"
              )}
            >
              <button
                onClick={() => toggleAccordion(index)}
                className="flex items-center justify-between w-full p-6 text-left focus:outline-none"
              >
                <h4 className={cn("text-lg font-bold transition-colors", isOpen ? "text-blue-900" : "text-gray-900")}>
                  {faq.question}
                </h4>
                <div className={cn(
                  "w-8 h-8 rounded-full flex items-center justify-center transition-transform duration-300 shrink-0 ml-4",
                  isOpen ? "bg-blue-100 text-blue-600 rotate-180" : "bg-gray-100 text-gray-500"
                )}>
                  <ChevronDown className="w-5 h-5" />
                </div>
              </button>
              
              <AnimatePresence initial={false}>
                {isOpen && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3, ease: "easeInOut" }}
                  >
                    <div className="px-6 pb-6 pt-2 text-gray-600 leading-relaxed border-t border-blue-100/50">
                      {faq.answer}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          );
        })}
      </div>
    </div>
  );
}
