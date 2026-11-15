"use client";

import { useEffect, useRef } from "react";

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  size: number;
  alpha: number;
  baseAlpha: number;
  pulsePhase: number;
}

export function InteractiveBackground() {
  const primaryGlowRef = useRef<HTMLDivElement>(null);
  const secondaryGlowRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const meshRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReducedMotion) return;

    let targetX = window.innerWidth * 0.5;
    let targetY = window.innerHeight * 0.4;
    let currentX1 = targetX;
    let currentY1 = targetY;
    let currentX2 = targetX;
    let currentY2 = targetY;
    let isVisible = false;
    let mouseVx = 0;
    let mouseVy = 0;
    let lastMouseX = targetX;
    let lastMouseY = targetY;
    let targetScrollY = window.scrollY || 0;
    let currentScrollY = targetScrollY;
    let scrollVy = 0;
    let lastScrollY = targetScrollY;
    let animFrameId: number;

    const handleScroll = () => {
      targetScrollY = window.scrollY || 0;
      scrollVy = (targetScrollY - lastScrollY) * 0.15;
      lastScrollY = targetScrollY;
    };

    const handleMouseMove = (event: MouseEvent) => {
      mouseVx = (event.clientX - lastMouseX) * 0.25;
      mouseVy = (event.clientY - lastMouseY) * 0.25;
      lastMouseX = event.clientX;
      lastMouseY = event.clientY;

      targetX = event.clientX;
      targetY = event.clientY;
      if (!isVisible) {
        isVisible = true;
        if (primaryGlowRef.current) primaryGlowRef.current.style.opacity = "1";
        if (secondaryGlowRef.current) secondaryGlowRef.current.style.opacity = "1";
      }
    };

    const handleMouseLeave = () => {
      targetX = window.innerWidth * 0.5;
      targetY = window.innerHeight * 0.35;
      mouseVx = 0;
      mouseVy = 0;
    };

    // Canvas particle system: atmospheric prairie wind motes
    const canvas = canvasRef.current;
    const ctx = canvas ? canvas.getContext("2d") : null;
    let width = window.innerWidth;
    let height = window.innerHeight;

    const initCanvasSize = () => {
      if (!canvas || !ctx) return;
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = width * dpr;
      canvas.height = height * dpr;
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
      ctx.scale(dpr, dpr);
    };

    initCanvasSize();
    window.addEventListener("resize", initCanvasSize);

    // Initialize 36 atmospheric particles
    const particleCount = 36;
    const particles: Particle[] = [];
    for (let i = 0; i < particleCount; i++) {
      const baseAlpha = 0.12 + Math.random() * 0.28;
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: 0.3 + Math.random() * 0.45,
        vy: (Math.random() - 0.5) * 0.2,
        size: 0.8 + Math.random() * 1.6,
        alpha: baseAlpha,
        baseAlpha,
        pulsePhase: Math.random() * Math.PI * 2,
      });
    }

    let tick = 0;

    const updateScene = () => {
      tick += 0.015;

      // Smooth cursor lerp
      currentX1 += (targetX - currentX1) * 0.08;
      currentY1 += (targetY - currentY1) * 0.08;
      currentX2 += (targetX - currentX2) * 0.045;
      currentY2 += (targetY - currentY2) * 0.045;

      // Smooth scroll parallax lerp
      currentScrollY += (targetScrollY - currentScrollY) * 0.09;
      scrollVy *= 0.88;

      // Dampen mouse velocity
      mouseVx *= 0.9;
      mouseVy *= 0.9;

      if (primaryGlowRef.current) {
        primaryGlowRef.current.style.transform = `translate3d(${currentX1 - 280}px, ${currentY1 - 280}px, 0)`;
      }
      if (secondaryGlowRef.current) {
        secondaryGlowRef.current.style.transform = `translate3d(${currentX2 - 240}px, ${currentY2 - 200}px, 0)`;
      }
      if (meshRef.current) {
        meshRef.current.style.transform = `translate3d(0, ${-currentScrollY * 0.07}px, 0)`;
      }

      // Render prairie breeze particles
      if (ctx && canvas) {
        ctx.clearRect(0, 0, width, height);
        canvas.style.transform = `translate3d(0, ${-currentScrollY * 0.12}px, 0)`;

        for (let i = 0; i < particles.length; i++) {
          const p = particles[i];

          // Gentle sinusoidal vertical drift simulating atmospheric wave with scroll gust
          p.x += p.vx;
          p.y += p.vy + Math.sin(tick + p.pulsePhase) * 0.25 - scrollVy * 0.12;

          // Mouse wind interaction: subtle push if cursor is within 140px
          const dx = p.x - currentX1;
          const dy = p.y - currentY1;
          const distSq = dx * dx + dy * dy;
          if (distSq < 19600 && distSq > 0) {
            const dist = Math.sqrt(distSq);
            const force = (1 - dist / 140) * 0.6;
            p.x += (dx / dist) * force * 2.5 + mouseVx * 0.1;
            p.y += (dy / dist) * force * 2.5 + mouseVy * 0.1;
          }

          // Wrap boundaries
          if (p.x > width + 20) p.x = -20;
          if (p.x < -20) p.x = width + 20;
          if (p.y > height + 20) p.y = -20;
          if (p.y < -20) p.y = height + 20;

          // Gentle breathing opacity
          const alpha = p.baseAlpha * (0.8 + 0.2 * Math.sin(tick * 1.5 + p.pulsePhase));

          // Draw subtle emerald-tinted particle
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(133, 242, 184, ${alpha})`;
          ctx.fill();
        }
      }

      animFrameId = requestAnimationFrame(updateScene);
    };

    window.addEventListener("mousemove", handleMouseMove, { passive: true });
    window.addEventListener("scroll", handleScroll, { passive: true });
    document.addEventListener("mouseleave", handleMouseLeave);
    animFrameId = requestAnimationFrame(updateScene);

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("scroll", handleScroll);
      document.removeEventListener("mouseleave", handleMouseLeave);
      window.removeEventListener("resize", initCanvasSize);
      cancelAnimationFrame(animFrameId);
    };
  }, []);

  return (
    <div className="interactive-bg-container" aria-hidden="true">
      {/* Autonomous breathing ambient waves with parallax */}
      <div ref={meshRef} style={{ position: "absolute", inset: 0, pointerEvents: "none" }}>
        <div className="ambient-drift-mesh drift-orb-1" />
        <div className="ambient-drift-mesh drift-orb-2" />
        <div className="ambient-drift-mesh drift-orb-3" />
      </div>

      {/* Atmospheric Wind Vector Canvas */}
      <canvas
        ref={canvasRef}
        style={{
          position: "absolute",
          inset: 0,
          pointerEvents: "none",
          zIndex: 1,
          opacity: 0.85,
        }}
      />

      {/* Interactive Cursor Follower Orbs with GPU acceleration */}
      <div ref={primaryGlowRef} className="cursor-glow cursor-glow-primary" />
      <div ref={secondaryGlowRef} className="cursor-glow cursor-glow-secondary" />

      {/* Organic texture overlay */}
      <div className="ambient-noise-layer" />
    </div>
  );
}
