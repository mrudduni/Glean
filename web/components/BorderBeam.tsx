"use client";

import React from "react";

interface BorderBeamProps {
  className?: string;
  size?: number;
  duration?: number;
  borderWidth?: number;
  anchor?: number;
  colorFrom?: string;
  colorTo?: string;
  delay?: number;
}

/**
 * BorderBeam — inspired by 21st.dev / Magic UI
 * Animates a luminous radiant beam that travels around the outer perimeter of its parent card.
 */
export function BorderBeam({
  className = "",
  size = 200,
  duration = 8,
  borderWidth = 1.5,
  anchor = 90,
  colorFrom = "var(--color-primary, #34d399)",
  colorTo = "var(--color-accent, #df9a4f)",
  delay = 0,
}: BorderBeamProps) {
  return (
    <div
      style={
        {
          "--beam-size": `${size}px`,
          "--beam-duration": `${duration}s`,
          "--beam-anchor": `${anchor}%`,
          "--beam-border-width": `${borderWidth}px`,
          "--beam-color-from": colorFrom,
          "--beam-color-to": colorTo,
          "--beam-delay": `-${delay}s`,
        } as React.CSSProperties
      }
      className={`border-beam-container ${className}`}
      aria-hidden="true"
    >
      <div className="border-beam-tracer" />
    </div>
  );
}
