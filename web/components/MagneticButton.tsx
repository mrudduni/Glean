"use client";

import React, { useRef, useState, useCallback, useEffect } from "react";

interface MagneticProps {
  children: React.ReactElement<React.HTMLAttributes<HTMLElement>>;
  strength?: number;
  radius?: number;
  className?: string;
}

/**
 * MagneticButton — inspired by 21st.dev
 * Subtle physics-based magnetic pull toward the mouse cursor with smooth spring return.
 */
export function MagneticButton({
  children,
  strength = 0.28,
  radius = 60,
  className = "",
}: MagneticProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    setPrefersReducedMotion(media.matches);
  }, []);

  const handleMouseMove = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      if (prefersReducedMotion || !containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      const distanceX = e.clientX - centerX;
      const distanceY = e.clientY - centerY;
      const distance = Math.hypot(distanceX, distanceY);

      if (distance < radius) {
        setPosition({
          x: distanceX * strength,
          y: distanceY * strength,
        });
      } else {
        setPosition({ x: 0, y: 0 });
      }
    },
    [strength, radius, prefersReducedMotion]
  );

  const handleMouseLeave = useCallback(() => {
    setPosition({ x: 0, y: 0 });
  }, []);

  return (
    <div
      ref={containerRef}
      className={`magnetic-container ${className}`}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{ display: "inline-block" }}
    >
      <div
        className="magnetic-inner"
        style={{
          transform: `translate3d(${position.x.toFixed(1)}px, ${position.y.toFixed(1)}px, 0)`,
          transition: position.x === 0 && position.y === 0
            ? "transform 0.45s cubic-bezier(0.25, 1, 0.5, 1)"
            : "transform 0.12s ease-out",
        }}
      >
        {children}
      </div>
    </div>
  );
}
