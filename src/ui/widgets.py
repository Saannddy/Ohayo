"""ui/widgets.py — custom Tkinter widget primitives for Ohayo."""

import math
import random
import tkinter as tk
from tkinter import ttk


# ── colour helpers ────────────────────────────────────────────────────────────

def _hex2rgb(h: str):
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _lerp_color(c1: str, c2: str, t: float) -> str:
    r1, g1, b1 = _hex2rgb(c1)
    r2, g2, b2 = _hex2rgb(c2)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


# ── StarField ─────────────────────────────────────────────────────────────────

class StarField(tk.Canvas):
    """Animated twinkling blue-white night-sky background."""

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
                # 0 = pure blue-white, 1 = warm golden (for larger accent stars)
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
                # Large stars: blue-white to soft gold
                rv = min(255, int((180 + 60 * warm) * brightness))
                gv = min(255, int((190 + 40 * warm) * brightness))
                bv = min(255, int((255 - 80 * warm) * brightness))
            else:
                # Small stars: blue-white
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


# ── GradientHeader ────────────────────────────────────────────────────────────

class GradientHeader(tk.Canvas):
    """Full-width gradient header with decorative gold star sparkles."""

    _STARS = [
        (0.50, 0.25, 4.5), (0.54, 0.75, 3.0), (0.59, 0.35, 5.5),
        (0.63, 0.68, 3.5), (0.67, 0.18, 6.0), (0.71, 0.60, 4.0),
        (0.75, 0.30, 3.0), (0.79, 0.75, 5.0), (0.83, 0.22, 4.5),
        (0.87, 0.58, 6.5), (0.91, 0.38, 3.5), (0.95, 0.65, 4.5),
        (0.97, 0.22, 3.0),
    ]

    def __init__(self, parent, c1: str, c2: str, height=88, **kw):
        super().__init__(parent, height=height, highlightthickness=0, bd=0, **kw)
        self._c1, self._c2 = c1, c2
        self.bind("<Configure>", self._redraw)

    def _redraw(self, _=None):
        self.delete("all")
        w = self.winfo_width() or 960
        h = self.winfo_height() or 88
        step = max(1, w // 400)
        for x in range(0, w, step):
            t = x / max(w - 1, 1)
            col = _lerp_color(self._c1, self._c2, t)
            self.create_rectangle(x, 0, x + step + 1, h,
                                  fill=col, outline="")
        for rx, ry, size in self._STARS:
            cx, cy = w * rx, h * ry
            pts = []
            for i in range(8):
                angle = math.pi / 4 * i - math.pi / 2
                r = size if i % 2 == 0 else size * 0.35
                pts.extend([cx + r * math.cos(angle),
                             cy + r * math.sin(angle)])
            self.create_polygon(pts, fill="#FFD166", outline="")

    def update_colors(self, c1: str, c2: str):
        self._c1, self._c2 = c1, c2
        self._redraw()


# ── AnimatedDot ───────────────────────────────────────────────────────────────

class AnimatedDot(tk.Canvas):
    """Pulsing coloured circle used as a status indicator."""

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


# ── CountdownBar ──────────────────────────────────────────────────────────────

class CountdownBar(tk.Canvas):
    """Slim horizontal progress bar for request-interval countdown."""

    def __init__(self, parent, bg="#0E1B30", fill="#FFD166", height=5, **kw):
        super().__init__(parent, height=height, highlightthickness=0, **kw)
        self._bg = bg
        self._fill = fill
        self._progress = 0.0
        self.config(bg=bg)
        self.bind("<Configure>", self._draw)

    def set_progress(self, value: float):
        self._progress = max(0.0, min(1.0, value))
        self._draw()

    def _draw(self, _=None):
        self.delete("all")
        w = self.winfo_width() or 1
        h = self.winfo_height() or 5
        self.create_rectangle(0, 0, w, h, fill=self._bg, outline="")
        fw = int(w * self._progress)
        if fw > 0:
            self.create_rectangle(0, 0, fw, h, fill=self._fill, outline="")

    def update_theme(self, bg: str, fill: str):
        self._bg = bg
        self._fill = fill
        self.config(bg=bg)
        self._draw()


# ── StatsCard ─────────────────────────────────────────────────────────────────

class StatsCard(tk.Frame):
    """Metric tile with a coloured accent bar at top and large value."""

    def __init__(self, parent, label: str, value="—",
                 color="#FFD166", theme=None, **kw):
        from theme.themes import DARK_THEME
        t = theme or DARK_THEME
        super().__init__(parent, bg=t["card_bg"], **kw)
        self._t = t
        self.color = color

        self._accent_bar = tk.Frame(self, bg=color, height=3)
        self._accent_bar.pack(fill=tk.X)

        body = tk.Frame(self, bg=t["card_bg"], padx=12, pady=10)
        body.pack(fill=tk.X)
        self._body = body

        self._val_var = tk.StringVar(value=value)
        self._val_lbl = tk.Label(body, textvariable=self._val_var,
                                  font=("Helvetica", 20, "bold"),
                                  bg=t["card_bg"], fg=color)
        self._val_lbl.pack(anchor="w")

        self._name_lbl = tk.Label(body, text=label,
                                   font=("Helvetica", 8),
                                   bg=t["card_bg"], fg=t["text_secondary"])
        self._name_lbl.pack(anchor="w")

    def set_value(self, v):
        self._val_var.set(str(v))

    def apply_theme(self, t: dict):
        self._t = t
        self.config(bg=t["card_bg"])
        self._body.config(bg=t["card_bg"])
        self._val_lbl.config(bg=t["card_bg"])
        self._name_lbl.config(bg=t["card_bg"], fg=t["text_secondary"])


# ── PlaceholderEntry ──────────────────────────────────────────────────────────

class PlaceholderEntry(tk.Frame):
    """Entry with placeholder text, animated focus border, optional label."""

    def __init__(self, parent, label="", placeholder="",
                 theme=None, font=None, show="", **kw):
        from theme.themes import DARK_THEME
        t = theme or DARK_THEME
        super().__init__(parent, bg=t["card_bg"], **kw)
        self._t = t
        self._ph = placeholder
        self._ph_active = False
        self._font = font or ("Helvetica", 10)

        if label:
            lw = tk.Label(self, text=label, font=("Helvetica", 9, "bold"),
                          bg=t["card_bg"], fg=t["text_secondary"], anchor="w")
            lw.pack(fill=tk.X, pady=(0, 4))
            self._lw = lw
        else:
            self._lw = None

        self._border = tk.Frame(self, bg=t["input_border"], padx=1, pady=1)
        self._border.pack(fill=tk.X)

        inner = tk.Frame(self._border, bg=t["input_bg"])
        inner.pack(fill=tk.X)
        self._inner = inner

        self.entry = tk.Entry(inner, font=self._font, show=show,
                              bg=t["input_bg"], fg=t["text_muted"],
                              insertbackground=t["cursor"],
                              relief=tk.FLAT, bd=0,
                              selectbackground=t["sel_bg"])
        self.entry.pack(fill=tk.X, padx=12, pady=10)

        if placeholder:
            self._show_ph()

        self.entry.bind("<FocusIn>",  self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)

    def _show_ph(self):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, self._ph)
        self.entry.config(fg=self._t["text_muted"])
        self._ph_active = True

    def _on_focus_in(self, _=None):
        if self._ph_active:
            self.entry.delete(0, tk.END)
            self.entry.config(fg=self._t["fg"])
            self._ph_active = False
        self._border.config(bg=self._t["accent"])

    def _on_focus_out(self, _=None):
        if not self.entry.get():
            self._show_ph()
        self._border.config(bg=self._t["input_border"])

    def get(self) -> str:
        return "" if self._ph_active else self.entry.get()

    def set(self, value: str):
        self.entry.delete(0, tk.END)
        if value:
            self.entry.insert(0, value)
            self.entry.config(fg=self._t["fg"])
            self._ph_active = False
        else:
            if self._ph:
                self._show_ph()

    def apply_theme(self, t: dict):
        self._t = t
        self.config(bg=t["card_bg"])
        if self._lw:
            self._lw.config(bg=t["card_bg"], fg=t["text_secondary"])
        self._border.config(bg=t["input_border"])
        self._inner.config(bg=t["input_bg"])
        self.entry.config(bg=t["input_bg"],
                          fg=t["text_muted"] if self._ph_active else t["fg"],
                          insertbackground=t["cursor"],
                          selectbackground=t["sel_bg"])


