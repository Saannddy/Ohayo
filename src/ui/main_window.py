"""ui/main_window.py — Ohayo main application window."""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from datetime import datetime

from theme.themes import DARK_THEME, LIGHT_THEME, FONTS
from core.scheduler import Scheduler
from core.profiles import (get_profile_names, save_profile,
                            load_profile, delete_profile)
from ui.widgets import (GradientHeader, AnimatedDot, CountdownBar,
                        StatsCard, PlaceholderEntry, ActionButton,
                        FilterButton, HeadersEditor)

_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD"]
_ICON_PATH = os.path.join(os.path.dirname(__file__),
                          "..", "..", "images", "icon.png")


# ── helper: card frame ────────────────────────────────────────────────────────

def _card(parent, theme, pady=(0, 10), **kw):
    """Returns a frame styled as a themed card."""
    outer = tk.Frame(parent, bg=theme["card_bg"], pady=4, **kw)
    outer.pack(fill=tk.X, pady=pady)
    sep = tk.Frame(outer, bg=theme["card_border"], height=1)
    sep.pack(fill=tk.X)

    inner = tk.Frame(outer, bg=theme["card_bg"], padx=14, pady=10)
    inner.pack(fill=tk.X)
    return inner


def _section_label(parent, text, theme):
    return tk.Label(parent, text=text, font=("Helvetica", 8, "bold"),
                    bg=parent["bg"], fg=theme["text_secondary"])


# ── MainWindow ────────────────────────────────────────────────────────────────

