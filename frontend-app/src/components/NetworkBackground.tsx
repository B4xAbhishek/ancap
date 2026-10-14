"use client";

import { useEffect, useRef } from "react";
import { usePathname } from "next/navigation";

export function NetworkBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const pathname = usePathname();
  const presentation = pathname === "/" || pathname === "/projects" || pathname === "/investors";

  useEffect(() => {
    if (presentation) return;
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Respect the user's "Reduce motion" OS preference. We still draw a
    // single static frame so the page does not look empty, but the
    // requestAnimationFrame loop is never started.
    const motionQuery =
      typeof window !== "undefined" && typeof window.matchMedia === "function"
        ? window.matchMedia("(prefers-reduced-motion: reduce)")
        : null;
    let prefersReducedMotion = motionQuery?.matches ?? false;

    let width: number, height: number;
    let nodes: Array<{
      x: number;
      y: number;
      vx: number;
      vy: number;
      r: number;
    }> = [];
    let nodeCount = 28;
    const maxDist = 150;
    let scrollPhase = 0;
    let rafId: number | null = null;
    let scrollRafId: number | null = null;

    function targetNodeCount() {
      const area = Math.max((width || 0) * (height || 0), 0);
      return Math.max(18, Math.min(48, Math.round(area / 50000)));
    }

    function resize() {
      if (!canvas) return;
      width = canvas.width = canvas.offsetWidth;
      height = canvas.height = canvas.offsetHeight;
      const nextCount = targetNodeCount();
      if (nodes.length === 0 || nextCount !== nodeCount) {
        nodeCount = nextCount;
        initNodes();
      }
    }

    function initNodes() {
      nodes = [];
      for (let i = 0; i < nodeCount; i++) {
        nodes.push({
          x: Math.random() * width,
          y: Math.random() * height,
          vx: (Math.random() - 0.5) * 0.28,
          vy: (Math.random() - 0.5) * 0.28,
          r: 1.3 + Math.random() * 1.2,
        });
      }
    }

    function updateScrollPhase() {
      const scrollY = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      scrollPhase = docHeight > 0 ? Math.min(1, scrollY / docHeight) : 0;
    }

    function drawFrame(animate: boolean) {
      if (!ctx || !width || !height) return;
      if (nodes.some((n) => !Number.isFinite(n.x) || !Number.isFinite(n.y))) {
        initNodes();
      }

      ctx.clearRect(0, 0, width, height);

      const connectionDist = maxDist * (0.7 + scrollPhase * 0.5);
      const lineOpacity = 0.15 + scrollPhase * 0.2;
      const glowIntensity = 0.3 + scrollPhase * 0.5;
      const hueShift = scrollPhase * 40;

      // Draw edges
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const dx = nodes[i].x - nodes[j].x;
          const dy = nodes[i].y - nodes[j].y;
          const d = Math.hypot(dx, dy);
          if (d < connectionDist) {
            const alpha = (1 - d / connectionDist) * lineOpacity;
            const hue = (170 + hueShift) % 360;
            ctx.strokeStyle = `hsla(${hue}, 80%, 60%, ${alpha})`;
            ctx.lineWidth = 0.8;
            ctx.beginPath();
            ctx.moveTo(nodes[i].x, nodes[i].y);
            ctx.lineTo(nodes[j].x, nodes[j].y);
            ctx.stroke();
          }
        }
      }

      // Draw nodes
      nodes.forEach((n) => {
        if (animate) {
          n.x += n.vx;
          n.y += n.vy;
          if (n.x < 0 || n.x > width) n.vx *= -1;
          if (n.y < 0 || n.y > height) n.vy *= -1;
          n.x = Math.max(0, Math.min(width, n.x));
          n.y = Math.max(0, Math.min(height, n.y));
        }

        const hue = (170 + hueShift) % 360;
        const grd = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, n.r * 6);
        grd.addColorStop(0, `hsla(${hue}, 80%, 70%, ${glowIntensity})`);
        grd.addColorStop(0.4, `hsla(${hue}, 70%, 55%, ${glowIntensity * 0.4})`);
        grd.addColorStop(1, "transparent");
        ctx.fillStyle = grd;
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.r * 6, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = `hsla(${hue}, 85%, 65%, ${0.6 + scrollPhase * 0.3})`;
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
        ctx.fill();
      });

      if (animate && !document.hidden) {
        rafId = requestAnimationFrame(() => drawFrame(true));
      }
    }

    function startLoop() {
      cancelLoop();
      if (prefersReducedMotion) {
        // One static frame, no animation.
        drawFrame(false);
      } else {
        drawFrame(true);
      }
    }

    function cancelLoop() {
      if (rafId !== null) {
        cancelAnimationFrame(rafId);
        rafId = null;
      }
    }

    function onScroll() {
      updateScrollPhase();
      if (scrollRafId !== null) return;
      scrollRafId = requestAnimationFrame(() => {
        scrollRafId = null;
        if (prefersReducedMotion) {
          // Re-render the static frame so scroll-driven hue/opacity still updates,
          // but without continuous animation.
          drawFrame(false);
        }
      });
    }

    function onVisibilityChange() {
      if (document.hidden) {
        cancelLoop();
        return;
      }
      startLoop();
    }

    function onMotionChange(e: MediaQueryListEvent) {
      prefersReducedMotion = e.matches;
      startLoop();
    }

    window.addEventListener("resize", resize);
    window.addEventListener("scroll", onScroll, { passive: true });
    document.addEventListener("visibilitychange", onVisibilityChange);
    motionQuery?.addEventListener?.("change", onMotionChange);
    resize();
    updateScrollPhase();
    startLoop();

    return () => {
      window.removeEventListener("resize", resize);
      window.removeEventListener("scroll", onScroll);
      document.removeEventListener("visibilitychange", onVisibilityChange);
      motionQuery?.removeEventListener?.("change", onMotionChange);
      if (scrollRafId !== null) cancelAnimationFrame(scrollRafId);
      cancelLoop();
    };
  }, [presentation]);

  return presentation ? null : (
    <div className="canvas-wrap" aria-hidden="true">
      <canvas ref={canvasRef} id="network"></canvas>
    </div>
  );
}