# ── ActionButton ──────────────────────────────────────────────────────────────

class ActionButton(tk.Label):
    """Flat hover-animated button built on tk.Label."""

    def __init__(self, parent, text, command=None,
                 bg="#FFD166", hover_bg="#F5B800", fg="#080E1C",
                 disabled_bg="#12284A", disabled_fg="#2C4060",
                 font=None, padx=18, pady=10,
                 state=tk.NORMAL, **kw):
        self._font = font or ("Helvetica", 10, "bold")
        super().__init__(parent, text=text, font=self._font,
                         bg=bg, fg=fg, cursor="hand2",
                         padx=padx, pady=pady,
                         relief=tk.FLAT, **kw)
        self._bg = bg
        self._hover = hover_bg
        self._fg = fg
        self._dis_bg = disabled_bg
        self._dis_fg = disabled_fg
        self._state = state
        self._cmd = command

        self.bind("<Enter>",    self._on_enter)
        self.bind("<Leave>",    self._on_leave)
        self.bind("<Button-1>", self._on_click)

        if state == tk.DISABLED:
            self._apply_disabled()

    def _on_enter(self, _=None):
        if self._state != tk.DISABLED:
            self.config(bg=self._hover)

    def _on_leave(self, _=None):
        if self._state != tk.DISABLED:
            self.config(bg=self._bg)

    def _on_click(self, _=None):
        if self._state != tk.DISABLED and self._cmd:
            self._cmd()

    def _apply_disabled(self):
        self.config(bg=self._dis_bg, fg=self._dis_fg, cursor="")

    def _apply_normal(self):
        self.config(bg=self._bg, fg=self._fg, cursor="hand2")

    def configure_state(self, state):
        self._state = state
        if state == tk.DISABLED:
            self._apply_disabled()
        else:
            self._apply_normal()

    def update_colors(self, bg, hover_bg, fg,
                      disabled_bg=None, disabled_fg=None):
        self._bg = bg
        self._hover = hover_bg
        self._fg = fg
        if disabled_bg:
            self._dis_bg = disabled_bg
        if disabled_fg:
            self._dis_fg = disabled_fg
        if self._state == tk.DISABLED:
            self._apply_disabled()
        else:
            self._apply_normal()


