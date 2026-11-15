"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Moon, Sprout, Sun } from "lucide-react";
import { useFieldShift } from "@/lib/state";

export function SiteHeader() {
  const pathname = usePathname();
  const { lang, setLang, theme, setTheme } = useFieldShift();
  return (
    <header className="site-header">
      <div className="site-header-inner">
        <Link className="brand" href="/" aria-label="Field Shift home">
          <span className="brand-mark"><Sprout size={19} strokeWidth={2.2} /></span>
          <span className="brand-name">field<span>shift</span></span>
        </Link>
        <div className="header-location"><span className="location-dot" /> FINNEY COUNTY, KANSAS</div>
        <nav className="header-nav" aria-label="Main navigation">
          <Link className={pathname === "/" ? "nav-link active" : "nav-link"} href="/">{lang === "es" ? "Explorar campos" : "Explore fields"}</Link>
          <Link className={pathname.startsWith("/how-we-know") ? "nav-link active" : "nav-link"} href="/how-we-know">{lang === "es" ? "Cómo lo sabemos" : "How we know"}</Link>
        </nav>
        <div className="header-controls">
          <div className="theme-toggle" role="group" aria-label="Choose color theme">
            <button
              type="button"
              className={theme === "light" ? "active" : ""}
              aria-pressed={theme === "light"}
              onClick={() => setTheme("light")}
              title={lang === "es" ? "Modo claro" : "Light mode"}
              aria-label={lang === "es" ? "Activar modo claro" : "Switch to light mode"}
            >
              <Sun size={15} strokeWidth={2.2} />
              <span className="sr-only">Light</span>
            </button>
            <button
              type="button"
              className={theme === "dark" ? "active" : ""}
              aria-pressed={theme === "dark"}
              onClick={() => setTheme("dark")}
              title={lang === "es" ? "Modo oscuro" : "Dark mode"}
              aria-label={lang === "es" ? "Activar modo oscuro" : "Switch to dark mode"}
            >
              <Moon size={15} strokeWidth={2.2} />
              <span className="sr-only">Dark</span>
            </button>
          </div>
          <div className="lang-toggle" role="group" aria-label="Choose language">
            <button type="button" aria-pressed={lang === "en"} onClick={() => setLang("en")}>EN</button>
            <button type="button" aria-pressed={lang === "es"} onClick={() => setLang("es")}>ES</button>
          </div>
        </div>
      </div>
    </header>
  );
}

export function SiteFooter() {
  const { lang } = useFieldShift();
  return (
    <footer className="site-footer">
      <p>{lang === "es"
        ? "Field Shift apoya el criterio del agricultor, no lo reemplaza. Verifique condiciones, mercados, agua y equipo con expertos locales."
        : "Field Shift supports farmer judgment. It does not replace it. Confirm field conditions, markets, water and equipment with local experts."}</p>
      <div><span>FIELD SHIFT</span><span>AGRICULTURAL DECISION SUPPORT</span><span>FINNEY COUNTY, KS</span></div>
    </footer>
  );
}
