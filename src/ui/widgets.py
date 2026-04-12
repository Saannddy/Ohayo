"""ui/widgets.py — custom Tkinter widget primitives for Ohayo."""

import tkinter as tk
from tkinter import ttk


# ── colour helpers ───────────────────────────────────────────────────────────

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


# ── GradientHeader ───────────────────────────────────────────────────────────

class GradientHeader(tk.Canvas):
    """Full-width canvas that fills itself with a horizontal gradient."""

    def __init__(self, parent, c1: str, c2: str, height=70, **kw):
        super().__init__(parent, height=height, highlightthickness=0, bd=0, **kw)
        self._c1, self._c2 = c1, c2
        self.bind("<Configure>", self._redraw)

    def _redraw(self, _=None):
        self.delete("grad")
        w = self.winfo_width() or 900
        h = self.winfo_height() or 70
        step = max(1, w // 300)
        for x in range(0, w, step):
            t = x / max(w - 1, 1)
            col = _lerp_color(self._c1, self._c2, t)
            self.create_rectangle(x, 0, x + step + 1, h,
                                   fill=col, outline="", tags="grad")

    def update_colors(self, c1: str, c2: str):
        self._c1, self._c2 = c1, c2
        self._redraw()


# ── AnimatedDot ──────────────────────────────────────────────────────────────

class AnimatedDot(tk.Canvas):
    """Pulsing coloured circle used as a status indicator."""

    def __init__(self, parent, color="#56E39F", size=12, bg="#0D1117", **kw):
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
        self.create_oval(m, m, s - m, s - m,
                         fill=self.color, outline="")

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


# ── CountdownBar ─────────────────────────────────────────────────────────────

class CountdownBar(tk.Canvas):
    """Horizontal progress bar used as a request-interval countdown."""

    def __init__(self, parent, bg="#161B22", fill="#FF7043", height=4, **kw):
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
        h = self.winfo_height() or 4
        self.create_rectangle(0, 0, w, h, fill=self._bg, outline="")
        fw = int(w * self._progress)
        if fw > 0:
            self.create_rectangle(0, 0, fw, h,
                                   fill=self._fill, outline="")

    def update_theme(self, bg: str, fill: str):
        self._bg = bg
        self._fill = fill
        self.config(bg=bg)
        self._draw()


# ── StatsCard ────────────────────────────────────────────────────────────────

class StatsCard(tk.Frame):
    """A metric tile showing a large number + descriptor label."""

    def __init__(self, parent, label: str, value="—",
                 color="#FF7043", theme=None, **kw):
        from theme.themes import DARK_THEME
        t = theme or DARK_THEME
        super().__init__(parent, bg=t["card_bg"],
                         padx=14, pady=10, **kw)
        self._t = t
        self.color = color

        self._val_var = tk.StringVar(value=value)
        self._val_lbl = tk.Label(self, textvariable=self._val_var,
                                  font=("Helvetica", 20, "bold"),
                                  bg=t["card_bg"], fg=color)
        self._val_lbl.pack(anchor="w")

        self._name_lbl = tk.Label(self, text=label,
                                   font=("Helvetica", 8),
                                   bg=t["card_bg"], fg=t["text_secondary"])
        self._name_lbl.pack(anchor="w")

    def set_value(self, v):
        self._val_var.set(str(v))

    def apply_theme(self, t: dict):
        self._t = t
        self.config(bg=t["card_bg"])
        self._val_lbl.config(bg=t["card_bg"])
        self._name_lbl.config(bg=t["card_bg"], fg=t["text_secondary"])


# ── PlaceholderEntry ─────────────────────────────────────────────────────────

class PlaceholderEntry(tk.Frame):
    """Entry widget with placeholder text, animated focus border, optional label."""

    def __init__(self, parent, label="", placeholder="",
                 theme=None, font=None, show="", **kw):
        from theme.themes import DARK_THEME
        t = theme or DARK_THEME
        super().__init__(parent, bg=t["bg"], **kw)
        self._t = t
        self._ph = placeholder
        self._ph_active = False
        self._font = font or ("Helvetica", 10)

        if label:
            lw = tk.Label(self, text=label, font=("Helvetica", 9, "bold"),
                          bg=t["bg"], fg=t["text_secondary"], anchor="w")
            lw.pack(fill=tk.X, pady=(0, 3))
            self._lw = lw
        else:
            self._lw = None

        # border frame (1 px)
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
        self.entry.pack(fill=tk.X, padx=10, pady=7)

        if placeholder:
            self._show_ph()

        self.entry.bind("<FocusIn>",  self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)

    # ── placeholder ──────────────────────────────────────────────────────
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

    # ── public API ───────────────────────────────────────────────────────
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
        self.config(bg=t["bg"])
        if self._lw:
            self._lw.config(bg=t["bg"], fg=t["text_secondary"])
        self._border.config(bg=t["input_border"])
        self._inner.config(bg=t["input_bg"])
        self.entry.config(bg=t["input_bg"],
                          fg=t["text_muted"] if self._ph_active else t["fg"],
                          insertbackground=t["cursor"],
                          selectbackground=t["sel_bg"])


# ── ActionButton ─────────────────────────────────────────────────────────────

class ActionButton(tk.Label):
    """
    A flat, hover-animated button built on tk.Label so we can control every pixel.
    bg / hover_bg / fg / disabled_bg / disabled_fg are explicit.
    """

    def __init__(self, parent, text, command=None,
                 bg="#FF7043", hover_bg="#FF5722", fg="white",
                 disabled_bg="#21262D", disabled_fg="#484F58",
                 font=None, padx=18, pady=9,
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


# ── FilterButton ─────────────────────────────────────────────────────────────

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
        fg = "white" if active else t["text_secondary"]
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
            fg="white" if active else self._t["text_secondary"],
        )

    def apply_theme(self, t: dict):
        self._t = t
        self.set_active(self._active)


# ── HeadersEditor ────────────────────────────────────────────────────────────

class HeadersEditor(tk.Frame):
    """Dynamic key-value header editor."""

    def __init__(self, parent, theme=None, **kw):
        from theme.themes import DARK_THEME
        t = theme or DARK_THEME
        super().__init__(parent, bg=t["card_bg"], **kw)
        self._t = t
        self._rows: list[tuple] = []  # (key_entry, val_entry, del_btn, row_frame)

        top = tk.Frame(self, bg=t["card_bg"])
        top.pack(fill=tk.X, pady=(0, 4))

        tk.Label(top, text="HEADERS", font=("Helvetica", 8, "bold"),
                 bg=t["card_bg"], fg=t["text_secondary"]).pack(side=tk.LEFT)

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
        k.pack(side=tk.LEFT, padx=(0, 4), ipady=5, fill=tk.X, expand=True)

        v = tk.Entry(row, font=("Helvetica", 9),
                     bg=t["input_bg"], fg=t["fg"],
                     insertbackground=t["cursor"],
                     relief=tk.FLAT, bd=0)
        v.insert(0, value)
        v.pack(side=tk.LEFT, padx=(0, 4), ipady=5, fill=tk.X, expand=True)

        idx = len(self._rows)
        del_btn = tk.Label(row, text="✕", font=("Helvetica", 9),
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
        # clear
        for item in self._rows:
            if item:
                item[3].destroy()
        self._rows.clear()
        for k, v in headers.items():
            self.add_row(k, v)

    def apply_theme(self, t: dict):
        self._t = t
        self.config(bg=t["card_bg"])
        self._rows_frame.config(bg=t["card_bg"])