class MainWindow:
    """Builds and manages the full Ohayo UI."""

    def __init__(self):
        self._t = DARK_THEME          # current theme
        self._scheduler = Scheduler()
        self._log_filter = "ALL"      # ALL, 2xx, 3xx, 4xx, 5xx, ERR
        self._filter_btns: list[FilterButton] = []
        self._accordion_body_open = False

        self._root = tk.Tk()
        self._setup_window()
        self._setup_ttk_style()
        self._build_ui()
        self._wire_scheduler()
        self._apply_theme()

    # ─────────────────────────────────────────────────────────────────────────
    # Window bootstrap
    # ─────────────────────────────────────────────────────────────────────────

    def _setup_window(self):
        r = self._root
        r.title("おはよう — Ohayo")
        r.geometry("960x700")
        r.minsize(820, 580)
        r.configure(bg=self._t["bg"])

        try:
            img = tk.PhotoImage(file=_ICON_PATH)
            r.iconphoto(True, img)
        except Exception:
            pass

    def _setup_ttk_style(self):
        s = ttk.Style(self._root)
        s.theme_use("clam")
        t = self._t
        s.configure("Modern.TCombobox",
                     fieldbackground=t["input_bg"],
                     background=t["input_bg"],
                     foreground=t["fg"],
                     selectbackground=t["sel_bg"],
                     selectforeground=t["fg"],
                     arrowcolor=t["accent"],
                     borderwidth=0,
                     padding=6)
        s.map("Modern.TCombobox",
              fieldbackground=[("readonly", t["input_bg"])],
              foreground=[("readonly", t["fg"])])

        s.configure("Vertical.TScrollbar",
                     background=t["scroll_fg"],
                     troughcolor=t["scroll_bg"],
                     arrowcolor=t["scroll_fg"],
                     borderwidth=0)

    # ─────────────────────────────────────────────────────────────────────────
    # UI construction
    # ─────────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_header()
        self._build_content()

    def _build_header(self):
        t = self._t
        self._header = GradientHeader(
            self._root, c1=t["grad_start"], c2=t["grad_end"], height=72)
        self._header.pack(fill=tk.X)

        # widgets drawn *over* the canvas via create_window
        self._header.update_idletasks()
        self._header.bind("<Configure>", self._on_header_configure)

        # dot
        self._dot = AnimatedDot(self._header, color="white",
                                 size=10, bg=t["grad_start"])
        self._dot_id = self._header.create_window(
            20, 36, anchor="w", window=self._dot)

        # title (Japanese)
        self._title_lbl = tk.Label(self._header,
                                    text="おはよう",
                                    font=("Helvetica", 22, "bold"),
                                    bg=t["grad_start"], fg="white")
        self._title_id = self._header.create_window(
            40, 32, anchor="w", window=self._title_lbl)

        # subtitle
        self._sub_lbl = tk.Label(self._header,
                                  text="URL Request Scheduler",
                                  font=("Helvetica", 9),
                                  bg=t["grad_end"], fg="#FFDDD0")
        self._sub_id = self._header.create_window(
            40, 55, anchor="w", window=self._sub_lbl)

        # theme toggle
        self._theme_btn = tk.Label(self._header,
                                    text="☀️",
                                    font=("Helvetica", 16),
                                    bg=t["grad_end"], cursor="hand2")
        self._theme_btn_id = self._header.create_window(
            900, 36, anchor="e", window=self._theme_btn)
        self._theme_btn.bind("<Button-1>", lambda _: self._toggle_theme())

    def _on_header_configure(self, event):
        w = event.width
        # reposition right-anchored theme button
        self._header.coords(self._theme_btn_id, w - 16, 36)

    def _build_content(self):
        t = self._t
        frame = tk.Frame(self._root, bg=t["bg"])
        frame.pack(fill=tk.BOTH, expand=True)
        self._content_frame = frame

        self._build_sidebar(frame)
        self._build_main_panel(frame)

    # ── Sidebar ───────────────────────────────────────────────────────────────

    def _build_sidebar(self, parent):
        t = self._t
        self._sidebar = tk.Frame(parent, bg=t["sidebar_bg"], width=300)
        self._sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
        self._sidebar.pack_propagate(False)

        # scrollable canvas inside sidebar
        canvas = tk.Canvas(self._sidebar, bg=t["sidebar_bg"],
                           highlightthickness=0, bd=0)
        sb = tk.Scrollbar(self._sidebar, orient="vertical",
                          command=canvas.yview,
                          bg=t["scroll_fg"])
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._sb_canvas = canvas

        inner = tk.Frame(canvas, bg=t["sidebar_bg"])
        self._sb_inner = inner
        self._sb_win = canvas.create_window((0, 0), window=inner, anchor="nw")

        inner.bind("<Configure>", self._on_sb_inner_configure)
        canvas.bind("<Configure>", self._on_sb_canvas_configure)

        # mouse wheel scroll
        def _on_wheel(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_wheel)

        self._build_sidebar_content(inner)

    def _on_sb_inner_configure(self, _=None):
        self._sb_canvas.configure(
            scrollregion=self._sb_canvas.bbox("all"))

    def _on_sb_canvas_configure(self, event):
        self._sb_canvas.itemconfig(self._sb_win, width=event.width)

    def _build_sidebar_content(self, parent):
        t = self._t
        pad = {"padx": 14}

        # ── Section: Config ──
        tk.Frame(parent, bg=t["sidebar_bg"], height=12).pack()

        sec_lbl = tk.Label(parent, text="CONFIGURATION",
                            font=("Helvetica", 8, "bold"),
                            bg=t["sidebar_bg"], fg=t["text_secondary"])
        sec_lbl.pack(anchor="w", **pad)
        self._sec_lbl = sec_lbl

        config_card = tk.Frame(parent, bg=t["card_bg"], padx=14, pady=12)
        config_card.pack(fill=tk.X, pady=(6, 0))
        self._config_card = config_card

        # Method row
        method_row = tk.Frame(config_card, bg=t["card_bg"])
        method_row.pack(fill=tk.X, pady=(0, 10))

        tk.Label(method_row, text="Method", font=("Helvetica", 9, "bold"),
                 bg=t["card_bg"], fg=t["text_secondary"]).pack(side=tk.LEFT)

        self._method_var = tk.StringVar(value="GET")
        self._method_cb = ttk.Combobox(method_row, textvariable=self._method_var,
                                        values=_METHODS, state="readonly",
                                        width=10, style="Modern.TCombobox",
                                        font=("Helvetica", 10, "bold"))
        self._method_cb.pack(side=tk.RIGHT)
        self._method_cb.bind("<<ComboboxSelected>>", self._on_method_change)

        # URL
        self._url_entry = PlaceholderEntry(
            config_card, label="URL",
            placeholder="https://example.com/api/ping",
            theme=t, font=("Helvetica", 10))
        self._url_entry.pack(fill=tk.X, pady=(0, 8))

        # Interval
        self._interval_entry = PlaceholderEntry(
            config_card, label="Interval (seconds)",
            placeholder="5",
            theme=t, font=("Helvetica", 10))
        self._interval_entry.pack(fill=tk.X, pady=(0, 8))

        # Stop Time
        self._stop_entry = PlaceholderEntry(
            config_card, label="Stop Time  HH:MM",
            placeholder="23:59",
            theme=t, font=("Helvetica", 10))
        self._stop_entry.pack(fill=tk.X)

        # ── Section: Body (accordion) ──
        tk.Frame(parent, bg=t["sidebar_bg"], height=10).pack()

        body_toggle = tk.Frame(parent, bg=t["card_bg"], padx=14, pady=10)
        body_toggle.pack(fill=tk.X)
        self._body_toggle_frame = body_toggle

        body_toggle_lbl = tk.Label(body_toggle, text="▶  Request Body",
                                    font=("Helvetica", 9, "bold"),
                                    bg=t["card_bg"], fg=t["text_secondary"],
                                    cursor="hand2")
        body_toggle_lbl.pack(side=tk.LEFT)
        self._body_toggle_lbl = body_toggle_lbl
        body_toggle_lbl.bind("<Button-1>", self._toggle_body)

        method_note = tk.Label(body_toggle, text="POST/PUT only",
                                font=("Helvetica", 8),
                                bg=t["card_bg"], fg=t["text_muted"])
        method_note.pack(side=tk.RIGHT)

        self._body_area_frame = tk.Frame(parent, bg=t["card_bg"],
                                          padx=14, pady=6)
        # don't pack yet — accordion is collapsed

        tk.Label(self._body_area_frame, text="Body (raw)",
                 font=("Helvetica", 8, "bold"),
                 bg=t["card_bg"], fg=t["text_secondary"]).pack(anchor="w")

        self._body_text = tk.Text(self._body_area_frame,
                                   font=("Courier", 9), height=5,
                                   bg=t["input_bg"], fg=t["fg"],
                                   insertbackground=t["cursor"],
                                   relief=tk.FLAT, bd=0,
                                   wrap=tk.WORD,
                                   selectbackground=t["sel_bg"])
        self._body_text.pack(fill=tk.X, pady=(4, 0))

        # ── Section: Headers ──
        tk.Frame(parent, bg=t["sidebar_bg"], height=10).pack()

        headers_card = tk.Frame(parent, bg=t["card_bg"], padx=14, pady=10)
        headers_card.pack(fill=tk.X)
        self._headers_card = headers_card
        self._headers_editor = HeadersEditor(headers_card, theme=t)
        self._headers_editor.pack(fill=tk.X)

        # ── Section: Profiles ──
        tk.Frame(parent, bg=t["sidebar_bg"], height=10).pack()

        tk.Label(parent, text="PROFILES",
                 font=("Helvetica", 8, "bold"),
                 bg=t["sidebar_bg"], fg=t["text_secondary"]).pack(anchor="w", **pad)

        prof_card = tk.Frame(parent, bg=t["card_bg"], padx=14, pady=10)
        prof_card.pack(fill=tk.X, pady=(6, 0))
        self._prof_card = prof_card

        self._prof_var = tk.StringVar(value="Select profile…")
        self._prof_cb = ttk.Combobox(prof_card, textvariable=self._prof_var,
                                      state="readonly", width=22,
                                      style="Modern.TCombobox",
                                      font=("Helvetica", 9))
        self._prof_cb.pack(fill=tk.X, pady=(0, 8))
        self._refresh_profiles()

        prof_btns = tk.Frame(prof_card, bg=t["card_bg"])
        prof_btns.pack(fill=tk.X)

        self._prof_save_btn = ActionButton(
            prof_btns, text="💾  Save",
            command=self._save_profile,
            bg=t["accent"], hover_bg=t["accent_hover"], fg="white",
            disabled_bg=t["disabled"], disabled_fg=t["disabled_fg"],
            font=("Helvetica", 9, "bold"), padx=12, pady=6)
        self._prof_save_btn.pack(side=tk.LEFT, padx=(0, 6))

        self._prof_load_btn = ActionButton(
            prof_btns, text="📂  Load",
            command=self._load_profile,
            bg=t["card_border"], hover_bg=t["border"], fg=t["fg"],
            disabled_bg=t["disabled"], disabled_fg=t["disabled_fg"],
            font=("Helvetica", 9, "bold"), padx=12, pady=6)
        self._prof_load_btn.pack(side=tk.LEFT, padx=(0, 6))

        self._prof_del_btn = ActionButton(
            prof_btns, text="🗑",
            command=self._delete_profile,
            bg=t["danger_bg"], hover_bg=t["danger"], fg=t["danger"],
            disabled_bg=t["disabled"], disabled_fg=t["disabled_fg"],
            font=("Helvetica", 10), padx=10, pady=6)
        self._prof_del_btn.pack(side=tk.LEFT)

        # ── Section: Controls ──
        tk.Frame(parent, bg=t["sidebar_bg"], height=12).pack()

        ctrl_card = tk.Frame(parent, bg=t["card_bg"], padx=14, pady=14)
        ctrl_card.pack(fill=tk.X, pady=(0, 14))
        self._ctrl_card = ctrl_card

        btn_row = tk.Frame(ctrl_card, bg=t["card_bg"])
        btn_row.pack(fill=tk.X, pady=(0, 12))

        self._start_btn = ActionButton(
            btn_row, text="▶  START",
            command=self._on_start,
            bg=t["success"], hover_bg=t["success_hover"], fg="white",
            disabled_bg=t["disabled"], disabled_fg=t["disabled_fg"],
            font=("Helvetica", 10, "bold"), padx=16, pady=10)
        self._start_btn.pack(side=tk.LEFT, padx=(0, 8))

        self._stop_btn = ActionButton(
            btn_row, text="⏹  STOP",
            command=self._on_stop,
            bg=t["danger"], hover_bg=t["danger_hover"], fg="white",
            disabled_bg=t["disabled"], disabled_fg=t["disabled_fg"],
            font=("Helvetica", 10, "bold"), padx=16, pady=10,
            state=tk.DISABLED)
        self._stop_btn.pack(side=tk.LEFT, padx=(0, 8))

        self._clear_btn = ActionButton(
            btn_row, text="🗑",
            command=self._on_clear,
            bg=t["filter_bg"], hover_bg=t["border"], fg=t["text_secondary"],
            disabled_bg=t["disabled"], disabled_fg=t["disabled_fg"],
            font=("Helvetica", 10), padx=12, pady=10)
        self._clear_btn.pack(side=tk.LEFT)

        # Status row
        status_row = tk.Frame(ctrl_card, bg=t["card_bg"])
        status_row.pack(fill=tk.X, pady=(0, 8))

        self._status_dot = AnimatedDot(status_row, color=t["text_muted"],
                                        size=10, bg=t["card_bg"])
        self._status_dot.pack(side=tk.LEFT, padx=(0, 8))

        self._status_lbl = tk.Label(status_row, text="Ready to start",
                                     font=("Helvetica", 9),
                                     bg=t["card_bg"], fg=t["text_secondary"])
        self._status_lbl.pack(side=tk.LEFT)

        # Countdown bar
        self._countdown = CountdownBar(ctrl_card, bg=t["filter_bg"],
                                        fill=t["accent"], height=4)
        self._countdown.pack(fill=tk.X, pady=(4, 0))

    # ── Main panel (right) ────────────────────────────────────────────────────

    def _build_main_panel(self, parent):
        t = self._t
        self._main = tk.Frame(parent, bg=t["panel_bg"])
        self._main.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # thin left border separator
        sep = tk.Frame(parent, bg=t["border"], width=1)
        sep.place(relx=0, rely=0, relheight=1)

        self._build_stats_row()
        self._build_log_section()

    def _build_stats_row(self):
        t = self._t
        row = tk.Frame(self._main, bg=t["panel_bg"], pady=16, padx=16)
        row.pack(fill=tk.X)
        self._stats_row = row

        specs = [
            ("Total Requests", "—",  t["accent"]),
            ("Success Rate",   "—%", t["success"]),
            ("Avg Response",   "—ms",t["warning"]),
            ("Last Status",    "—",  t["text_secondary"]),
        ]

        self._stat_cards: list[StatsCard] = []
        for i, (lbl, val, col) in enumerate(specs):
            card = StatsCard(row, label=lbl, value=val, color=col, theme=t)
            card.grid(row=0, column=i, padx=(0, 12), sticky="ew")
            row.columnconfigure(i, weight=1)
            self._stat_cards.append(card)

    def _build_log_section(self):
        t = self._t

        # header row: title + filter buttons + export
        log_hdr = tk.Frame(self._main, bg=t["panel_bg"], padx=16)
        log_hdr.pack(fill=tk.X, pady=(0, 8))
        self._log_hdr = log_hdr

        tk.Label(log_hdr, text="📋  Request Log",
                 font=("Helvetica", 11, "bold"),
                 bg=t["panel_bg"], fg=t["fg"]).pack(side=tk.LEFT)

        export_btn = ActionButton(
            log_hdr, text="⬇  Export",
            command=self._export_log,
            bg=t["filter_bg"], hover_bg=t["border"], fg=t["text_secondary"],
            disabled_bg=t["disabled"], disabled_fg=t["disabled_fg"],
            font=("Helvetica", 8, "bold"), padx=10, pady=4)
        export_btn.pack(side=tk.RIGHT, padx=(8, 0))
        self._export_btn = export_btn

        # filter pills
        filters_frame = tk.Frame(log_hdr, bg=t["panel_bg"])
        filters_frame.pack(side=tk.RIGHT, padx=(0, 8))
        self._filters_frame = filters_frame

        for fname in ["ALL", "2xx", "3xx", "4xx", "5xx", "ERR"]:
            active = fname == "ALL"
            btn = FilterButton(filters_frame, text=fname,
                                on_toggle=self._on_filter,
                                active=active, theme=t)
            btn.pack(side=tk.LEFT, padx=2)
            btn._label = fname  # type: ignore
            self._filter_btns.append(btn)

        # log text area
        log_outer = tk.Frame(self._main, bg=t["log_bg"], padx=16, pady=(0))
        log_outer.pack(fill=tk.BOTH, expand=True, padx=0, pady=(0, 16))
        self._log_outer = log_outer

        log_frame = tk.Frame(log_outer, bg=t["log_bg"])
        log_frame.pack(fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(log_frame, orient="vertical",
                             style="Vertical.TScrollbar")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self._log = tk.Text(log_frame,
                             font=("Courier", 9),
                             bg=t["log_bg"], fg=t["fg"],
                             insertbackground=t["cursor"],
                             selectbackground=t["sel_bg"],
                             relief=tk.FLAT, bd=0,
                             state=tk.DISABLED,
                             wrap=tk.WORD,
                             yscrollcommand=vsb.set,
                             padx=10, pady=8)
        self._log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.config(command=self._log.yview)

        self._log.tag_config("2xx",    foreground=t["tag_2xx"])
        self._log.tag_config("3xx",    foreground=t["tag_3xx"])
        self._log.tag_config("4xx",    foreground=t["tag_4xx"])
        self._log.tag_config("5xx",    foreground=t["tag_5xx"])
        self._log.tag_config("error",  foreground=t["tag_error"])
        self._log.tag_config("info",   foreground=t["tag_info"])
        self._log.tag_config("ts",     foreground=t["tag_ts"])
        self._log.tag_config("method", foreground=t["tag_method"])
        self._log.tag_config("ms",     foreground=t["tag_ms"])

    # ─────────────────────────────────────────────────────────────────────────
    # Theme
    # ─────────────────────────────────────────────────────────────────────────

    def _toggle_theme(self):
        self._t = LIGHT_THEME if self._t["name"] == "dark" else DARK_THEME
        self._theme_btn.config(
            text="🌙" if self._t["name"] == "light" else "☀️")
        self._apply_theme()

    def _apply_theme(self):
        t = self._t
        r = self._root
        r.configure(bg=t["bg"])

        self._header.update_colors(t["grad_start"], t["grad_end"])
        self._title_lbl.config(bg=t["grad_start"])
        self._sub_lbl.config(bg=t["grad_end"])
        self._theme_btn.config(bg=t["grad_end"])
        self._dot.set_bg(t["grad_start"])

        self._content_frame.config(bg=t["bg"])
        self._sidebar.config(bg=t["sidebar_bg"])
        self._sb_canvas.config(bg=t["sidebar_bg"])
        self._sb_inner.config(bg=t["sidebar_bg"])

        # config card
        self._config_card.config(bg=t["card_bg"])
        for child in self._config_card.winfo_children():
            try:
                child.config(bg=t["card_bg"])
            except Exception:
                pass
        self._url_entry.apply_theme(t)
        self._interval_entry.apply_theme(t)
        self._stop_entry.apply_theme(t)

        # method combo
        s = ttk.Style()
        s.configure("Modern.TCombobox",
                     fieldbackground=t["input_bg"],
                     background=t["input_bg"],
                     foreground=t["fg"],
                     selectbackground=t["sel_bg"],
                     selectforeground=t["fg"],
                     arrowcolor=t["accent"])
        s.map("Modern.TCombobox",
              fieldbackground=[("readonly", t["input_bg"])],
              foreground=[("readonly", t["fg"])])

        # body accordion
        self._body_toggle_frame.config(bg=t["card_bg"])
        self._body_toggle_lbl.config(bg=t["card_bg"], fg=t["text_secondary"])
        self._body_area_frame.config(bg=t["card_bg"])
        self._body_text.config(bg=t["input_bg"], fg=t["fg"],
                                insertbackground=t["cursor"],
                                selectbackground=t["sel_bg"])

        # headers
        self._headers_card.config(bg=t["card_bg"])
        self._headers_editor.apply_theme(t)

        # profiles
        self._prof_card.config(bg=t["card_bg"])
        self._prof_save_btn.update_colors(t["accent"], t["accent_hover"], "white",
                                           t["disabled"], t["disabled_fg"])
        self._prof_load_btn.update_colors(t["card_border"], t["border"], t["fg"],
                                           t["disabled"], t["disabled_fg"])
        self._prof_del_btn.update_colors(t["danger_bg"], t["danger"], t["danger"],
                                          t["disabled"], t["disabled_fg"])

        # controls card
        self._ctrl_card.config(bg=t["card_bg"])
        self._start_btn.update_colors(t["success"], t["success_hover"], "white",
                                       t["disabled"], t["disabled_fg"])
        self._stop_btn.update_colors(t["danger"], t["danger_hover"], "white",
                                      t["disabled"], t["disabled_fg"])
        self._clear_btn.update_colors(t["filter_bg"], t["border"],
                                       t["text_secondary"],
                                       t["disabled"], t["disabled_fg"])
        self._status_lbl.config(bg=t["card_bg"])
        self._status_dot.set_bg(t["card_bg"])
        self._countdown.update_theme(t["filter_bg"], t["accent"])

        # section labels
        self._sec_lbl.config(bg=t["sidebar_bg"], fg=t["text_secondary"])

        # stats row
        self._stats_row.config(bg=t["panel_bg"])
        for card in self._stat_cards:
            card.apply_theme(t)

        # main panel
        self._main.config(bg=t["panel_bg"])
        self._log_hdr.config(bg=t["panel_bg"])
        for child in self._log_hdr.winfo_children():
            try:
                child.config(bg=t["panel_bg"])
            except Exception:
                pass

        self._export_btn.update_colors(t["filter_bg"], t["border"],
                                        t["text_secondary"],
                                        t["disabled"], t["disabled_fg"])

        self._filters_frame.config(bg=t["panel_bg"])
        for fb in self._filter_btns:
            fb.apply_theme(t)

        self._log_outer.config(bg=t["log_bg"])
        self._log.config(bg=t["log_bg"], fg=t["fg"],
                          insertbackground=t["cursor"],
                          selectbackground=t["sel_bg"])
        self._log.tag_config("2xx",    foreground=t["tag_2xx"])
        self._log.tag_config("3xx",    foreground=t["tag_3xx"])
        self._log.tag_config("4xx",    foreground=t["tag_4xx"])
        self._log.tag_config("5xx",    foreground=t["tag_5xx"])
        self._log.tag_config("error",  foreground=t["tag_error"])
        self._log.tag_config("info",   foreground=t["tag_info"])
        self._log.tag_config("ts",     foreground=t["tag_ts"])
        self._log.tag_config("method", foreground=t["tag_method"])
        self._log.tag_config("ms",     foreground=t["tag_ms"])

        # scrollbar
        s.configure("Vertical.TScrollbar",
                     background=t["scroll_fg"],
                     troughcolor=t["scroll_bg"],
                     arrowcolor=t["scroll_fg"])

    # ─────────────────────────────────────────────────────────────────────────
    # Body accordion
    # ─────────────────────────────────────────────────────────────────────────

    def _toggle_body(self, _=None):
        self._accordion_body_open = not self._accordion_body_open
        if self._accordion_body_open:
            self._body_area_frame.pack(fill=tk.X, after=self._body_toggle_frame)
            self._body_toggle_lbl.config(text="▼  Request Body")
        else:
            self._body_area_frame.pack_forget()
            self._body_toggle_lbl.config(text="▶  Request Body")

    # ─────────────────────────────────────────────────────────────────────────
    # Method selector
    # ─────────────────────────────────────────────────────────────────────────

    def _on_method_change(self, _=None):
        method = self._method_var.get()
        if method in ("POST", "PUT", "PATCH") and not self._accordion_body_open:
            self._toggle_body()

    # ─────────────────────────────────────────────────────────────────────────
    # Scheduler wiring
    # ─────────────────────────────────────────────────────────────────────────

    def _wire_scheduler(self):
        sch = self._scheduler
        (sch
         .on("response",    self._on_response)
         .on("req_error",   self._on_req_error)
         .on("countdown",   self._on_countdown)
         .on("completed",   self._on_completed)
         .on("finished",    self._on_finished)
         .on("error_event", self._on_error_event))

    def _safe(self, fn, *args, **kwargs):
        """Schedule a UI call on the main thread."""
        self._root.after(0, lambda: fn(*args, **kwargs))

    # ── scheduler callbacks (arrive on bg thread) ─────────────────────────────

    def _on_response(self, data: dict):
        self._safe(self._handle_response, data)

    def _on_req_error(self, data: dict):
        self._safe(self._handle_req_error, data)

    def _on_countdown(self, remaining: int, total: int):
        self._safe(self._handle_countdown, remaining, total)

    def _on_completed(self, stop_time):
        self._safe(self._handle_completed, stop_time)

    def _on_finished(self):
        self._safe(self._handle_finished)

    def _on_error_event(self, msg: str):
        self._safe(self._handle_error_event, msg)

    # ── UI-thread handlers ────────────────────────────────────────────────────

    def _handle_response(self, data: dict):
        code = data["status"]
        ts   = data["timestamp"]
        cnt  = data["count"]
        ms   = data["elapsed_ms"]
        meth = data["method"]

        if code < 300:
            tag = "2xx"
        elif code < 400:
            tag = "3xx"
        elif code < 500:
            tag = "4xx"
        else:
            tag = "5xx"

        line = f"[{ts}]  #{cnt:>4}  {meth}  {code}  {ms:>7.1f}ms"

        if self._matches_filter(tag):
            self._append_log(line, tag, ts, meth, ms)

        self._update_stats()

    def _handle_req_error(self, data: dict):
        ts  = data["timestamp"]
        cnt = data["count"]
        err = data["error"]
        ms  = data["elapsed_ms"]

        line = f"[{ts}]  #{cnt:>4}  ERROR  {ms:>7.1f}ms  — {err}"
        if self._matches_filter("error"):
            self._append_log(line, "error", ts, None, ms)
        self._update_stats()

    def _handle_countdown(self, remaining: int, total: int):
        progress = remaining / total
        self._countdown.set_progress(progress)
        self._status_lbl.config(
            text=f"Next request in {remaining}s…",
            fg=self._t["text_secondary"])

    def _handle_completed(self, stop_time):
        self._status_lbl.config(
            text=f"Completed at {stop_time.strftime('%H:%M')}",
            fg=self._t["success"])
        self._status_dot.set_color(self._t["success"])
        self._countdown.set_progress(0.0)

    def _handle_finished(self):
        self._start_btn.configure_state(tk.NORMAL)
        self._stop_btn.configure_state(tk.DISABLED)
        self._status_dot.stop()
        self._countdown.set_progress(0.0)
        if "Running" in (self._status_lbl.cget("text") or ""):
            self._status_lbl.config(text="Stopped", fg=self._t["danger"])

    def _handle_error_event(self, msg: str):
        self._status_lbl.config(text=f"Error: {msg}", fg=self._t["danger"])

    # ─────────────────────────────────────────────────────────────────────────
    # Log helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _matches_filter(self, tag: str) -> bool:
        f = self._log_filter
        if f == "ALL":
            return True
        if f == "ERR":
            return tag == "error"
        return tag == f

    def _append_log(self, line: str, tag: str, ts: str,
                    method: str | None, ms: float):
        log = self._log
        log.config(state=tk.NORMAL)
        log.insert(tk.END, line + "\n", tag)
        log.see(tk.END)
        log.config(state=tk.DISABLED)

    def _update_stats(self):
        s = self._scheduler.stats
        self._stat_cards[0].set_value(str(s["total"]))
        self._stat_cards[1].set_value(f"{s['success_pct']:.1f}%")
        self._stat_cards[2].set_value(f"{s['avg_ms']:.0f}ms")
        st = s["last_status"]
        self._stat_cards[3].set_value(str(st) if st else "—")

    # ─────────────────────────────────────────────────────────────────────────
    # Control actions
    # ─────────────────────────────────────────────────────────────────────────

    def _on_start(self):
        url = self._url_entry.get().strip()
        interval_str = self._interval_entry.get().strip()
        stop_str = self._stop_entry.get().strip()

        if not url:
            messagebox.showerror("おはよう", "Please enter a URL")
            return
        if not interval_str:
            messagebox.showerror("おはよう", "Please enter an interval in seconds")
            return
        if not stop_str:
            messagebox.showerror("おはよう", "Please enter a stop time (HH:MM)")
            return

        try:
            interval = int(interval_str)
            if interval <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("おはよう", "Interval must be a positive integer")
            return

        try:
            stop_time = datetime.strptime(stop_str, "%H:%M").time()
        except ValueError:
            messagebox.showerror("おはよう", "Stop time must be HH:MM (24-hour)")
            return

        # collect headers & body
        headers = self._headers_editor.get_headers()
        body = self._body_text.get("1.0", tk.END).strip() \
            if self._accordion_body_open else ""
        method = self._method_var.get()

        # update UI
        self._start_btn.configure_state(tk.DISABLED)
        self._stop_btn.configure_state(tk.NORMAL)
        self._status_lbl.config(text="Running…", fg=self._t["success"])
        self._status_dot.set_color(self._t["success"])
        self._status_dot.start()
        self._countdown.set_progress(1.0)

        self._scheduler.start(url, method, headers, body, interval, stop_time)

    def _on_stop(self):
        self._scheduler.stop()
        self._status_lbl.config(text="Stopped", fg=self._t["danger"])
        self._status_dot.set_color(self._t["danger"])
        self._status_dot.stop()
        self._countdown.set_progress(0.0)

    def _on_clear(self):
        self._log.config(state=tk.NORMAL)
        self._log.delete("1.0", tk.END)
        self._log.config(state=tk.DISABLED)
        # reset stats
        self._scheduler.reset_stats()
        for i, v in enumerate(["—", "—%", "—ms", "—"]):
            self._stat_cards[i].set_value(v)

    # ─────────────────────────────────────────────────────────────────────────
    # Filter
    # ─────────────────────────────────────────────────────────────────────────

    def _on_filter(self, clicked: FilterButton):
        for btn in self._filter_btns:
            btn.set_active(btn is clicked)
        self._log_filter = clicked._label  # type: ignore

    # ─────────────────────────────────────────────────────────────────────────
    # Export
    # ─────────────────────────────────────────────────────────────────────────

    def _export_log(self):
        content = self._log.get("1.0", tk.END).strip()
        if not content:
            messagebox.showinfo("おはよう", "Log is empty — nothing to export.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text file", "*.txt"), ("CSV", "*.csv"), ("All", "*.*")],
            title="Export Request Log",
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("おはよう", f"Log exported to:\n{path}")

    # ─────────────────────────────────────────────────────────────────────────
    # Profiles
    # ─────────────────────────────────────────────────────────────────────────

    def _refresh_profiles(self):
        names = get_profile_names()
        self._prof_cb["values"] = names
        if names:
            self._prof_cb.set(names[0])
        else:
            self._prof_cb.set("Select profile…")

    def _save_profile(self):
        name = simpledialog.askstring(
            "Save Profile", "Profile name:", parent=self._root)
        if not name:
            return
        data = {
            "url":      self._url_entry.get(),
            "method":   self._method_var.get(),
            "interval": self._interval_entry.get(),
            "stop":     self._stop_entry.get(),
            "headers":  self._headers_editor.get_headers(),
            "body":     self._body_text.get("1.0", tk.END).strip(),
        }
        save_profile(name, data)
        self._refresh_profiles()

    def _load_profile(self):
        name = self._prof_var.get()
        if not name or name == "Select profile…":
            messagebox.showinfo("おはよう", "Select a profile first.")
            return
        data = load_profile(name)
        if not data:
            return
        self._url_entry.set(data.get("url", ""))
        self._method_var.set(data.get("method", "GET"))
        self._interval_entry.set(data.get("interval", ""))
        self._stop_entry.set(data.get("stop", ""))
        headers = data.get("headers", {})
        self._headers_editor.set_headers(headers)
        body = data.get("body", "")
        if body and not self._accordion_body_open:
            self._toggle_body()
        self._body_text.delete("1.0", tk.END)
        self._body_text.insert("1.0", body)

    def _delete_profile(self):
        name = self._prof_var.get()
        if not name or name == "Select profile…":
            messagebox.showinfo("おはよう", "Select a profile first.")
            return
        if messagebox.askyesno("Delete Profile",
                                f"Delete profile '{name}'?"):
            delete_profile(name)
            self._refresh_profiles()

    # ─────────────────────────────────────────────────────────────────────────
    # Run
    # ─────────────────────────────────────────────────────────────────────────

    def run(self):
        self._root.mainloop()


def run_app():
    app = MainWindow()
    app.run()
