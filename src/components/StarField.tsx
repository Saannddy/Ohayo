import { useEffect, useRef } from "react";
import { useAppStore } from "../store/appStore";

interface Star {
  x: number; y: number; r: number;
  phase: number; speed: number; hue: number; baseAlpha: number;
}

function makeStar(w: number, h: number, rng: () => number, dark: boolean): Star {
  const tier = rng();
  return {
    x: rng() * w,
    y: rng() * h,
    r:         dark ? (tier < 0.7 ? 0.4 + rng() * 0.8 : tier < 0.9 ? 0.9 + rng() * 1.2 : 1.6 + rng() * 1.5)
                    : (0.8 + rng() * 2.5),
    phase:     rng() * Math.PI * 2,
    speed:     dark ? 0.3 + rng() * 1.4 : 0.15 + rng() * 0.4,
    hue:       dark ? (tier < 0.55 ? 210 + rng() * 50 : tier < 0.8 ? 260 + rng() * 40 : 45 + rng() * 15)
                    : (tier < 0.5 ? 200 + rng() * 30 : 35 + rng() * 25),
    baseAlpha: dark ? (tier < 0.65 ? 0.2 + rng() * 0.55 : tier < 0.88 ? 0.45 + rng() * 0.35 : 0.65 + rng() * 0.35)
                    : (0.04 + rng() * 0.1),
  };
}

export function StarField() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const rafRef    = useRef<number>(0);
  const starsRef  = useRef<Star[]>([]);
  const { isDark } = useAppStore();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d")!;

    let seed = 42;
    const rng = () => { seed = (seed * 9301 + 49297) % 233280; return seed / 233280; };

    const resize = () => {
      canvas.width  = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
      seed = 42;
      starsRef.current = Array.from({ length: isDark ? 230 : 60 }, () =>
        makeStar(canvas.width, canvas.height, rng, isDark)
      );
    };

    const observer = new ResizeObserver(resize);
    observer.observe(canvas);
    resize();

    let t = 0;
    const draw = () => {
      const { width: w, height: h } = canvas;
      ctx.clearRect(0, 0, w, h);
      t += isDark ? 0.008 : 0.004;

      if (!isDark) {
        // Morning sky: soft sun glow in top-right, floating light orbs
        const grd = ctx.createRadialGradient(w * 0.85, h * 0.12, 0, w * 0.85, h * 0.12, w * 0.55);
        grd.addColorStop(0,   "rgba(253,224,71,0.13)");
        grd.addColorStop(0.4, "rgba(253,186,116,0.07)");
        grd.addColorStop(1,   "transparent");
        ctx.fillStyle = grd;
        ctx.fillRect(0, 0, w, h);
      }

      for (const s of starsRef.current) {
        const alpha = s.baseAlpha * (0.3 + 0.7 * (0.5 + 0.5 * Math.sin(t * s.speed + s.phase)));
        if (isDark) {
          const glow = s.r > 1.5;
          if (glow) {
            const g = ctx.createRadialGradient(s.x, s.y, 0, s.x, s.y, s.r * 5);
            g.addColorStop(0, `hsla(${s.hue},75%,85%,${alpha * 0.55})`);
            g.addColorStop(1, "transparent");
            ctx.fillStyle = g;
            ctx.beginPath();
            ctx.arc(s.x, s.y, s.r * 5, 0, Math.PI * 2);
            ctx.fill();
          }
          ctx.beginPath();
          ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
          ctx.fillStyle = `hsla(${s.hue},65%,${glow ? 92 : 78}%,${alpha})`;
          ctx.fill();
        } else {
          // Light mode: soft floating orbs (morning haze)
          const g = ctx.createRadialGradient(s.x, s.y, 0, s.x, s.y, s.r * 3);
          g.addColorStop(0, `hsla(${s.hue},60%,70%,${alpha})`);
          g.addColorStop(1, "transparent");
          ctx.fillStyle = g;
          ctx.beginPath();
          ctx.arc(s.x, s.y, s.r * 3, 0, Math.PI * 2);
          ctx.fill();
        }
      }

      rafRef.current = requestAnimationFrame(draw);
    };
    rafRef.current = requestAnimationFrame(draw);

    return () => { observer.disconnect(); cancelAnimationFrame(rafRef.current); };
  }, [isDark]);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 w-full h-full pointer-events-none"
      style={{ opacity: isDark ? 0.85 : 0.6 }}
    />
  );
}