# ── FilterButton ──────────────────────────────────────────────────────────────

class FilterButton(tk.Label):
    """Toggle-style filter pill button."""

    def __init__(self, parent, text, on_toggle=None,
                 active=False, theme=None, **kw):
        from theme.themes import DARK_THEME
        t = theme or DARK_THEME
        self._t = t
        self._active = active
        self._on_toggle = on_toggle
        bg = t["filter_act"] if active else t["filter_bg"]
        fg = t["bg"] if active else t["text_secondary"]
        super().__init__(parent, text=text, font=("Helvetica", 8, "bold"),
                         bg=bg, fg=fg, cursor="hand2",
                         padx=10, pady=4, relief=tk.FLAT, **kw)
        self.bind("<Button-1>", self._click)

    def _click(self, _=None):
        if self._on_toggle:
            self._on_toggle(self)

    def set_active(self, active: bool):
        self._active = active
        self.config(
            bg=self._t["filter_act"] if active else self._t["filter_bg"],
            fg=self._t["bg"] if active else self._t["text_secondary"],
        )

    def apply_theme(self, t: dict):
        self._t = t
        self.set_active(self._active)


# ── MiniEntry ─────────────────────────────────────────────────────────────────

class MiniEntry(tk.Frame):
    """Compact labelled entry for use in grid rows."""

    def __init__(self, parent, label="", placeholder="",
                 theme=None, width=None, **kw):
        from theme.themes import DARK_THEME
        t = theme or DARK_THEME
        super().__init__(parent, bg=t["card_bg"], **kw)
        self._t = t
        self._ph = placeholder
        self._ph_active = False

        self._lbl = tk.Label(self, text=label, font=("Helvetica", 8, "bold"),
                              bg=t["card_bg"], fg=t["text_secondary"], anchor="w")
        self._lbl.pack(fill=tk.X, pady=(0, 3))

        self._border = tk.Frame(self, bg=t["input_border"], padx=1, pady=1)
        self._border.pack(fill=tk.X)

        inner = tk.Frame(self._border, bg=t["input_bg"])
        inner.pack(fill=tk.X)
        self._inner = inner

        self.entry = tk.Entry(inner, font=("Helvetica", 10),
                               bg=t["input_bg"], fg=t["text_muted"],
                               insertbackground=t["cursor"],
                               relief=tk.FLAT, bd=0,
                               selectbackground=t["sel_bg"],
                               width=width)
        self.entry.pack(fill=tk.X, padx=8, pady=8)

        if placeholder:
            self._show_ph()

        self.entry.bind("<FocusIn>",  self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)

    def _show_ph(self):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, self._ph)
        self.entry.config(fg=self._t["text_muted"])
        self._ph_active = True

    def _on_focus_in(self, _=None):
        if self._ph_active:
            self.entry.delete(0, tk.END)
            self.entry.config(fg=self._t["fg"])
            self._ph_active = False
        self._border.config(bg=self._t["accent"])

    def _on_focus_out(self, _=None):
        if not self.entry.get():
            self._show_ph()
        self._border.config(bg=self._t["input_border"])

    def get(self) -> str:
        return "" if self._ph_active else self.entry.get()

    def set(self, value: str):
        self.entry.delete(0, tk.END)
        if value:
            self.entry.insert(0, value)
            self.entry.config(fg=self._t["fg"])
            self._ph_active = False
        else:
            if self._ph:
                self._show_ph()

    def apply_theme(self, t: dict):
        self._t = t
        self.config(bg=t["card_bg"])
        self._lbl.config(bg=t["card_bg"], fg=t["text_secondary"])
        self._border.config(bg=t["input_border"])
        self._inner.config(bg=t["input_bg"])
        self.entry.config(bg=t["input_bg"],
                          fg=t["text_muted"] if self._ph_active else t["fg"],
                          insertbackground=t["cursor"],
                          selectbackground=t["sel_bg"])


