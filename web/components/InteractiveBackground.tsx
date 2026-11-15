"use client";

import { useEffect, useRef } from "react";

export function InteractiveBackground() {
  const primaryGlowRef = useRef<HTMLDivElement>(null);
  const secondaryGlowRef = useRef<HTMLDivElement>(null);
  const tertiaryGlowRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Check for reduced motion
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReducedMotion) return;

    let targetX = window.innerWidth * 0.5;
    let targetY = window.innerHeight * 0.4;
    let currentX1 = targetX;
    let currentY1 = targetY;
    let currentX2 = targetX;
    let currentY2 = targetY;
    let isVisible = false;
    let animFrameId: number;

    const handleMouseMove = (event: MouseEvent) => {
      targetX = event.clientX;
      targetY = event.clientY;
      if (!isVisible) {
        isVisible = true;
        if (primaryGlowRef.current) primaryGlowRef.current.style.opacity = "1";
        if (secondaryGlowRef.current) secondaryGlowRef.current.style.opacity = "1";
      }
    };

    const handleMouseLeave = () => {
      // Smoothly drift toward center-top when cursor leaves window
      targetX = window.innerWidth * 0.5;
      targetY = window.innerHeight * 0.35;
    };

    // Smooth lerp animation loop for 60/120fps fluid tracking
    const updateGlow = () => {
      // Primary emerald orb tracks with 0.08 spring lerp
      currentX1 += (targetX - currentX1) * 0.08;
      currentY1 += (targetY - currentY1) * 0.08;

      // Secondary amber orb trails with 0.045 lerp and slight offset for majestic chromatic depth
      currentX2 += (targetX - currentX2) * 0.045;
      currentY2 += (targetY - currentY2) * 0.045;

      if (primaryGlowRef.current) {
        primaryGlowRef.current.style.transform = `translate3d(${currentX1 - 280}px, ${currentY1 - 280}px, 0)`;
      }
      if (secondaryGlowRef.current) {
        secondaryGlowRef.current.style.transform = `translate3d(${currentX2 - 240}px, ${currentY2 - 200}px, 0)`;
      }

      animFrameId = requestAnimationFrame(updateGlow);
    };

    window.addEventListener("mousemove", handleMouseMove, { passive: true });
    document.addEventListener("mouseleave", handleMouseLeave);
    animFrameId = requestAnimationFrame(updateGlow);

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseleave", handleMouseLeave);
      cancelAnimationFrame(animFrameId);
    };
  }, []);

  return (
    <div className="interactive-bg-container" aria-hidden="true">
      {/* Autonomous breathing ambient waves in the backdrop */}
      <div className="ambient-drift-mesh drift-orb-1" />
      <div className="ambient-drift-mesh drift-orb-2" />
      <div className="ambient-drift-mesh drift-orb-3" />

      {/* Interactive Cursor Follower Orbs with GPU acceleration */}
      <div ref={primaryGlowRef} className="cursor-glow cursor-glow-primary" />
      <div ref={secondaryGlowRef} className="cursor-glow cursor-glow-secondary" />

      {/* Subtle organic noise/texture overlay for tactile luxury finish */}
      <div className="ambient-noise-layer" />
    </div>
  );
}

