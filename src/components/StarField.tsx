import { useEffect, useRef } from "react";

interface Star {
  x: number; y: number; r: number;
  phase: number; speed: number;
  hue: number; baseAlpha: number;
}

function makeStar(w: number, h: number, rng: () => number): Star {
  const tier = rng();
  return {
    x: rng() * w,
    y: rng() * h,
    r: tier < 0.7 ? 0.5 + rng() * 0.8 : tier < 0.9 ? 1 + rng() * 1.2 : 1.8 + rng() * 1.4,
    phase: rng() * Math.PI * 2,
    speed: 0.3 + rng() * 1.2,
    hue: tier < 0.6 ? 210 + rng() * 40 : tier < 0.85 ? 180 + rng() * 60 : 38 + rng() * 20,
    baseAlpha: tier < 0.7 ? 0.2 + rng() * 0.5 : tier < 0.9 ? 0.4 + rng() * 0.4 : 0.6 + rng() * 0.4,
  };
}

export function StarField() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const rafRef = useRef<number>(0);
  const starsRef = useRef<Star[]>([]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d")!;

    let seed = 42;
    const rng = () => { seed = (seed * 9301 + 49297) % 233280; return seed / 233280; };

    const resize = () => {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
      starsRef.current = Array.from({ length: 220 }, () => makeStar(canvas.width, canvas.height, rng));
    };

    const observer = new ResizeObserver(resize);
    observer.observe(canvas);
    resize();

    let t = 0;
    const draw = () => {
      const { width: w, height: h } = canvas;
      ctx.clearRect(0, 0, w, h);
      t += 0.008;

      for (const s of starsRef.current) {
        const alpha = s.baseAlpha * (0.4 + 0.6 * (0.5 + 0.5 * Math.sin(t * s.speed + s.phase)));
        const glow = s.r > 1.5;

        if (glow) {
          const grad = ctx.createRadialGradient(s.x, s.y, 0, s.x, s.y, s.r * 4);
          grad.addColorStop(0, `hsla(${s.hue},80%,80%,${alpha * 0.6})`);
          grad.addColorStop(1, "transparent");
          ctx.fillStyle = grad;
          ctx.beginPath();
          ctx.arc(s.x, s.y, s.r * 4, 0, Math.PI * 2);
          ctx.fill();
        }

        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        ctx.fillStyle = `hsla(${s.hue},70%,${glow ? 90 : 75}%,${alpha})`;
        ctx.fill();
      }

      rafRef.current = requestAnimationFrame(draw);
    };
    rafRef.current = requestAnimationFrame(draw);

    return () => {
      observer.disconnect();
      cancelAnimationFrame(rafRef.current);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 w-full h-full pointer-events-none"
      style={{ opacity: 0.8 }}
    />
  );
}
