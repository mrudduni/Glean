"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Moon, Sprout, Sun } from "lucide-react";
import { useGlean } from "@/lib/state";
import { useCopy } from "@/lib/useCopy";

export function SiteHeader() {
  const pathname = usePathname();
  const { lang, setLang, theme, setTheme } = useGlean();
  const t = useCopy();
  return (
    <header className="site-header">
      <div className="site-header-inner">
        <Link className="brand" href="/" aria-label={t("app.name", "Glean")}>
          <span className="brand-mark"><Sprout size={19} strokeWidth={2.2} /></span>
          <span className="brand-name text-shimmer">{t("app.name", "Glean")}</span>
        </Link>
        <div className="header-location"><span className="location-dot" /> {t("app.location", "Finney County, Kansas")}</div>
        <nav className="header-nav" aria-label={t("nav.main", "Main navigation")}>
          <Link className={pathname === "/" ? "nav-link active" : "nav-link"} href="/">{t("pick.title")}</Link>
          <Link className={pathname.startsWith("/how-we-know") ? "nav-link active" : "nav-link"} href="/how-we-know">{t("nav.trust")}</Link>
        </nav>
        <div className="header-controls">
          <div className="theme-toggle" role="group" aria-label={t("theme.label", "Colour theme")}>
            <button
              type="button"
              className={theme === "light" ? "active" : ""}
              aria-pressed={theme === "light"}
              onClick={() => setTheme("light")}
              aria-label={t("theme.light", "Light theme")}
            >
              <Sun size={15} strokeWidth={2.2} />
            </button>
            <button
              type="button"
              className={theme === "dark" ? "active" : ""}
              aria-pressed={theme === "dark"}
              onClick={() => setTheme("dark")}
              aria-label={t("theme.dark", "Dark theme")}
            >
              <Moon size={15} strokeWidth={2.2} />
            </button>
          </div>
          <div className="lang-toggle" role="group" aria-label={t("lang.label", "Language")}>
            <button type="button" aria-pressed={lang === "en"} aria-label={t("lang.en")} onClick={() => setLang("en")}>EN</button>
            <button type="button" aria-pressed={lang === "es"} aria-label={t("lang.es")} onClick={() => setLang("es")}>ES</button>
          </div>
        </div>
      </div>
    </header>
  );
}

export function SiteFooter() {
  const t = useCopy();
  return (
    <footer className="site-footer">
      <p>{t("disclaimer.main")}</p>
      <div><span>{t("app.name")}</span><span>{t("app.location", "Finney County, Kansas")}</span><Link href="/how-we-know">{t("nav.trust")}</Link></div>
    </footer>
  );
}
