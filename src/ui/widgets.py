"""ui/widgets.py — custom canvas animation widgets for Ohayo."""

import math
import random
import tkinter as tk


# ── StarField ─────────────────────────────────────────────────────────────────

class StarField(tk.Canvas):
    """Animated twinkling night-sky background canvas."""

    def __init__(self, parent, theme, num_stars=140, seed=42, **kw):
        super().__init__(parent, highlightthickness=0, bd=0,
                         bg=theme["bg"], **kw)
        self._t = theme
        self._stars = []
        rnd = random.Random(seed)
        for _ in range(num_stars):
            self._stars.append({
                "x":     rnd.random(),
                "y":     rnd.random(),
                "size":  rnd.choices([1, 1, 1, 2, 2, 3, 4],
                                     weights=[6, 6, 6, 3, 3, 2, 1])[0],
                "base":  rnd.uniform(0.25, 1.0),
                "phase": rnd.uniform(0, math.pi * 2),
                "speed": rnd.uniform(0.5, 2.4),
                "warm":  rnd.random(),
            })
        self._t_anim = 0.0
        self._running = True
        self._after_id = None
        self.bind("<Configure>", self._redraw)
        self._schedule()

    def _schedule(self):
        if self._running:
            self._after_id = self.after(120, self._tick)

    def _tick(self):
        if not self._running:
            return
        self._t_anim += 0.06
        self._redraw()
        self._schedule()

    def stop(self):
        self._running = False
        if self._after_id is not None:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def start(self):
        if not self._running:
            self._running = True
            self._schedule()

    def _redraw(self, _=None):
        self.delete("star")
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 2 or h < 2:
            return
        for st in self._stars:
            x = st["x"] * w
            y = st["y"] * h
            size = st["size"]
            twinkle = math.sin(self._t_anim * st["speed"] + st["phase"]) * 0.5 + 0.5
            brightness = st["base"] * (0.35 + 0.65 * twinkle)
            warm = st["warm"]
            if size >= 3:
                rv = min(255, int((180 + 60 * warm) * brightness))
                gv = min(255, int((190 + 40 * warm) * brightness))
                bv = min(255, int((255 - 80 * warm) * brightness))
            else:
                rv = min(255, int(160 * brightness))
                gv = min(255, int(180 * brightness))
                bv = min(255, int(255 * brightness))
            color = f"#{rv:02x}{gv:02x}{bv:02x}"
            if size >= 3:
                pts = []
                for i in range(8):
                    angle = math.pi / 4 * i - math.pi / 2
                    rr = size if i % 2 == 0 else size * 0.35
                    pts.extend([x + rr * math.cos(angle),
                                 y + rr * math.sin(angle)])
                self.create_polygon(pts, fill=color, outline="", tags="star")
            else:
                self.create_oval(x - size, y - size, x + size, y + size,
                                 fill=color, outline="", tags="star")

    def apply_theme(self, t: dict):
        self._t = t
        self.configure(bg=t["bg"])


# ── AnimatedDot ───────────────────────────────────────────────────────────────

class AnimatedDot(tk.Canvas):
    """Pulsing coloured status indicator dot."""

    def __init__(self, parent, color="#4DD9C0", size=12, bg="#080E1C", **kw):
        super().__init__(parent, width=size, height=size,
                         highlightthickness=0, bg=bg, **kw)
        self.color = color
        self.size = size
        self._running = False
        self._scale = 1.0
        self._dir = -1
        self._draw()

    def _draw(self):
        self.delete("all")
        s = self.size
        m = s * (1 - self._scale) / 2
        self.create_oval(m, m, s - m, s - m, fill=self.color, outline="")

    def start(self):
        self._running = True
        self._tick()

    def stop(self):
        self._running = False
        self._scale = 1.0
        self._draw()

    def _tick(self):
        if not self._running:
            return
        self._scale += self._dir * 0.06
        if self._scale <= 0.45:
            self._dir = 1
        elif self._scale >= 1.0:
            self._dir = -1
        self._draw()
        self.after(55, self._tick)

    def set_color(self, color: str):
        self.color = color
        self._draw()

    def set_bg(self, bg: str):
        self.config(bg=bg)