# ── HeadersEditor ─────────────────────────────────────────────────────────────

class HeadersEditor(tk.Frame):
    """Dynamic key-value header editor."""

    def __init__(self, parent, theme=None, **kw):
        from theme.themes import DARK_THEME
        t = theme or DARK_THEME
        super().__init__(parent, bg=t["card_bg"], **kw)
        self._t = t
        self._rows: list[tuple] = []

        top = tk.Frame(self, bg=t["card_bg"])
        top.pack(fill=tk.X, pady=(0, 6))
        self._top_frame = top

        self._headers_lbl = tk.Label(top, text="HEADERS",
                                      font=("Helvetica", 8, "bold"),
                                      bg=t["card_bg"], fg=t["text_secondary"])
        self._headers_lbl.pack(side=tk.LEFT)

        self._add_btn = tk.Label(top, text="+ Add", font=("Helvetica", 8),
                                  bg=t["card_bg"], fg=t["accent"], cursor="hand2")
        self._add_btn.pack(side=tk.RIGHT)
        self._add_btn.bind("<Button-1>", lambda _: self.add_row())

        self._rows_frame = tk.Frame(self, bg=t["card_bg"])
        self._rows_frame.pack(fill=tk.X)

    def add_row(self, key="", value=""):
        t = self._t
        row = tk.Frame(self._rows_frame, bg=t["card_bg"])
        row.pack(fill=tk.X, pady=2)

        k = tk.Entry(row, font=("Helvetica", 9),
                     bg=t["input_bg"], fg=t["fg"],
                     insertbackground=t["cursor"],
                     relief=tk.FLAT, bd=0, width=14)
        k.insert(0, key)
        k.pack(side=tk.LEFT, padx=(0, 4), ipady=6, fill=tk.X, expand=True)

        v = tk.Entry(row, font=("Helvetica", 9),
                     bg=t["input_bg"], fg=t["fg"],
                     insertbackground=t["cursor"],
                     relief=tk.FLAT, bd=0)
        v.insert(0, value)
        v.pack(side=tk.LEFT, padx=(0, 4), ipady=6, fill=tk.X, expand=True)

        idx = len(self._rows)
        del_btn = tk.Label(row, text="✕", font=("Helvetica", 10),
                            bg=t["card_bg"], fg=t["danger"], cursor="hand2")
        del_btn.pack(side=tk.LEFT)
        del_btn.bind("<Button-1>", lambda _, i=idx: self._remove(i))

        self._rows.append((k, v, del_btn, row))

    def _remove(self, idx: int):
        if idx < len(self._rows):
            _, _, _, row = self._rows[idx]
            row.destroy()
            self._rows[idx] = None  # type: ignore

    def get_headers(self) -> dict:
        result = {}
        for item in self._rows:
            if item is None:
                continue
            k, v, _, _ = item
            key = k.get().strip()
            val = v.get().strip()
            if key:
                result[key] = val
        return result

    def set_headers(self, headers: dict):
        for item in self._rows:
            if item:
                item[3].destroy()
        self._rows.clear()
        for k, v in headers.items():
            self.add_row(k, v)

    def apply_theme(self, t: dict):
        self._t = t
        self.config(bg=t["card_bg"])
        self._top_frame.config(bg=t["card_bg"])
        self._headers_lbl.config(bg=t["card_bg"], fg=t["text_secondary"])
        self._rows_frame.config(bg=t["card_bg"])
        self._add_btn.config(bg=t["card_bg"], fg=t["accent"])
        for item in self._rows:
            if item is None:
                continue
            k, v, del_btn, row = item
            row.config(bg=t["card_bg"])
            k.config(bg=t["input_bg"], fg=t["fg"],
                     insertbackground=t["cursor"])
            v.config(bg=t["input_bg"], fg=t["fg"],
                     insertbackground=t["cursor"])
            del_btn.config(bg=t["card_bg"], fg=t["danger"])
