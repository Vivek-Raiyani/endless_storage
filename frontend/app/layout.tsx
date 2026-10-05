import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";
import { Toaster } from 'sonner';

const ranade = localFont({
  src: [
    {
      path: './fonts/Ranade-Variable.woff2',
      style: 'normal',
    },
    {
      path: './fonts/Ranade-VariableItalic.woff2',
      style: 'italic',
    }
  ],
  variable: '--font-ranade',
});

export const metadata: Metadata = {
  title: "Endless Storage",
  description: "Unlimited cloud storage, powered by your Google accounts.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      className={`${ranade.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col font-sans" suppressHydrationWarning>
        {children}
        <Toaster position="bottom-right" richColors />
      </body>
    </html>
  );
}
