"""ui/main_window.py — Ohayo CustomTkinter UI with auto theme + send modes."""

import os
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from datetime import datetime

import customtkinter as ctk

from theme.themes import DARK_THEME, LIGHT_THEME, T
from core.scheduler import Scheduler
from core.profiles import (get_profile_names, save_profile,
                            load_profile, delete_profile)
from ui.widgets import StarField, AnimatedDot

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD"]
_ICON_PATH = os.path.join(os.path.dirname(__file__),
                          "..", "..", "images", "icon.png")

MODE_SINGLE     = "single"
MODE_COUNT      = "count"
MODE_CONTINUOUS = "continuous"
_MODES = [
    ("⚡", "Once",       MODE_SINGLE),
    ("🔁", "Repeat N",   MODE_COUNT),
    ("♾",  "Continuous", MODE_CONTINUOUS),
]


# ───────────────────────────────────────────────────────────────────────────────


class MainWindow:
    def __init__(self):
        self._is_dark = True
        self._scheduler = Scheduler()
        self._log_filter = "ALL"
        self._is_running = False
        self._stored_headers: dict = {}
        self._stored_body: str = ""
        self._profile_widgets: list = []
        self._mode = MODE_CONTINUOUS
        self._mode_buttons: dict = {}
        self._filter_btns: dict = {}
        self._tk_bg_widgets: list = []
        self._tk_card_bg_widgets: list = []
        self._hero_img = None
        self._sb_icon_img = None

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self._root = ctk.CTk()
        self._setup_window()
        self._load_images()
        self._build_ui()
        self._wire_scheduler()
        self._update_mode_ui()

    # ── bootstrap ──────────────────────────────────────────────────────────────

    def _setup_window(self):
        r = self._root
        r.title("おはよう — The API Waker")
        r.geometry("1240x800")
        r.minsize(1020, 680)
        r.configure(fg_color=T("bg"))
        try:
            img = tk.PhotoImage(file=_ICON_PATH)
            r.iconphoto(True, img)
        except Exception:
            pass

    def _load_images(self):
        if not HAS_PIL:
            return
        try:
            pil = Image.open(_ICON_PATH).convert("RGBA")
            self._hero_img    = ctk.CTkImage(light_image=pil, dark_image=pil, size=(72, 72))
            self._sb_icon_img = ctk.CTkImage(light_image=pil, dark_image=pil, size=(40, 40))
        except Exception:
            pass

    def _build_ui(self):
        self._build_sidebar()
        self._build_content()

    # ── sidebar ────────────────────────────────────────────────────────────────

    def _build_sidebar(self):
        self._sidebar = ctk.CTkFrame(self._root, width=236,
                                      fg_color=T("sidebar_bg"), corner_radius=0)
        self._sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self._sidebar.pack_propagate(False)

        self._sb_sep = ctk.CTkFrame(self._root, width=1,
                                     fg_color=T("border"), corner_radius=0)
        self._sb_sep.pack(side=tk.LEFT, fill=tk.Y)

        # Brand block
        brand = ctk.CTkFrame(self._sidebar, fg_color="transparent")
        brand.pack(fill=tk.X, padx=22, pady=(24, 12))

        if self._sb_icon_img:
            ctk.CTkLabel(brand, image=self._sb_icon_img, text="").pack(
                anchor="w", pady=(0, 12))

        ctk.CTkLabel(brand, text="おはよう",
                     font=(None, 24, "bold"),
                     text_color=T("accent")).pack(anchor="w")

        ctk.CTkLabel(brand, text="API Waker · v2",
                     font=(None, 9),
                     text_color=T("text_secondary")).pack(anchor="w",
                                                           pady=(2, 0))

        ctk.CTkFrame(self._sidebar, height=1,
                      fg_color=T("border"), corner_radius=0).pack(
            fill=tk.X, padx=18, pady=(14, 16))

        # Profiles header
        phdr = ctk.CTkFrame(self._sidebar, fg_color="transparent")
        phdr.pack(fill=tk.X, padx=22)

        ctk.CTkLabel(phdr, text="SAVED PROFILES",
                     font=(None, 8, "bold"),
                     text_color=T("text_muted")).pack(side=tk.LEFT,
                                                       pady=(0, 8))

        # Scrollable profile list
        self._prof_scroll = ctk.CTkScrollableFrame(
            self._sidebar,
            fg_color="transparent",
            scrollbar_fg_color=T("sidebar_bg"),
            scrollbar_button_color=T("scroll_fg"),
            scrollbar_button_hover_color=T("accent"),
            corner_radius=0,
        )
        self._prof_scroll.pack(fill=tk.BOTH, expand=True, padx=10)

        # Bottom controls
        ctk.CTkFrame(self._sidebar, height=1,
                      fg_color=T("border"), corner_radius=0).pack(
            fill=tk.X, padx=18, side=tk.BOTTOM)

        bottom = ctk.CTkFrame(self._sidebar, fg_color="transparent")
        bottom.pack(fill=tk.X, padx=18, pady=16, side=tk.BOTTOM)

        ctk.CTkButton(bottom, text="＋  Save Profile",
                      command=self._save_profile,
                      fg_color=T("filter_bg"),
                      hover_color=T("card_border"),
                      text_color=T("text_secondary"),
                      font=(None, 10, "bold"),
                      height=36, corner_radius=10).pack(fill=tk.X,
                                                         pady=(0, 12))

        theme_row = ctk.CTkFrame(bottom, fg_color="transparent")
        theme_row.pack(fill=tk.X)

        ctk.CTkLabel(theme_row, text="Theme",
                     font=(None, 9),
                     text_color=T("text_secondary")).pack(side=tk.LEFT)

        self._theme_switch = ctk.CTkSwitch(
            theme_row, text="",
            command=self._toggle_theme,
            width=46, height=22,
            switch_width=42, switch_height=22,
            progress_color=T("accent"),
            button_color=T("fg"),
            button_hover_color=T("accent_hover"),
            fg_color=T("filter_bg"),
        )
        self._theme_switch.pack(side=tk.RIGHT)

        self._refresh_profiles_list()

    # ── content area ───────────────────────────────────────────────────────────

    def _build_content(self):
        # tk.Frame hosts the starfield Canvas. bg gets refreshed on theme switch.
        self._content_wrap = tk.Frame(self._root, bg=DARK_THEME["bg"])
        self._content_wrap.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._tk_bg_widgets.append(self._content_wrap)

        self._stars = StarField(self._content_wrap,
                                 theme=DARK_THEME, num_stars=110, seed=7)
        self._stars.place(x=0, y=0, relwidth=1, relheight=1)

        cols_holder = tk.Frame(self._content_wrap, bg=DARK_THEME["bg"])
        cols_holder.place(x=18, y=18, relwidth=1, relheight=1,
                          width=-36, height=-36)
        cols_holder.lift()
        self._tk_bg_widgets.append(cols_holder)

        left_col = tk.Frame(cols_holder, bg=DARK_THEME["bg"])
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 9))
        self._tk_bg_widgets.append(left_col)
        self._left_col = left_col

        right_col = tk.Frame(cols_holder, bg=DARK_THEME["bg"])
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(9, 0))
        self._tk_bg_widgets.append(right_col)
        self._right_col = right_col

        self._build_wakeup_panel()
        self._build_activity_panel()

    # ── Wake Up card ───────────────────────────────────────────────────────────

    def _build_wakeup_panel(self):
        self._wu_card = ctk.CTkFrame(self._left_col,
                                      fg_color=T("card_bg"),
                                      corner_radius=22,
                                      border_width=1,
                                      border_color=T("card_border"))
        self._wu_card.pack(fill=tk.BOTH, expand=True)

        ctk.CTkFrame(self._wu_card, fg_color=T("accent"),
                      height=3, corner_radius=0).pack(fill=tk.X, padx=22)

        pad = ctk.CTkFrame(self._wu_card, fg_color="transparent")
        pad.pack(fill=tk.BOTH, expand=True, padx=28, pady=(20, 24))

        # Hero row
        hero = ctk.CTkFrame(pad, fg_color="transparent")
        hero.pack(fill=tk.X, pady=(0, 20))

        if self._hero_img:
            ctk.CTkLabel(hero, image=self._hero_img, text="").pack(
                side=tk.LEFT, padx=(0, 18))

        tcol = ctk.CTkFrame(hero, fg_color="transparent")
        tcol.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ctk.CTkLabel(tcol, text="Wake Up API",
                     font=(None, 26, "bold"),
                     text_color=T("fg")).pack(anchor="w")

        ctk.CTkLabel(tcol, text="Schedule HTTP requests your way",
                     font=(None, 10),
                     text_color=T("text_secondary")).pack(anchor="w",
                                                           pady=(3, 0))

        # Mode selector
        ctk.CTkLabel(pad, text="SEND MODE",
                     font=(None, 8, "bold"),
                     text_color=T("text_secondary"),
                     anchor="w").pack(fill=tk.X, pady=(0, 6))

        mode_row = ctk.CTkFrame(pad, fg_color="transparent")
        mode_row.pack(fill=tk.X, pady=(0, 18))
        for i, (icon, label, value) in enumerate(_MODES):
            mode_row.columnconfigure(i, weight=1)
            btn = ctk.CTkButton(
                mode_row, text=f"{icon}  {label}",
                command=lambda v=value: self._set_mode(v),
                font=(None, 11, "bold"),
                height=42, corner_radius=10,
                fg_color=T("filter_bg"),
                hover_color=T("border"),
                text_color=T("text_secondary"),
                border_width=1,
                border_color=T("input_border"),
            )
            btn.grid(row=0, column=i, padx=(0 if i == 0 else 6, 0), sticky="ew")
            self._mode_buttons[value] = btn

        # URL
        ctk.CTkLabel(pad, text="TARGET URL",
                     font=(None, 8, "bold"),
                     text_color=T("text_secondary"),
                     anchor="w").pack(fill=tk.X, pady=(0, 4))

        self._url_entry = ctk.CTkEntry(
            pad,
            placeholder_text="https://example.com/api/ping",
            fg_color=T("input_bg"),
            border_color=T("input_border"),
            text_color=T("fg"),
            placeholder_text_color=T("text_muted"),
            font=(None, 12), height=46, corner_radius=10, border_width=1,
        )
        self._url_entry.pack(fill=tk.X, pady=(0, 16))

        # Timing row (conditional based on mode)
        self._timing_holder = ctk.CTkFrame(pad, fg_color="transparent")
        self._timing_holder.pack(fill=tk.X, pady=(0, 16))

        self._mc_col = self._make_field("METHOD", combo=True)
        self._ic_col = self._make_field("EVERY (s)", placeholder="5")
        self._sc_col = self._make_field("UNTIL  HH:MM", placeholder="23:59")
        self._cc_col = self._make_field("COUNT (N)", placeholder="10")

        # Extras
        extras = ctk.CTkFrame(pad, fg_color="transparent")
        extras.pack(fill=tk.X, pady=(0, 20))

        self._headers_btn = ctk.CTkLabel(extras, text="✎  Headers",
                                          font=(None, 10),
                                          text_color=T("text_secondary"),
                                          cursor="hand2")
        self._headers_btn.pack(side=tk.LEFT, padx=(0, 20))
        self._headers_btn.bind("<Button-1>",
                                lambda _: self._open_headers_dialog())

        self._body_btn = ctk.CTkLabel(extras, text="✎  Body",
                                       font=(None, 10),
                                       text_color=T("text_secondary"),
                                       cursor="hand2")
        self._body_btn.pack(side=tk.LEFT)
        self._body_btn.bind("<Button-1>",
                             lambda _: self._open_body_dialog())

        # Wake button
        self._wake_btn = ctk.CTkButton(
            pad, text="▶   WAKE UP API",
            command=self._on_wake_click,
            fg_color=T("accent"), hover_color=T("accent_hover"),
            text_color=T("bg"), font=(None, 14, "bold"),
            height=54, corner_radius=14,
        )
        self._wake_btn.pack(fill=tk.X, pady=(0, 16))

        # Status row
        st_row = ctk.CTkFrame(pad, fg_color="transparent")
        st_row.pack(fill=tk.X, pady=(0, 10))

        self._wu_dot = AnimatedDot(st_row, color=DARK_THEME["text_muted"],
                                    size=10, bg=DARK_THEME["card_bg"])
        self._wu_dot.pack(side=tk.LEFT, padx=(0, 10))
        self._tk_card_bg_widgets.append(self._wu_dot)

        self._wu_status = ctk.CTkLabel(st_row, text="Ready to wake up an API.",
                                        font=(None, 10),
                                        text_color=T("text_secondary"))
        self._wu_status.pack(side=tk.LEFT)

        self._wu_bar = ctk.CTkProgressBar(pad,
                                           fg_color=T("filter_bg"),
                                           progress_color=T("accent"),
                                           height=6, corner_radius=3)
        self._wu_bar.pack(fill=tk.X)
        self._wu_bar.set(0)

    def _make_field(self, label, placeholder="", combo=False):
        """Build a labelled input column (frame containing label + input)."""
        col = ctk.CTkFrame(self._timing_holder, fg_color="transparent")
        ctk.CTkLabel(col, text=label, font=(None, 8, "bold"),
                     text_color=T("text_secondary"), anchor="w").pack(
            fill=tk.X, pady=(0, 4))
        if combo:
            self._method_var = tk.StringVar(value="GET")
            self._method_cb = ctk.CTkComboBox(
                col, variable=self._method_var, values=_METHODS,
                fg_color=T("input_bg"),
                border_color=T("input_border"),
                button_color=T("input_bg"),
                button_hover_color=T("card_border"),
                dropdown_fg_color=T("card_bg"),
                dropdown_hover_color=T("filter_bg"),
                text_color=T("fg"),
                font=(None, 11, "bold"),
                height=42, corner_radius=10, state="readonly",
            )
            self._method_cb.pack(fill=tk.X)
        else:
            entry = ctk.CTkEntry(
                col, placeholder_text=placeholder,
                fg_color=T("input_bg"), border_color=T("input_border"),
                text_color=T("fg"), placeholder_text_color=T("text_muted"),
                font=(None, 11), height=42, corner_radius=10, border_width=1,
            )
            entry.pack(fill=tk.X)
            col._entry = entry  # type: ignore
            if label == "EVERY (s)":
                self._interval_entry = entry
            elif label == "UNTIL  HH:MM":
                self._stop_entry = entry
            elif label == "COUNT (N)":
                self._count_entry = entry
        return col

    # ── Activity card ──────────────────────────────────────────────────────────

    def _build_activity_panel(self):
        self._act_card = ctk.CTkFrame(self._right_col,
                                       fg_color=T("card_bg"),
                                       corner_radius=22,
                                       border_width=1,
                                       border_color=T("card_border"))
        self._act_card.pack(fill=tk.BOTH, expand=True)

        ctk.CTkFrame(self._act_card, fg_color=T("success"),
                      height=3, corner_radius=0).pack(fill=tk.X, padx=22)

        wrap = ctk.CTkFrame(self._act_card, fg_color="transparent")
        wrap.pack(fill=tk.BOTH, expand=True, padx=22, pady=(20, 22))

        # Title row
        trow = ctk.CTkFrame(wrap, fg_color="transparent")
        trow.pack(fill=tk.X, pady=(0, 16))

        ctk.CTkLabel(trow, text="Activity",
                     font=(None, 22, "bold"),
                     text_color=T("fg")).pack(side=tk.LEFT)

        self._export_btn = ctk.CTkButton(
            trow, text="⬇ Export", command=self._export_log,
            fg_color=T("filter_bg"), hover_color=T("border"),
            text_color=T("text_secondary"), font=(None, 9, "bold"),
            width=84, height=30, corner_radius=8,
        )
        self._export_btn.pack(side=tk.RIGHT, padx=(6, 0))

        self._clear_btn = ctk.CTkButton(
            trow, text="🗑 Clear", command=self._on_clear,
            fg_color=T("filter_bg"), hover_color=T("border"),
            text_color=T("text_secondary"), font=(None, 9, "bold"),
            width=84, height=30, corner_radius=8,
        )
        self._clear_btn.pack(side=tk.RIGHT, padx=(6, 0))

        # Stats grid
        stats_frame = ctk.CTkFrame(wrap, fg_color="transparent")
        stats_frame.pack(fill=tk.X, pady=(0, 16))

        specs = [("🎯", "Total",   "—",   T("accent")),
                 ("✓",  "Success", "—%",  T("success")),
                 ("⏱",  "Avg",     "—ms", T("warning")),
                 ("📡", "Status",  "—",   T("text_secondary"))]
        self._stat_cards: list = []
        for i, (icon, lbl, val, col) in enumerate(specs):
            card = self._make_stat_card(stats_frame, icon, lbl, val, col)
            card["frame"].grid(row=0, column=i,
                               padx=(0 if i == 0 else 8, 0), sticky="nsew")
            stats_frame.columnconfigure(i, weight=1)
            self._stat_cards.append(card)

        # Filter pills
        frow = ctk.CTkFrame(wrap, fg_color="transparent")
        frow.pack(fill=tk.X, pady=(0, 12))
        for fname in ["ALL", "2xx", "3xx", "4xx", "5xx", "ERR"]:
            is_active = (fname == "ALL")
            btn = ctk.CTkButton(
                frow, text=fname,
                command=lambda f=fname: self._on_filter(f),
                fg_color=T("filter_act") if is_active else T("filter_bg"),
                hover_color=T("accent_hover") if is_active else T("border"),
                text_color=T("bg") if is_active else T("text_secondary"),
                font=(None, 9, "bold"),
                width=50, height=28, corner_radius=8,
            )
            btn.pack(side=tk.LEFT, padx=(0, 5))
            self._filter_btns[fname] = btn

        # Log textbox
        self._log = ctk.CTkTextbox(
            wrap,
            fg_color=T("log_bg"),
            text_color=T("fg"),
            font=("Courier", 10),
            corner_radius=12,
            border_width=1,
            border_color=T("card_border"),
            scrollbar_button_color=T("scroll_fg"),
            scrollbar_button_hover_color=T("accent"),
            state="disabled",
            wrap="word",
        )
        self._log.pack(fill=tk.BOTH, expand=True)

        self._refresh_log_tags()

    def _refresh_log_tags(self):
        tb = self._log._textbox
        theme = DARK_THEME if self._is_dark else LIGHT_THEME
        for tag in ("2xx", "3xx", "4xx", "5xx", "error",
                    "info", "ts", "method", "ms"):
            tb.tag_config(tag, foreground=theme[f"tag_{tag}"])

    def _make_stat_card(self, parent, icon, label, value, color) -> dict:
        frame = ctk.CTkFrame(parent, fg_color=T("input_bg"),
                              corner_radius=12, border_width=0)
        ctk.CTkFrame(frame, fg_color=color, height=3,
                     corner_radius=0).pack(fill=tk.X)
        body = ctk.CTkFrame(frame, fg_color="transparent")
        body.pack(fill=tk.X, padx=12, pady=10)

        head_row = ctk.CTkFrame(body, fg_color="transparent")
        head_row.pack(fill=tk.X)
        ctk.CTkLabel(head_row, text=icon, font=(None, 11),
                     text_color=color).pack(side=tk.LEFT, padx=(0, 6))
        ctk.CTkLabel(head_row, text=label, font=(None, 8, "bold"),
                     text_color=T("text_secondary")).pack(side=tk.LEFT)

        val_var = tk.StringVar(value=value)
        ctk.CTkLabel(body, textvariable=val_var,
                     font=(None, 22, "bold"),
                     text_color=color).pack(anchor="w", pady=(4, 0))
        return {"frame": frame, "val_var": val_var, "color": color}

    # ── Mode handling ──────────────────────────────────────────────────────────

    def _set_mode(self, mode: str):
        self._mode = mode
        self._update_mode_ui()

    def _update_mode_ui(self):
        # Update mode button styles
        for value, btn in self._mode_buttons.items():
            active = (value == self._mode)
            btn.configure(
                fg_color=T("accent") if active else T("filter_bg"),
                hover_color=T("accent_hover") if active else T("border"),
                text_color=T("bg") if active else T("text_secondary"),
                border_color=T("accent") if active else T("input_border"),
            )

        # Remove all timing columns from grid
        for col in (self._mc_col, self._ic_col, self._sc_col, self._cc_col):
            col.grid_forget()
        for c in range(4):
            self._timing_holder.columnconfigure(c, weight=0, minsize=0)

        # Always show method first
        self._timing_holder.columnconfigure(0, weight=2, minsize=110)

        if self._mode == MODE_SINGLE:
            self._mc_col.grid(row=0, column=0, sticky="ew")
        elif self._mode == MODE_COUNT:
            self._timing_holder.columnconfigure(1, weight=1, minsize=80)
            self._timing_holder.columnconfigure(2, weight=1, minsize=80)
            self._mc_col.grid(row=0, column=0, padx=(0, 8), sticky="ew")
            self._ic_col.grid(row=0, column=1, padx=(0, 8), sticky="ew")
            self._cc_col.grid(row=0, column=2, sticky="ew")
        else:  # continuous
            self._timing_holder.columnconfigure(1, weight=1, minsize=80)
            self._timing_holder.columnconfigure(2, weight=1, minsize=80)
            self._mc_col.grid(row=0, column=0, padx=(0, 8), sticky="ew")
            self._ic_col.grid(row=0, column=1, padx=(0, 8), sticky="ew")
            self._sc_col.grid(row=0, column=2, sticky="ew")

    # ── sidebar profiles ───────────────────────────────────────────────────────

    def _refresh_profiles_list(self):
        for w in self._profile_widgets:
            try:
                w.destroy()
            except Exception:
                pass
        self._profile_widgets = []

        names = get_profile_names()
        if not names:
            lbl = ctk.CTkLabel(
                self._prof_scroll,
                text="No profiles yet.\n\nConfigure a request\nand click  ＋ Save.",
                font=(None, 9), text_color=T("text_muted"),
                justify="center",
            )
            lbl.pack(fill=tk.X, padx=8, pady=20)
            self._profile_widgets.append(lbl)
            return

        for name in names:
            data = load_profile(name)
            item = self._build_profile_item(name, data)
            item.pack(fill=tk.X, pady=(0, 5), padx=2)
            self._profile_widgets.append(item)

    def _build_profile_item(self, name: str, data: dict) -> ctk.CTkFrame:
        outer = ctk.CTkFrame(self._prof_scroll, fg_color=T("card_bg"),
                              corner_radius=10, cursor="hand2",
                              border_width=1, border_color=T("card_border"))

        inner = ctk.CTkFrame(outer, fg_color="transparent")
        inner.pack(fill=tk.X, padx=12, pady=10)

        row1 = ctk.CTkFrame(inner, fg_color="transparent")
        row1.pack(fill=tk.X)

        play = ctk.CTkLabel(row1, text="▶", font=(None, 8),
                             text_color=T("accent"))
        play.pack(side=tk.LEFT, padx=(0, 6))

        nlbl = ctk.CTkLabel(row1, text=name, font=(None, 10, "bold"),
                             text_color=T("fg"))
        nlbl.pack(side=tk.LEFT)

        del_btn = ctk.CTkLabel(row1, text="✕", font=(None, 10),
                                text_color=T("text_muted"), cursor="hand2")
        del_btn.pack(side=tk.RIGHT)
        del_btn.bind("<Button-1>",
                     lambda _, n=name: self._delete_profile_by_name(n))

        method = data.get('method', 'GET')
        mode_lbl = {
            MODE_SINGLE: "once",
            MODE_COUNT: f"×{data.get('count', '?')}",
            MODE_CONTINUOUS: f"every {data.get('interval','?')}s",
        }.get(data.get("mode", MODE_CONTINUOUS),
              f"every {data.get('interval','?')}s")
        meta = ctk.CTkLabel(inner, text=f"{method} · {mode_lbl}",
                             font=(None, 8),
                             text_color=T("text_secondary"))
        meta.pack(anchor="w", pady=(2, 0))

        click_handler = lambda _, n=name: self._load_profile_by_name(n)
        for w in (outer, inner, row1, play, nlbl, meta):
            w.bind("<Button-1>", click_handler)

        def _enter(_):
            outer.configure(fg_color=T("filter_bg"))
        def _leave(_):
            outer.configure(fg_color=T("card_bg"))

        for w in (outer, inner, row1, play, nlbl, meta, del_btn):
            w.bind("<Enter>", _enter)
            w.bind("<Leave>", _leave)

        return outer

    def _load_profile_by_name(self, name: str):
        data = load_profile(name)
        if not data:
            return
        self._url_entry.delete(0, tk.END)
        self._url_entry.insert(0, data.get("url", ""))
        self._method_var.set(data.get("method", "GET"))
        self._method_cb.set(data.get("method", "GET"))
        self._interval_entry.delete(0, tk.END)
        self._interval_entry.insert(0, str(data.get("interval", "")))
        self._stop_entry.delete(0, tk.END)
        self._stop_entry.insert(0, data.get("stop", ""))
        self._count_entry.delete(0, tk.END)
        if data.get("count"):
            self._count_entry.insert(0, str(data.get("count")))
        mode = data.get("mode", MODE_CONTINUOUS)
        if mode in (MODE_SINGLE, MODE_COUNT, MODE_CONTINUOUS):
            self._set_mode(mode)
        self._stored_headers = data.get("headers", {})
        self._stored_body    = data.get("body", "")
        self._update_extra_indicators()

    def _delete_profile_by_name(self, name: str):
        if messagebox.askyesno("Delete Profile", f"Delete '{name}'?"):
            delete_profile(name)
            self._refresh_profiles_list()

    # ── dialogs ────────────────────────────────────────────────────────────────

    def _open_headers_dialog(self):
        dlg = ctk.CTkToplevel(self._root)
        dlg.title("HTTP Headers")
        dlg.geometry("560x460")
        dlg.configure(fg_color=T("bg"))
        dlg.transient(self._root)
        dlg.after(100, dlg.grab_set)

        ctk.CTkLabel(dlg, text="HTTP Headers",
                     font=(None, 16, "bold"),
                     text_color=T("fg")).pack(anchor="w", padx=22, pady=(20, 4))
        ctk.CTkLabel(dlg, text="Key / value pairs sent with every request.",
                     font=(None, 10),
                     text_color=T("text_secondary")).pack(anchor="w", padx=22)

        card = ctk.CTkFrame(dlg, fg_color=T("card_bg"), corner_radius=12,
                             border_width=1, border_color=T("card_border"))
        card.pack(fill=tk.BOTH, expand=True, padx=22, pady=14)
        ctk.CTkFrame(card, fg_color=T("accent"),
                      height=3, corner_radius=0).pack(fill=tk.X)

        body = ctk.CTkScrollableFrame(card, fg_color="transparent",
                                       corner_radius=0)
        body.pack(fill=tk.BOTH, expand=True, padx=14, pady=12)

        rows: list = []

        def add_row(key="", value=""):
            row = ctk.CTkFrame(body, fg_color="transparent")
            row.pack(fill=tk.X, pady=3)
            ke = ctk.CTkEntry(row, placeholder_text="Header",
                               fg_color=T("input_bg"),
                               border_color=T("input_border"),
                               text_color=T("fg"),
                               placeholder_text_color=T("text_muted"),
                               font=(None, 10),
                               height=34, corner_radius=8)
            ke.pack(side=tk.LEFT, padx=(0, 6), fill=tk.X, expand=True)
            if key:
                ke.insert(0, key)
            ve = ctk.CTkEntry(row, placeholder_text="Value",
                               fg_color=T("input_bg"),
                               border_color=T("input_border"),
                               text_color=T("fg"),
                               placeholder_text_color=T("text_muted"),
                               font=(None, 10),
                               height=34, corner_radius=8)
            ve.pack(side=tk.LEFT, padx=(0, 6), fill=tk.X, expand=True)
            if value:
                ve.insert(0, value)
            idx = len(rows)
            db = ctk.CTkButton(row, text="✕", width=30, height=30,
                                corner_radius=8,
                                fg_color=T("danger_bg"),
                                hover_color=T("danger"),
                                text_color=T("danger"),
                                font=(None, 10, "bold"),
                                command=lambda i=idx: _remove(i))
            db.pack(side=tk.LEFT)
            rows.append((ke, ve, db, row))

        def _remove(idx):
            if idx < len(rows) and rows[idx] is not None:
                rows[idx][3].destroy()
                rows[idx] = None

        for k, v in self._stored_headers.items():
            add_row(k, v)

        add_bar = ctk.CTkFrame(card, fg_color="transparent")
        add_bar.pack(fill=tk.X, padx=14, pady=(0, 10))
        ctk.CTkButton(add_bar, text="＋  Add Header", command=add_row,
                      fg_color=T("filter_bg"), hover_color=T("border"),
                      text_color=T("text_secondary"), font=(None, 10),
                      height=30, corner_radius=8).pack(anchor="w")

        btn_row = ctk.CTkFrame(dlg, fg_color="transparent")
        btn_row.pack(fill=tk.X, padx=22, pady=(0, 20))

        def _save():
            result = {}
            for item in rows:
                if item is None:
                    continue
                k = item[0].get().strip()
                v = item[1].get().strip()
                if k:
                    result[k] = v
            self._stored_headers = result
            self._update_extra_indicators()
            dlg.destroy()

        ctk.CTkButton(btn_row, text="Save", command=_save,
                      fg_color=T("accent"), hover_color=T("accent_hover"),
                      text_color=T("bg"), font=(None, 11, "bold"),
                      height=38, corner_radius=10).pack(side=tk.RIGHT)
        ctk.CTkButton(btn_row, text="Cancel", command=dlg.destroy,
                      fg_color=T("filter_bg"), hover_color=T("border"),
                      text_color=T("text_secondary"), font=(None, 11, "bold"),
                      height=38, corner_radius=10).pack(side=tk.RIGHT, padx=(0, 8))

    def _open_body_dialog(self):
        dlg = ctk.CTkToplevel(self._root)
        dlg.title("Request Body")
        dlg.geometry("560x460")
        dlg.configure(fg_color=T("bg"))
        dlg.transient(self._root)
        dlg.after(100, dlg.grab_set)

        ctk.CTkLabel(dlg, text="Request Body",
                     font=(None, 16, "bold"),
                     text_color=T("fg")).pack(anchor="w", padx=22, pady=(20, 4))
        ctk.CTkLabel(dlg, text="Sent only with POST / PUT / PATCH.",
                     font=(None, 10),
                     text_color=T("text_secondary")).pack(anchor="w", padx=22)

        card = ctk.CTkFrame(dlg, fg_color=T("card_bg"), corner_radius=12,
                             border_width=1, border_color=T("card_border"))
        card.pack(fill=tk.BOTH, expand=True, padx=22, pady=14)
        ctk.CTkFrame(card, fg_color=T("accent"),
                      height=3, corner_radius=0).pack(fill=tk.X)

        text = ctk.CTkTextbox(card, fg_color=T("input_bg"),
                               text_color=T("fg"), font=("Courier", 11),
                               corner_radius=0, border_width=0)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        if self._stored_body:
            text.insert("1.0", self._stored_body)

        btn_row = ctk.CTkFrame(dlg, fg_color="transparent")
        btn_row.pack(fill=tk.X, padx=22, pady=(0, 20))

        def _save():
            self._stored_body = text.get("1.0", tk.END).strip()
            self._update_extra_indicators()
            dlg.destroy()

        ctk.CTkButton(btn_row, text="Save", command=_save,
                      fg_color=T("accent"), hover_color=T("accent_hover"),
                      text_color=T("bg"), font=(None, 11, "bold"),
                      height=38, corner_radius=10).pack(side=tk.RIGHT)
        ctk.CTkButton(btn_row, text="Cancel", command=dlg.destroy,
                      fg_color=T("filter_bg"), hover_color=T("border"),
                      text_color=T("text_secondary"), font=(None, 11, "bold"),
                      height=38, corner_radius=10).pack(side=tk.RIGHT, padx=(0, 8))

    def _update_extra_indicators(self):
        has_h = bool(self._stored_headers)
        has_b = bool(self._stored_body)
        self._headers_btn.configure(
            text=f"✎  Headers · {len(self._stored_headers)}" if has_h else "✎  Headers",
            text_color=T("accent") if has_h else T("text_secondary"))
        self._body_btn.configure(
            text="✎  Body · set" if has_b else "✎  Body",
            text_color=T("accent") if has_b else T("text_secondary"))

    # ── theme ──────────────────────────────────────────────────────────────────

    def _toggle_theme(self):
        self._is_dark = not self._is_dark
        ctk.set_appearance_mode("dark" if self._is_dark else "light")
        theme = DARK_THEME if self._is_dark else LIGHT_THEME

        for w in self._tk_bg_widgets:
            try:
                w.configure(bg=theme["bg"])
            except Exception:
                pass
        self._stars.apply_theme(theme)
        for w in self._tk_card_bg_widgets:
            try:
                w.set_bg(theme["card_bg"])
            except Exception:
                pass

        self._refresh_log_tags()

    # ── scheduler wiring ───────────────────────────────────────────────────────

    def _wire_scheduler(self):
        sch = self._scheduler
        (sch
         .on("response",         self._on_response)
         .on("req_error",        self._on_req_error)
         .on("countdown",        self._on_countdown)
         .on("sent",             self._on_sent)
         .on("completed",        self._on_completed)
         .on("completed_count",  self._on_completed_count)
         .on("completed_single", self._on_completed_single)
         .on("finished",         self._on_finished)
         .on("error_event",      self._on_error_event))

    def _safe(self, fn, *a, **kw):
        self._root.after(0, lambda: fn(*a, **kw))

    def _on_response(self, d):           self._safe(self._handle_response, d)
    def _on_req_error(self, d):          self._safe(self._handle_req_error, d)
    def _on_countdown(self, r, t):       self._safe(self._handle_countdown, r, t)
    def _on_sent(self, n, tg):           self._safe(self._handle_sent, n, tg)
    def _on_completed(self, st):         self._safe(self._handle_completed, st)
    def _on_completed_count(self, n):    self._safe(self._handle_completed_count, n)
    def _on_completed_single(self):      self._safe(self._handle_completed_single)
    def _on_finished(self):              self._safe(self._handle_finished)
    def _on_error_event(self, m):        self._safe(self._handle_error_event, m)

    # ── UI-thread handlers ─────────────────────────────────────────────────────

    def _handle_response(self, data: dict):
        code = data["status"]
        ts   = data["timestamp"]
        cnt  = data["count"]
        ms   = data["elapsed_ms"]
        meth = data["method"]
        if code < 300:   tag = "2xx"
        elif code < 400: tag = "3xx"
        elif code < 500: tag = "4xx"
        else:            tag = "5xx"
        line = f"[{ts}]  #{cnt:>4}  {meth:<7}  {code}  {ms:>8.1f}ms"
        if self._matches_filter(tag):
            self._append_log(line, tag)
        self._update_stats()

    def _handle_req_error(self, data: dict):
        ts  = data["timestamp"]
        cnt = data["count"]
        err = data["error"]
        ms  = data["elapsed_ms"]
        line = f"[{ts}]  #{cnt:>4}  ERROR    —  {ms:>8.1f}ms  {err}"
        if self._matches_filter("error"):
            self._append_log(line, "error")
        self._update_stats()

    def _handle_countdown(self, remaining: int, total: int):
        self._wu_bar.set(remaining / total)
        if self._mode == MODE_COUNT:
            self._wu_status.configure(
                text=f"Sent {self._scheduler.sent_count} of "
                     f"{self._scheduler.target_count} · next in {remaining}s…",
                text_color=T("text_secondary"))
        else:
            self._wu_status.configure(
                text=f"Next request in {remaining}s…",
                text_color=T("text_secondary"))

    def _handle_sent(self, n: int, target):
        if target is not None:
            self._wu_status.configure(
                text=f"Sent {n} of {target}…",
                text_color=T("success"))

    def _handle_completed(self, stop_time):
        self._wu_status.configure(
            text=f"Completed at {stop_time.strftime('%H:%M')}",
            text_color=T("success"))
        self._wu_dot.set_color(
            DARK_THEME["success"] if self._is_dark else LIGHT_THEME["success"])
        self._wu_bar.set(0)

    def _handle_completed_count(self, n: int):
        self._wu_status.configure(text=f"Completed — sent {n} requests",
                                   text_color=T("success"))
        self._wu_bar.set(1.0)

    def _handle_completed_single(self):
        self._wu_status.configure(text="Sent.", text_color=T("success"))
        self._wu_bar.set(1.0)

    def _handle_finished(self):
        self._set_running(False)
        self._wu_dot.stop()
        if "Running" in (self._wu_status.cget("text") or ""):
            self._wu_status.configure(text="Stopped",
                                       text_color=T("danger"))

    def _handle_error_event(self, msg: str):
        self._wu_status.configure(text=f"Error: {msg}",
                                   text_color=T("danger"))

    # ── log helpers ────────────────────────────────────────────────────────────

    def _matches_filter(self, tag: str) -> bool:
        f = self._log_filter
        if f == "ALL":   return True
        if f == "ERR":   return tag == "error"
        return tag == f

    def _append_log(self, line: str, tag: str):
        self._log.configure(state="normal")
        self._log._textbox.insert(tk.END, line + "\n", tag)
        self._log._textbox.see(tk.END)
        self._log.configure(state="disabled")

    def _update_stats(self):
        s = self._scheduler.stats
        self._stat_cards[0]["val_var"].set(str(s["total"]))
        self._stat_cards[1]["val_var"].set(f"{s['success_pct']:.1f}%")
        self._stat_cards[2]["val_var"].set(f"{s['avg_ms']:.0f}ms")
        st = s["last_status"]
        self._stat_cards[3]["val_var"].set(str(st) if st else "—")

    # ── actions ────────────────────────────────────────────────────────────────

    def _set_running(self, running: bool):
        self._is_running = running
        if running:
            self._wake_btn.configure(text="⏹  STOP",
                                      fg_color=T("danger"),
                                      hover_color=T("danger_hover"),
                                      text_color=("white", "white"))
        else:
            self._wake_btn.configure(text="▶   WAKE UP API",
                                      fg_color=T("accent"),
                                      hover_color=T("accent_hover"),
                                      text_color=T("bg"))

    def _on_wake_click(self):
        if self._is_running:
            self._on_stop()
        else:
            self._on_start()

    def _on_start(self):
        url = self._url_entry.get().strip()
        if not url:
            messagebox.showerror("おはよう", "Please enter a URL.")
            return

        method  = self._method_var.get()
        headers = self._stored_headers
        body    = self._stored_body if method in ("POST", "PUT", "PATCH") else ""

        interval = 0
        stop_time = None
        count = 1

        if self._mode in (MODE_COUNT, MODE_CONTINUOUS):
            int_str = self._interval_entry.get().strip()
            if not int_str:
                messagebox.showerror("おはよう",
                                     "Please enter an interval (seconds).")
                return
            try:
                interval = int(int_str)
                if interval <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("おはよう",
                                     "Interval must be a positive integer.")
                return

        if self._mode == MODE_CONTINUOUS:
            stop_str = self._stop_entry.get().strip()
            if not stop_str:
                messagebox.showerror("おはよう",
                                     "Please enter a stop time (HH:MM).")
                return
            try:
                stop_time = datetime.strptime(stop_str, "%H:%M").time()
            except ValueError:
                messagebox.showerror("おはよう",
                                     "Stop time must be HH:MM (24-hour).")
                return

        if self._mode == MODE_COUNT:
            cnt_str = self._count_entry.get().strip()
            if not cnt_str:
                messagebox.showerror("おはよう", "Please enter a count (N).")
                return
            try:
                count = int(cnt_str)
                if count <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("おはよう",
                                     "Count must be a positive integer.")
                return

        self._set_running(True)
        self._wu_status.configure(text="Running…", text_color=T("success"))
        self._wu_dot.set_color(
            DARK_THEME["success"] if self._is_dark else LIGHT_THEME["success"])
        self._wu_dot.start()
        self._wu_bar.set(1.0)

        self._scheduler.start(url, method, headers, body,
                               interval=interval, stop_time=stop_time,
                               mode=self._mode, count=count)

    def _on_stop(self):
        self._scheduler.stop()
        self._wu_status.configure(text="Stopped", text_color=T("danger"))
        self._wu_dot.set_color(
            DARK_THEME["danger"] if self._is_dark else LIGHT_THEME["danger"])
        self._wu_dot.stop()
        self._wu_bar.set(0)

    def _on_clear(self):
        self._log.configure(state="normal")
        self._log.delete("1.0", tk.END)
        self._log.configure(state="disabled")
        self._scheduler.reset_stats()
        defaults = ["—", "—%", "—ms", "—"]
        for card, val in zip(self._stat_cards, defaults):
            card["val_var"].set(val)

    def _on_filter(self, fname: str):
        self._log_filter = fname
        for f, btn in self._filter_btns.items():
            is_active = (f == fname)
            btn.configure(
                fg_color=T("filter_act") if is_active else T("filter_bg"),
                hover_color=T("accent_hover") if is_active else T("border"),
                text_color=T("bg") if is_active else T("text_secondary"))

    def _export_log(self):
        content = self._log.get("1.0", tk.END).strip()
        if not content:
            messagebox.showinfo("おはよう", "Log is empty — nothing to export.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text file", "*.txt"), ("CSV", "*.csv"), ("All", "*.*")],
            title="Export Request Log")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("おはよう", f"Exported to:\n{path}")

    def _save_profile(self):
        name = simpledialog.askstring("Save Profile", "Profile name:",
                                      parent=self._root)
        if not name:
            return
        data = {
            "url":      self._url_entry.get(),
            "method":   self._method_var.get(),
            "interval": self._interval_entry.get(),
            "stop":     self._stop_entry.get(),
            "count":    self._count_entry.get(),
            "mode":     self._mode,
            "headers":  self._stored_headers,
            "body":     self._stored_body,
        }
        save_profile(name, data)
        self._refresh_profiles_list()

    # ── run ────────────────────────────────────────────────────────────────────

    def run(self):
        self._root.mainloop()


def run_app():
    app = MainWindow()
    app.run()
