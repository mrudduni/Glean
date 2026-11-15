"use client";

import { useEffect, useState, useRef } from "react";

export interface ParallaxValues {
  scrollY: number;
  slowY: number;      // ~0.08x
  mediumY: number;    // ~0.18x
  fastY: number;      // ~0.28x
  heroOpacity: number; // fades from 1 to 0 as hero scrolls away
}

export function useScrollParallax(): ParallaxValues {
  const [values, setValues] = useState<ParallaxValues>({
    scrollY: 0,
    slowY: 0,
    mediumY: 0,
    fastY: 0,
    heroOpacity: 1,
  });

  const frameRef = useRef<number | null>(null);

  useEffect(() => {
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReducedMotion) return;

    const handleScroll = () => {
      if (frameRef.current !== null) return;
      frameRef.current = requestAnimationFrame(() => {
        const y = window.scrollY || 0;
        const opacity = Math.max(0, Math.min(1, 1 - y / 620));
        setValues({
          scrollY: y,
          slowY: Math.round(y * 0.08),
          mediumY: Math.round(y * 0.18),
          fastY: Math.round(y * 0.28),
          heroOpacity: Number(opacity.toFixed(3)),
        });
        frameRef.current = null;
      });
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    handleScroll();

    return () => {
      window.removeEventListener("scroll", handleScroll);
      if (frameRef.current !== null) cancelAnimationFrame(frameRef.current);
    };
  }, []);

  return values;
}
