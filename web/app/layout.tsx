import type { Metadata } from "next";
import "leaflet/dist/leaflet.css";
import "./globals.css";
import "@/styles/tokens.css";
import { AppProvider } from "@/lib/state";
import { SiteFooter, SiteHeader } from "@/components/SiteHeader";
import { InteractiveBackground } from "@/components/InteractiveBackground";
import { MockBanner } from "@/components/MockBanner";

export const metadata: Metadata = {
  title: "Field Shift",
  description: "Compare crop rotations for three Finney County, Kansas fields with NASA Earth observations, soil data and your own priorities.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
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
