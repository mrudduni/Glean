"use client";

import React, { useRef, useState, useCallback, useEffect } from "react";

interface SpotlightCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  className?: string;
  spotlightColor?: string;
  enableTilt?: boolean;
  tiltMax?: number;
  as?: React.ElementType;
}

export function SpotlightCard({
  children,
  className = "",
  spotlightColor,
  enableTilt = true,
  tiltMax = 4,
  as: Component = "div",
  onMouseMove,
  onMouseLeave,
  onMouseEnter,
  ...rest
}: SpotlightCardProps) {
  const cardRef = useRef<HTMLDivElement>(null);
  const [isHovered, setIsHovered] = useState(false);
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    setPrefersReducedMotion(media.matches);
    const listener = (e: MediaQueryListEvent) => setPrefersReducedMotion(e.matches);
    media.addEventListener("change", listener);
    return () => media.removeEventListener("change", listener);
  }, []);

  const handleMouseMove = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      if (!cardRef.current) return;
      const rect = cardRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      // Update CSS variables directly on DOM node for 60/120fps performance without React re-renders
      cardRef.current.style.setProperty("--spotlight-x", `${x}px`);
      cardRef.current.style.setProperty("--spotlight-y", `${y}px`);

      if (enableTilt && !prefersReducedMotion) {
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        const rotateX = ((y - centerY) / centerY) * -tiltMax;
        const rotateY = ((x - centerX) / centerX) * tiltMax;
        cardRef.current.style.setProperty("--card-rotate-x", `${rotateX.toFixed(2)}deg`);
        cardRef.current.style.setProperty("--card-rotate-y", `${rotateY.toFixed(2)}deg`);
      }

      onMouseMove?.(e);
    },
    [enableTilt, tiltMax, prefersReducedMotion, onMouseMove]
  );

  const handleMouseEnter = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      setIsHovered(true);
      onMouseEnter?.(e);
    },
    [onMouseEnter]
  );

  const handleMouseLeave = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      setIsHovered(false);
      if (cardRef.current) {
        cardRef.current.style.setProperty("--card-rotate-x", "0deg");
        cardRef.current.style.setProperty("--card-rotate-y", "0deg");
      }
      onMouseLeave?.(e);
    },
    [onMouseLeave]
  );

  return (
    <Component
      ref={cardRef}
      className={`spotlight-card ${isHovered ? "is-hovered" : ""} ${className}`}
      onMouseMove={handleMouseMove}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      style={
        spotlightColor
          ? ({ ...rest.style, "--spotlight-color": spotlightColor } as React.CSSProperties)
          : rest.style
      }
      {...rest}
    >
      <div className="spotlight-card-glow" aria-hidden="true" />
      <div className="spotlight-card-border" aria-hidden="true" />
      <div className="spotlight-card-content">{children}</div>
    </Component>
  );
}
