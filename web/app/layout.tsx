import type { Metadata } from "next";
import "leaflet/dist/leaflet.css";
import "./globals.css";
import "@/styles/tokens.css";
import { AppProvider } from "@/lib/state";
import { SiteFooter, SiteHeader } from "@/components/SiteHeader";
import { InteractiveBackground } from "@/components/InteractiveBackground";
import { MockBanner } from "@/components/MockBanner";

export const metadata: Metadata = {
  title: "Stubble",
  description: "Compare crop rotations for three Finney County, Kansas fields with NASA Earth observations, soil data and your own priorities.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        {/* eslint-disable-next-line @next/next/no-page-custom-font */}
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=IBM+Plex+Mono:wght@400;500&family=Source+Sans+3:wght@400;600;700&display=swap" />
        <script
          dangerouslySetInnerHTML={{
            __html: `(function(){try{var m=window.location.search.match(/[?&]theme=(dark|light)/);var t=m?m[1]:(localStorage.getItem('fieldshift_theme')||(window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'));document.documentElement.setAttribute('data-theme',t);if(t==='dark')document.documentElement.classList.add('dark');}catch(e){}})();`,
          }}
        />
      </head>
      <body>
        <AppProvider>
          <InteractiveBackground />
          <SiteHeader />
          <MockBanner />
          <main>{children}</main>
          <SiteFooter />
        </AppProvider>
      </body>
    </html>
  );
}
