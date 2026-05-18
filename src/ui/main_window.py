"""ui/main_window.py — Ohayo · Postman-style UI · dark sky / light sun themes."""

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

_METHODS  = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]
_ICON_PATH = os.path.join(os.path.dirname(__file__),
                           "..", "..", "images", "icon.png")

MODE_SINGLE     = "single"
MODE_COUNT      = "count"
MODE_CONTINUOUS = "continuous"


# ── helpers ────────────────────────────────────────────────────────────────────

def _card(parent, **kw) -> ctk.CTkFrame:
    return ctk.CTkFrame(parent,
                        fg_color=T("card_bg"),
                        corner_radius=14,
                        border_width=1,
                        border_color=T("card_border"),
                        **kw)

def _sep(parent, color_key="border", padx=0, pady=0):
    ctk.CTkFrame(parent, height=1, fg_color=T(color_key),
                 corner_radius=0).pack(fill=tk.X, padx=padx, pady=pady)


# ─────────────────────────────────────────────────────────────────────────────

class MainWindow:
    def __init__(self):
        self._is_dark  = True
        self._scheduler = Scheduler()
        self._log_filter = "ALL"
        self._is_running = False
        self._stored_headers: dict = {}
        self._stored_body: str = ""
        self._profile_widgets: list = []
        self._mode = MODE_CONTINUOUS
        self._mode_btns: dict = {}
        self._filter_btns: dict = {}
        self._active_tab = "mode"
        self._tab_btns: dict = {}
        self._tab_frames: dict = {}
        self._tk_bg: list = []          # raw tk widgets needing manual bg update
        self._stat_cards: list = []
        self._app_icon = None
        self._sb_icon  = None

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self._root = ctk.CTk()
        self._setup_window()
        self._load_images()
        self._build_ui()
        self._wire_scheduler()
        self._set_tab("mode")
        self._update_mode_fields()

    # ── bootstrap ──────────────────────────────────────────────────────────────

    def _setup_window(self):
        r = self._root
        r.title("おはよう — API Waker")
        r.geometry("1300x820")
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
            self._app_icon = ctk.CTkImage(light_image=pil, dark_image=pil,
                                           size=(72, 72))
            self._sb_icon  = ctk.CTkImage(light_image=pil, dark_image=pil,
                                           size=(36, 36))
        except Exception:
            pass

    def _build_ui(self):
        self._build_sidebar()
        self._build_main()

    # ── sidebar ────────────────────────────────────────────────────────────────

    def _build_sidebar(self):
        sb = ctk.CTkFrame(self._root, width=230,
                          fg_color=T("sidebar_bg"), corner_radius=0)
        sb.pack(side=tk.LEFT, fill=tk.Y)
        sb.pack_propagate(False)
        self._sidebar = sb

        # vertical separator
        ctk.CTkFrame(self._root, width=1,
                     fg_color=T("border"), corner_radius=0).pack(
            side=tk.LEFT, fill=tk.Y)

        # brand
        brand = ctk.CTkFrame(sb, fg_color="transparent")
        brand.pack(fill=tk.X, padx=20, pady=(22, 14))

        if self._sb_icon:
            ctk.CTkLabel(brand, image=self._sb_icon, text="").pack(
                anchor="w", pady=(0, 10))

        ctk.CTkLabel(brand, text="おはよう",
                     font=(None, 22, "bold"),
                     text_color=T("accent")).pack(anchor="w")
        ctk.CTkLabel(brand, text="API Waker  ·  v2",
                     font=(None, 9),
                     text_color=T("text_secondary")).pack(anchor="w", pady=(2, 0))

        _sep(sb, padx=16, pady=(10, 14))

        # profiles header
        hrow = ctk.CTkFrame(sb, fg_color="transparent")
        hrow.pack(fill=tk.X, padx=20, pady=(0, 8))
        ctk.CTkLabel(hrow, text="COLLECTIONS",
                     font=(None, 8, "bold"),
                     text_color=T("text_muted")).pack(side=tk.LEFT)

        # scrollable list
        self._prof_scroll = ctk.CTkScrollableFrame(
            sb, fg_color="transparent",
            scrollbar_fg_color=T("sidebar_bg"),
            scrollbar_button_color=T("scroll_fg"),
            scrollbar_button_hover_color=T("accent"),
            corner_radius=0)
        self._prof_scroll.pack(fill=tk.BOTH, expand=True, padx=8)

        # bottom
        _sep(sb, padx=16, pady=(4, 0))
        bot = ctk.CTkFrame(sb, fg_color="transparent")
        bot.pack(fill=tk.X, padx=18, pady=14, side=tk.BOTTOM)

        ctk.CTkButton(bot, text="＋  Save Current",
                      command=self._save_profile,
                      fg_color=T("filter_bg"),
                      hover_color=T("card_border"),
                      text_color=T("text_secondary"),
                      font=(None, 10, "bold"),
                      height=34, corner_radius=8).pack(fill=tk.X, pady=(0, 10))

        trow = ctk.CTkFrame(bot, fg_color="transparent")
        trow.pack(fill=tk.X)
        ctk.CTkLabel(trow, text="Dark Mode", font=(None, 9),
                     text_color=T("text_secondary")).pack(side=tk.LEFT)
        self._theme_sw = ctk.CTkSwitch(
            trow, text="",
            command=self._toggle_theme,
            width=42, height=22, switch_width=38, switch_height=22,
            progress_color=T("accent"),
            button_color=T("fg"),
            button_hover_color=T("accent_hover"),
            fg_color=T("filter_bg"))
        self._theme_sw.select()
        self._theme_sw.pack(side=tk.RIGHT)

        self._refresh_profiles_list()

    # ── main area ──────────────────────────────────────────────────────────────

    def _build_main(self):
        # outer raw tk.Frame holds the starfield canvas
        wrap = tk.Frame(self._root, bg=DARK_THEME["bg"])
        wrap.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._content_wrap = wrap
        self._tk_bg.append(wrap)

        # starfield (behind everything)
        self._stars = StarField(wrap, theme=DARK_THEME, num_stars=120, seed=13)
        self._stars.place(x=0, y=0, relwidth=1, relheight=1)

        # content column floats over the starfield
        col = tk.Frame(wrap, bg=DARK_THEME["bg"])
        col.place(x=16, y=14, relwidth=1, relheight=1, width=-32, height=-28)
        col.lift()
        self._tk_bg.append(col)
        self._main_col = col

        self._build_topbar(col)
        self._build_request_bar(col)
        self._build_tab_area(col)
        self._build_log_panel(col)

    # ── topbar ─────────────────────────────────────────────────────────────────

    def _build_topbar(self, parent):
        bar = ctk.CTkFrame(parent, fg_color="transparent", height=42)
        bar.pack(fill=tk.X, pady=(0, 10))
        bar.pack_propagate(False)

        ctk.CTkLabel(bar, text="Wake Up API",
                     font=(None, 20, "bold"),
                     text_color=T("fg")).pack(side=tk.LEFT, padx=4)
        ctk.CTkLabel(bar, text="Schedule HTTP requests",
                     font=(None, 10),
                     text_color=T("text_secondary")).pack(
            side=tk.LEFT, padx=(10, 0), pady=(4, 0))

    # ── request bar (Postman-style: method + url + send) ──────────────────────

    def _build_request_bar(self, parent):
        card = _card(parent)
        card.pack(fill=tk.X, pady=(0, 10))

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill=tk.X, padx=14, pady=12)

        # HTTP method
        self._method_var = tk.StringVar(value="GET")
        self._method_cb = ctk.CTkComboBox(
            row, variable=self._method_var, values=_METHODS,
            fg_color=T("input_bg"),
            border_color=T("input_border"),
            button_color=T("input_bg"),
            button_hover_color=T("card_border"),
            dropdown_fg_color=T("card_bg"),
            dropdown_hover_color=T("filter_bg"),
            text_color=T("accent"),
            font=(None, 12, "bold"),
            width=110, height=44, corner_radius=10, state="readonly")
        self._method_cb.pack(side=tk.LEFT, padx=(0, 8))

        # URL
        self._url_entry = ctk.CTkEntry(
            row,
            placeholder_text="https://api.example.com/ping",
            fg_color=T("input_bg"),
            border_color=T("input_border"),
            text_color=T("fg"),
            placeholder_text_color=T("text_muted"),
            font=(None, 12), height=44, corner_radius=10, border_width=1)
        self._url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        # Status dot
        self._wu_dot = AnimatedDot(row, color=DARK_THEME["text_muted"],
                                   size=10, bg=DARK_THEME["card_bg"])
        self._wu_dot.pack(side=tk.LEFT, padx=(0, 6))

        # Send / Stop button
        self._wake_btn = ctk.CTkButton(
            row, text="  Send",
            command=self._on_wake_click,
            fg_color=T("accent"), hover_color=T("accent_hover"),
            text_color=T("bg"), font=(None, 13, "bold"),
            width=110, height=44, corner_radius=10)
        self._wake_btn.pack(side=tk.LEFT)

    # ── tab area ───────────────────────────────────────────────────────────────

    def _build_tab_area(self, parent):
        card = _card(parent)
        card.pack(fill=tk.X, pady=(0, 10))
        self._tab_card = card

        # tab buttons row
        tab_bar = ctk.CTkFrame(card, fg_color="transparent")
        tab_bar.pack(fill=tk.X, padx=14, pady=(10, 0))

        tabs = [
            ("mode",    "⚡  Send Mode"),
            ("headers", "≡  Headers"),
            ("body",    "{ }  Body"),
        ]
        for key, label in tabs:
            btn = ctk.CTkButton(
                tab_bar, text=label,
                command=lambda k=key: self._set_tab(k),
                font=(None, 10, "bold"),
                height=32, corner_radius=8,
                fg_color="transparent",
                hover_color=T("filter_bg"),
                text_color=T("text_secondary"),
                border_width=0, width=0)
            btn.pack(side=tk.LEFT, padx=(0, 4))
            self._tab_btns[key] = btn

        _sep(card, padx=14, pady=(8, 0))

        # tab content frames (only one visible at a time)
        self._tab_body = ctk.CTkFrame(card, fg_color="transparent")
        self._tab_body.pack(fill=tk.BOTH, padx=14, pady=(0, 14))

        self._tab_frames["mode"]    = self._build_tab_mode(self._tab_body)
        self._tab_frames["headers"] = self._build_tab_headers(self._tab_body)
        self._tab_frames["body"]    = self._build_tab_body_content(self._tab_body)

    def _set_tab(self, key: str):
        self._active_tab = key
        for k, f in self._tab_frames.items():
            if k == key:
                f.pack(fill=tk.BOTH, expand=True)
            else:
                f.pack_forget()
        for k, btn in self._tab_btns.items():
            active = (k == key)
            btn.configure(
                fg_color=T("filter_bg") if active else "transparent",
                text_color=T("accent") if active else T("text_secondary"))

    # ── tab: Send Mode ─────────────────────────────────────────────────────────

    def _build_tab_mode(self, parent) -> ctk.CTkFrame:
        f = ctk.CTkFrame(parent, fg_color="transparent")

        # mode pill row
        pill_row = ctk.CTkFrame(f, fg_color="transparent")
        pill_row.pack(fill=tk.X, pady=(12, 10))

        modes = [
            (MODE_SINGLE,     "⚡  Once",        "Fire a single request"),
            (MODE_COUNT,      "🔁  Repeat N",     "Send N times with interval"),
            (MODE_CONTINUOUS, "♾  Continuous",   "Send until stop time"),
        ]
        for i, (value, label, tip) in enumerate(modes):
            col = ctk.CTkFrame(pill_row, fg_color="transparent")
            col.grid(row=0, column=i, padx=(0 if i == 0 else 8, 0), sticky="ew")
            pill_row.columnconfigure(i, weight=1)

            btn = ctk.CTkButton(
                col, text=label,
                command=lambda v=value: self._set_mode(v),
                font=(None, 11, "bold"),
                height=44, corner_radius=10,
                fg_color=T("filter_bg"),
                hover_color=T("border"),
                text_color=T("text_secondary"),
                border_width=1,
                border_color=T("input_border"))
            btn.pack(fill=tk.X)
            ctk.CTkLabel(col, text=tip, font=(None, 8),
                         text_color=T("text_muted")).pack(pady=(3, 0))
            self._mode_btns[value] = btn

        # fields row (interval / count / stop — shown based on mode)
        self._mode_fields_row = ctk.CTkFrame(f, fg_color="transparent")
        self._mode_fields_row.pack(fill=tk.X, pady=(0, 6))

        # interval entry
        self._f_interval = self.__field_col(
            self._mode_fields_row, "EVERY (s)", "5", column=0)
        # count entry
        self._f_count = self.__field_col(
            self._mode_fields_row, "COUNT (N)", "10", column=1)
        # stop time entry
        self._f_stop = self.__field_col(
            self._mode_fields_row, "UNTIL  HH:MM", "23:59", column=2)

        return f

    def __field_col(self, parent, label, placeholder, column):
        col = ctk.CTkFrame(parent, fg_color="transparent")
        col.grid(row=0, column=column, padx=(0 if column == 0 else 10, 0),
                 sticky="ew")
        parent.columnconfigure(column, weight=1)
        ctk.CTkLabel(col, text=label, font=(None, 8, "bold"),
                     text_color=T("text_secondary"), anchor="w").pack(
            fill=tk.X, pady=(0, 4))
        entry = ctk.CTkEntry(
            col, placeholder_text=placeholder,
            fg_color=T("input_bg"), border_color=T("input_border"),
            text_color=T("fg"), placeholder_text_color=T("text_muted"),
            font=(None, 11), height=38, corner_radius=8, border_width=1)
        entry.pack(fill=tk.X)
        return col

    def _get_entry_in_col(self, col_frame) -> ctk.CTkEntry:
        for child in col_frame.winfo_children():
            if isinstance(child, ctk.CTkEntry):
                return child
        return None

    # ── tab: Headers ───────────────────────────────────────────────────────────

    def _build_tab_headers(self, parent) -> ctk.CTkFrame:
        f = ctk.CTkFrame(parent, fg_color="transparent")

        scroll = ctk.CTkScrollableFrame(f, fg_color="transparent",
                                        height=110, corner_radius=0)
        scroll.pack(fill=tk.X, pady=(10, 0))
        self._hdr_scroll = scroll
        self._hdr_rows: list = []

        def _add_row(key="", val=""):
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill=tk.X, pady=3)
            ke = ctk.CTkEntry(row, placeholder_text="Header",
                               fg_color=T("input_bg"),
                               border_color=T("input_border"),
                               text_color=T("fg"),
                               placeholder_text_color=T("text_muted"),
                               height=32, corner_radius=8)
            ke.pack(side=tk.LEFT, padx=(0, 6), fill=tk.X, expand=True)
            if key: ke.insert(0, key)
            ve = ctk.CTkEntry(row, placeholder_text="Value",
                               fg_color=T("input_bg"),
                               border_color=T("input_border"),
                               text_color=T("fg"),
                               placeholder_text_color=T("text_muted"),
                               height=32, corner_radius=8)
            ve.pack(side=tk.LEFT, padx=(0, 6), fill=tk.X, expand=True)
            if val: ve.insert(0, val)
            idx = len(self._hdr_rows)
            rb = ctk.CTkButton(row, text="✕", width=28, height=28,
                                corner_radius=6,
                                fg_color=T("danger_bg"),
                                hover_color=T("danger"),
                                text_color=T("danger"),
                                font=(None, 9, "bold"),
                                command=lambda i=idx: _del(i))
            rb.pack(side=tk.LEFT)
            self._hdr_rows.append((ke, ve, rb, row))

        def _del(idx):
            if idx < len(self._hdr_rows) and self._hdr_rows[idx]:
                self._hdr_rows[idx][3].destroy()
                self._hdr_rows[idx] = None
            self._sync_headers()

        self._hdr_add_row = _add_row

        bot = ctk.CTkFrame(f, fg_color="transparent")
        bot.pack(fill=tk.X, pady=(6, 4))
        ctk.CTkButton(bot, text="＋  Add Header",
                      command=_add_row,
                      fg_color=T("filter_bg"), hover_color=T("border"),
                      text_color=T("text_secondary"), font=(None, 9),
                      height=28, corner_radius=8).pack(side=tk.LEFT)
        self._hdr_count_lbl = ctk.CTkLabel(bot, text="",
                                            font=(None, 9),
                                            text_color=T("accent"))
        self._hdr_count_lbl.pack(side=tk.LEFT, padx=(10, 0))

        return f

    def _sync_headers(self):
        result = {}
        for item in self._hdr_rows:
            if item is None:
                continue
            k = item[0].get().strip()
            v = item[1].get().strip()
            if k:
                result[k] = v
        self._stored_headers = result
        n = len(result)
        self._hdr_count_lbl.configure(
            text=f"{n} header{'s' if n != 1 else ''}" if n else "")

    # ── tab: Body ──────────────────────────────────────────────────────────────

    def _build_tab_body_content(self, parent) -> ctk.CTkFrame:
        f = ctk.CTkFrame(parent, fg_color="transparent")

        self._body_box = ctk.CTkTextbox(
            f, fg_color=T("input_bg"), text_color=T("fg"),
            font=("Courier", 11), corner_radius=10, border_width=1,
            border_color=T("input_border"),
            scrollbar_button_color=T("scroll_fg"),
            scrollbar_button_hover_color=T("accent"),
            height=120, wrap="none")
        self._body_box.pack(fill=tk.BOTH, expand=True, pady=(10, 4))

        note = ctk.CTkLabel(f, text="Sent only with POST · PUT · PATCH",
                             font=(None, 8), text_color=T("text_muted"))
        note.pack(anchor="w")
        return f

    # ── log panel ──────────────────────────────────────────────────────────────

    def _build_log_panel(self, parent):
        card = _card(parent)
        card.pack(fill=tk.BOTH, expand=True, pady=(0, 4))

        # coloured top stripe
        ctk.CTkFrame(card, fg_color=T("success"),
                     height=3, corner_radius=0).pack(fill=tk.X)

        wrap = ctk.CTkFrame(card, fg_color="transparent")
        wrap.pack(fill=tk.BOTH, expand=True, padx=18, pady=(12, 16))

        # ── header row
        hrow = ctk.CTkFrame(wrap, fg_color="transparent")
        hrow.pack(fill=tk.X, pady=(0, 10))

        ctk.CTkLabel(hrow, text="Response Log",
                     font=(None, 16, "bold"),
                     text_color=T("fg")).pack(side=tk.LEFT)

        # status dot + text (right of title)
        self._status_lbl = ctk.CTkLabel(hrow, text="Ready",
                                         font=(None, 9),
                                         text_color=T("text_muted"))
        self._status_lbl.pack(side=tk.LEFT, padx=(14, 0), pady=(3, 0))

        for txt, cmd in [("⬇ Export", self._export_log),
                          ("🗑 Clear",  self._on_clear)]:
            ctk.CTkButton(hrow, text=txt, command=cmd,
                          fg_color=T("filter_bg"), hover_color=T("border"),
                          text_color=T("text_secondary"),
                          font=(None, 9, "bold"),
                          width=78, height=28, corner_radius=8).pack(
                side=tk.RIGHT, padx=(5, 0))

        # ── stats row
        stats = ctk.CTkFrame(wrap, fg_color="transparent")
        stats.pack(fill=tk.X, pady=(0, 10))

        specs = [
            ("Total",   "—",    T("accent")),
            ("Success", "—%",   T("success")),
            ("Avg ms",  "—ms",  T("warning")),
            ("Status",  "—",    T("text_secondary")),
        ]
        for i, (lbl, val, col) in enumerate(specs):
            sc = self._make_stat_chip(stats, lbl, val, col)
            sc.grid(row=0, column=i, padx=(0 if i == 0 else 8, 0), sticky="ew")
            stats.columnconfigure(i, weight=1)
            self._stat_cards.append({"widget": sc,
                                      "val_var": sc._val_var,
                                      "color": col})

        # ── progress bar
        self._wu_bar = ctk.CTkProgressBar(wrap,
                                           fg_color=T("filter_bg"),
                                           progress_color=T("accent"),
                                           height=4, corner_radius=2)
        self._wu_bar.pack(fill=tk.X, pady=(0, 8))
        self._wu_bar.set(0)

        # ── filter pills
        frow = ctk.CTkFrame(wrap, fg_color="transparent")
        frow.pack(fill=tk.X, pady=(0, 8))
        for fname in ["ALL", "2xx", "3xx", "4xx", "5xx", "ERR"]:
            active = (fname == "ALL")
            btn = ctk.CTkButton(
                frow, text=fname,
                command=lambda f=fname: self._on_filter(f),
                fg_color=T("filter_act") if active else T("filter_bg"),
                hover_color=T("accent_hover") if active else T("border"),
                text_color=T("bg") if active else T("text_secondary"),
                font=(None, 8, "bold"),
                width=46, height=26, corner_radius=7)
            btn.pack(side=tk.LEFT, padx=(0, 4))
            self._filter_btns[fname] = btn

        # ── log textbox
        self._log = ctk.CTkTextbox(
            wrap, fg_color=T("log_bg"),
            text_color=T("fg"), font=("Courier", 10),
            corner_radius=10, border_width=1,
            border_color=T("card_border"),
            scrollbar_button_color=T("scroll_fg"),
            scrollbar_button_hover_color=T("accent"),
            state="disabled", wrap="none")
        self._log.pack(fill=tk.BOTH, expand=True)
        self._refresh_log_tags()

    def _make_stat_chip(self, parent, label: str, val: str,
                         color) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(parent, fg_color=T("input_bg"),
                              corner_radius=10)
        frame._val_var = tk.StringVar(value=val)
        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.pack(padx=12, pady=8)
        ctk.CTkLabel(inner, text=label, font=(None, 8, "bold"),
                     text_color=color).pack(anchor="w")
        ctk.CTkLabel(inner, textvariable=frame._val_var,
                     font=(None, 18, "bold"),
                     text_color=color).pack(anchor="w")
        return frame

    # ── log tags ───────────────────────────────────────────────────────────────

    def _refresh_log_tags(self):
        tb = self._log._textbox
        theme = DARK_THEME if self._is_dark else LIGHT_THEME
        for tag in ("2xx", "3xx", "4xx", "5xx", "error",
                    "info", "ts", "method", "ms"):
            tb.tag_config(tag, foreground=theme[f"tag_{tag}"])

    # ── mode handling ──────────────────────────────────────────────────────────

    def _set_mode(self, mode: str):
        self._mode = mode
        self._update_mode_fields()

    def _update_mode_fields(self):
        for value, btn in self._mode_btns.items():
            active = (value == self._mode)
            btn.configure(
                fg_color=T("accent") if active else T("filter_bg"),
                hover_color=T("accent_hover") if active else T("border"),
                text_color=T("bg") if active else T("text_secondary"),
                border_color=T("accent") if active else T("input_border"))

        # hide all field columns first
        for col in (self._f_interval, self._f_count, self._f_stop):
            col.grid_remove()

        if self._mode == MODE_SINGLE:
            pass  # no extra fields
        elif self._mode == MODE_COUNT:
            self._f_interval.grid()
            self._f_count.grid()
        else:  # continuous
            self._f_interval.grid()
            self._f_stop.grid()

    def _interval_entry(self) -> ctk.CTkEntry:
        return self._get_entry_in_col(self._f_interval)

    def _count_entry(self) -> ctk.CTkEntry:
        return self._get_entry_in_col(self._f_count)

    def _stop_entry(self) -> ctk.CTkEntry:
        return self._get_entry_in_col(self._f_stop)

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
                text="No collections yet.\n\nSave a request\nto get started.",
                font=(None, 9), text_color=T("text_muted"), justify="center")
            lbl.pack(fill=tk.X, padx=8, pady=20)
            self._profile_widgets.append(lbl)
            return

        for name in names:
            data = load_profile(name)
            item = self._build_profile_item(name, data)
            item.pack(fill=tk.X, pady=(0, 5), padx=2)
            self._profile_widgets.append(item)

    def _build_profile_item(self, name: str, data: dict) -> ctk.CTkFrame:
        outer = ctk.CTkFrame(self._prof_scroll,
                             fg_color=T("card_bg"), corner_radius=10,
                             cursor="hand2",
                             border_width=1, border_color=T("card_border"))
        inner = ctk.CTkFrame(outer, fg_color="transparent")
        inner.pack(fill=tk.X, padx=10, pady=8)

        row1 = ctk.CTkFrame(inner, fg_color="transparent")
        row1.pack(fill=tk.X)

        ctk.CTkLabel(row1, text="▶", font=(None, 7),
                     text_color=T("accent")).pack(side=tk.LEFT, padx=(0, 5))
        ctk.CTkLabel(row1, text=name, font=(None, 10, "bold"),
                     text_color=T("fg")).pack(side=tk.LEFT)

        del_lbl = ctk.CTkLabel(row1, text="✕", font=(None, 10),
                                text_color=T("text_muted"), cursor="hand2")
        del_lbl.pack(side=tk.RIGHT)
        del_lbl.bind("<Button-1>",
                     lambda _, n=name: self._delete_profile(n))

        method = data.get("method", "GET")
        mode_label = {
            MODE_SINGLE: "once",
            MODE_COUNT:  f"×{data.get('count', '?')}",
            MODE_CONTINUOUS: f"every {data.get('interval','?')}s",
        }.get(data.get("mode", MODE_CONTINUOUS),
              f"every {data.get('interval','?')}s")

        ctk.CTkLabel(inner, text=f"{method} · {mode_label}",
                     font=(None, 8),
                     text_color=T("text_secondary")).pack(anchor="w",
                                                           pady=(2, 0))

        click = lambda _, n=name: self._load_profile(n)
        for w in (outer, inner, row1):
            w.bind("<Button-1>", click)

        def _enter(_): outer.configure(fg_color=T("filter_bg"))
        def _leave(_): outer.configure(fg_color=T("card_bg"))
        for w in (outer, inner, row1):
            w.bind("<Enter>", _enter)
            w.bind("<Leave>", _leave)

        return outer

    def _load_profile(self, name: str):
        data = load_profile(name)
        if not data:
            return
        self._url_entry.delete(0, tk.END)
        self._url_entry.insert(0, data.get("url", ""))
        self._method_var.set(data.get("method", "GET"))
        self._method_cb.set(data.get("method", "GET"))

        iv = self._interval_entry()
        if iv:
            iv.delete(0, tk.END)
            iv.insert(0, str(data.get("interval", "")))
        sv = self._stop_entry()
        if sv:
            sv.delete(0, tk.END)
            sv.insert(0, data.get("stop", ""))
        cv = self._count_entry()
        if cv:
            cv.delete(0, tk.END)
            if data.get("count"):
                cv.insert(0, str(data["count"]))

        mode = data.get("mode", MODE_CONTINUOUS)
        if mode in (MODE_SINGLE, MODE_COUNT, MODE_CONTINUOUS):
            self._set_mode(mode)

        self._stored_headers = data.get("headers", {})
        self._stored_body    = data.get("body", "")
        # reload header rows
        self._reload_header_rows()
        # reload body
        self._body_box.delete("1.0", tk.END)
        if self._stored_body:
            self._body_box.insert("1.0", self._stored_body)

    def _reload_header_rows(self):
        for item in self._hdr_rows:
            if item:
                item[3].destroy()
        self._hdr_rows.clear()
        for k, v in self._stored_headers.items():
            self._hdr_add_row(k, v)

    def _delete_profile(self, name: str):
        if messagebox.askyesno("Delete", f"Delete '{name}'?"):
            delete_profile(name)
            self._refresh_profiles_list()

    def _save_profile(self):
        name = simpledialog.askstring("Save Collection",
                                      "Collection name:", parent=self._root)
        if not name:
            return
        self._sync_headers()
        self._stored_body = self._body_box.get("1.0", tk.END).strip()

        iv = self._interval_entry()
        sv = self._stop_entry()
        cv = self._count_entry()
        data = {
            "url":      self._url_entry.get(),
            "method":   self._method_var.get(),
            "interval": iv.get() if iv else "",
            "stop":     sv.get() if sv else "",
            "count":    cv.get() if cv else "",
            "mode":     self._mode,
            "headers":  self._stored_headers,
            "body":     self._stored_body,
        }
        save_profile(name, data)
        self._refresh_profiles_list()

    # ── theme ──────────────────────────────────────────────────────────────────

    def _toggle_theme(self):
        self._is_dark = not self._is_dark
        ctk.set_appearance_mode("dark" if self._is_dark else "light")
        theme = DARK_THEME if self._is_dark else LIGHT_THEME
        for w in self._tk_bg:
            try:
                w.configure(bg=theme["bg"])
            except Exception:
                pass
        self._stars.apply_theme(theme)
        dot_bg = theme["card_bg"]
        try:
            self._wu_dot.set_bg(dot_bg)
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

    def _on_response(self, d):        self._safe(self._handle_response, d)
    def _on_req_error(self, d):       self._safe(self._handle_req_error, d)
    def _on_countdown(self, r, t):    self._safe(self._handle_countdown, r, t)
    def _on_sent(self, n, tg):        self._safe(self._handle_sent, n, tg)
    def _on_completed(self, st):      self._safe(self._handle_completed, st)
    def _on_completed_count(self, n): self._safe(self._handle_completed_count, n)
    def _on_completed_single(self):   self._safe(self._handle_completed_single)
    def _on_finished(self):           self._safe(self._handle_finished)
    def _on_error_event(self, m):     self._safe(self._handle_error_event, m)

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
        line = f"[{ts}]  #{cnt:>4}  {meth:<7}  {code}  {ms:>8.1f} ms"
        if self._matches_filter(tag):
            self._append_log(line, tag)
        self._update_stats()

    def _handle_req_error(self, data: dict):
        ts  = data["timestamp"]
        cnt = data["count"]
        err = data["error"]
        ms  = data["elapsed_ms"]
        line = f"[{ts}]  #{cnt:>4}  ERROR    —  {ms:>8.1f} ms  {err}"
        if self._matches_filter("error"):
            self._append_log(line, "error")
        self._update_stats()

    def _handle_countdown(self, remaining: int, total: int):
        self._wu_bar.set(remaining / total)
        if self._mode == MODE_COUNT:
            txt = (f"Sent {self._scheduler.sent_count} of "
                   f"{self._scheduler.target_count} · next in {remaining}s…")
        else:
            txt = f"Next request in {remaining}s…"
        self._status_lbl.configure(text=txt, text_color=T("text_secondary"))

    def _handle_sent(self, n: int, target):
        if target is not None:
            self._status_lbl.configure(text=f"Sent {n} of {target}…",
                                        text_color=T("success"))

    def _handle_completed(self, stop_time):
        self._status_lbl.configure(
            text=f"Completed at {stop_time.strftime('%H:%M')}",
            text_color=T("success"))
        self._wu_bar.set(0)

    def _handle_completed_count(self, n: int):
        self._status_lbl.configure(text=f"Completed — sent {n} requests",
                                    text_color=T("success"))
        self._wu_bar.set(1.0)

    def _handle_completed_single(self):
        self._status_lbl.configure(text="Request sent.", text_color=T("success"))
        self._wu_bar.set(1.0)

    def _handle_finished(self):
        self._set_running(False)
        self._wu_dot.stop()
        theme = DARK_THEME if self._is_dark else LIGHT_THEME
        self._wu_dot.set_color(theme["text_muted"])
        if "Running" in (self._status_lbl.cget("text") or ""):
            self._status_lbl.configure(text="Stopped",
                                        text_color=T("danger"))

    def _handle_error_event(self, msg: str):
        self._status_lbl.configure(text=f"Error: {msg}",
                                    text_color=T("danger"))

    # ── log helpers ────────────────────────────────────────────────────────────

    def _matches_filter(self, tag: str) -> bool:
        f = self._log_filter
        if f == "ALL": return True
        if f == "ERR": return tag == "error"
        return tag == f

    def _append_log(self, line: str, tag: str):
        self._log.configure(state="normal")
        self._log._textbox.insert(tk.END, line + "\n", tag)
        self._log._textbox.see(tk.END)
        self._log.configure(state="disabled")

    def _update_stats(self):
        s = self._scheduler.stats
        vals = [str(s["total"]),
                f"{s['success_pct']:.1f}%",
                f"{s['avg_ms']:.0f}ms",
                str(s["last_status"]) if s["last_status"] else "—"]
        for card, val in zip(self._stat_cards, vals):
            card["val_var"].set(val)

    # ── actions ────────────────────────────────────────────────────────────────

    def _set_running(self, running: bool):
        self._is_running = running
        if running:
            self._wake_btn.configure(
                text="⏹  Stop",
                fg_color=T("danger"), hover_color=T("danger_hover"),
                text_color=("white", "white"))
        else:
            self._wake_btn.configure(
                text="  Send",
                fg_color=T("accent"), hover_color=T("accent_hover"),
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

        # sync inline headers / body before starting
        self._sync_headers()
        self._stored_body = self._body_box.get("1.0", tk.END).strip()

        method  = self._method_var.get()
        headers = self._stored_headers
        body    = self._stored_body if method in ("POST", "PUT", "PATCH") else ""

        interval  = 0
        stop_time = None
        count     = 1

        if self._mode in (MODE_COUNT, MODE_CONTINUOUS):
            iv = self._interval_entry()
            int_str = iv.get().strip() if iv else ""
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
            sv = self._stop_entry()
            stop_str = sv.get().strip() if sv else ""
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
            cv = self._count_entry()
            cnt_str = cv.get().strip() if cv else ""
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
        self._status_lbl.configure(text="Running…", text_color=T("success"))
        theme = DARK_THEME if self._is_dark else LIGHT_THEME
        self._wu_dot.set_color(theme["success"])
        self._wu_dot.start()
        self._wu_bar.set(1.0)

        self._scheduler.start(url, method, headers, body,
                               interval=interval, stop_time=stop_time,
                               mode=self._mode, count=count)

    def _on_stop(self):
        self._scheduler.stop()
        self._status_lbl.configure(text="Stopped", text_color=T("danger"))
        theme = DARK_THEME if self._is_dark else LIGHT_THEME
        self._wu_dot.set_color(theme["danger"])
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
            active = (f == fname)
            btn.configure(
                fg_color=T("filter_act") if active else T("filter_bg"),
                hover_color=T("accent_hover") if active else T("border"),
                text_color=T("bg") if active else T("text_secondary"))

    def _export_log(self):
        content = self._log.get("1.0", tk.END).strip()
        if not content:
            messagebox.showinfo("おはよう", "Log is empty — nothing to export.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text file", "*.txt"),
                       ("CSV", "*.csv"),
                       ("All", "*.*")],
            title="Export Request Log")
        if path:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(content)
            messagebox.showinfo("おはよう", f"Exported to:\n{path}")

    # ── run ────────────────────────────────────────────────────────────────────

    def run(self):
        self._root.mainloop()


def run_app():
    app = MainWindow()
    app.run()
