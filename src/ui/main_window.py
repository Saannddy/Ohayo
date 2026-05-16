"""ui/main_window.py — Ohayo CustomTkinter UI."""

import os
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from datetime import datetime

import customtkinter as ctk

from theme.themes import DARK_THEME, LIGHT_THEME
from core.scheduler import Scheduler
from core.profiles import (get_profile_names, save_profile,
                            load_profile, delete_profile)
from ui.widgets import StarField, AnimatedDot

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD"]
_ICON_PATH = os.path.join(os.path.dirname(__file__),
                          "..", "..", "images", "icon.png")


class MainWindow:
    def __init__(self):
        self._t = DARK_THEME
        self._scheduler = Scheduler()
        self._log_filter = "ALL"
        self._is_running = False
        self._stored_headers: dict = {}
        self._stored_body: str = ""
        self._profile_widgets: list = []
        self._hero_img = None
        self._sb_icon_img = None
        self._filter_btns: dict = {}

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self._root = ctk.CTk()
        self._setup_window()
        self._load_images()
        self._build_ui()
        self._wire_scheduler()

    # ── bootstrap ──────────────────────────────────────────────────────────────

    def _setup_window(self):
        r = self._root
        r.title("おはよう — The API Waker")
        r.geometry("1180x760")
        r.minsize(940, 640)
        r.configure(fg_color=self._t["bg"])
        try:
            img = tk.PhotoImage(file=_ICON_PATH)
            r.iconphoto(True, img)
        except Exception:
            pass

    def _load_images(self):
        if not HAS_PIL:
            return
        try:
            im = Image.open(_ICON_PATH).convert("RGBA")
            self._hero_img    = ImageTk.PhotoImage(im.resize((68, 68),  Image.LANCZOS))
            self._sb_icon_img = ImageTk.PhotoImage(im.resize((34, 34),  Image.LANCZOS))
        except Exception:
            pass

    def _build_ui(self):
        self._build_sidebar()
        self._build_content()

    # ── sidebar ────────────────────────────────────────────────────────────────

    def _build_sidebar(self):
        t = self._t

        self._sidebar = ctk.CTkFrame(self._root, width=230,
                                      fg_color=t["sidebar_bg"], corner_radius=0)
        self._sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self._sidebar.pack_propagate(False)

        # Separator line
        self._sb_sep = ctk.CTkFrame(self._root, width=1,
                                     fg_color=t["border"], corner_radius=0)
        self._sb_sep.pack(side=tk.LEFT, fill=tk.Y)

        # Brand
        brand = ctk.CTkFrame(self._sidebar, fg_color="transparent")
        brand.pack(fill=tk.X, padx=20, pady=(22, 8))
        self._sb_brand = brand

        if self._sb_icon_img:
            self._sb_icon_lbl = tk.Label(brand, image=self._sb_icon_img,
                                          bg=t["sidebar_bg"], bd=0)
            self._sb_icon_lbl.pack(anchor="w", pady=(0, 10))
        else:
            self._sb_icon_lbl = None

        self._sb_title = ctk.CTkLabel(brand, text="おはよう",
                                       font=(None, 22, "bold"),
                                       text_color=t["accent"])
        self._sb_title.pack(anchor="w")

        self._sb_sub = ctk.CTkLabel(brand, text="API Waker",
                                     font=(None, 9),
                                     text_color=t["text_secondary"])
        self._sb_sub.pack(anchor="w", pady=(1, 0))

        # Divider
        self._sb_div1 = ctk.CTkFrame(self._sidebar, height=1,
                                      fg_color=t["border"], corner_radius=0)
        self._sb_div1.pack(fill=tk.X, padx=16, pady=(10, 14))

        # Profiles header
        phdr = ctk.CTkFrame(self._sidebar, fg_color="transparent")
        phdr.pack(fill=tk.X, padx=20)
        self._sb_phdr = phdr

        self._sb_plbl = ctk.CTkLabel(phdr, text="SAVED PROFILES",
                                      font=(None, 8, "bold"),
                                      text_color=t["text_muted"])
        self._sb_plbl.pack(anchor="w", pady=(0, 8))

        # Scrollable profile list
        self._prof_scroll = ctk.CTkScrollableFrame(
            self._sidebar,
            fg_color="transparent",
            scrollbar_fg_color=t["sidebar_bg"],
            scrollbar_button_color=t["scroll_fg"],
            scrollbar_button_hover_color=t["accent"],
            corner_radius=0,
        )
        self._prof_scroll.pack(fill=tk.BOTH, expand=True, padx=8)

        # Bottom area (packed from bottom)
        self._sb_div2 = ctk.CTkFrame(self._sidebar, height=1,
                                      fg_color=t["border"], corner_radius=0)
        self._sb_div2.pack(fill=tk.X, padx=16, side=tk.BOTTOM)

        bottom = ctk.CTkFrame(self._sidebar, fg_color="transparent")
        bottom.pack(fill=tk.X, padx=16, pady=14, side=tk.BOTTOM)
        self._sb_bottom = bottom

        self._save_prof_btn = ctk.CTkButton(
            bottom, text="＋  Save Profile",
            command=self._save_profile,
            fg_color=t["filter_bg"], hover_color=t["card_border"],
            text_color=t["text_secondary"],
            font=(None, 10, "bold"),
            height=34, corner_radius=8,
        )
        self._save_prof_btn.pack(fill=tk.X, pady=(0, 10))

        theme_row = ctk.CTkFrame(bottom, fg_color="transparent")
        theme_row.pack(fill=tk.X)
        self._sb_theme_row = theme_row

        self._theme_lbl = ctk.CTkLabel(theme_row, text="Theme",
                                        font=(None, 9),
                                        text_color=t["text_secondary"])
        self._theme_lbl.pack(side=tk.LEFT)

        self._theme_btn = ctk.CTkLabel(theme_row, text="☀️",
                                        font=(None, 15), cursor="hand2",
                                        text_color=t["fg"])
        self._theme_btn.pack(side=tk.RIGHT)
        self._theme_btn.bind("<Button-1>", lambda _: self._toggle_theme())

        self._refresh_profiles_list()

    # ── content ────────────────────────────────────────────────────────────────

    def _build_content(self):
        t = self._t

        # Plain tk.Frame hosts the starfield canvas
        self._content_wrap = tk.Frame(self._root, bg=t["bg"])
        self._content_wrap.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._stars = StarField(self._content_wrap, theme=t, num_stars=110, seed=7)
        self._stars.place(x=0, y=0, relwidth=1, relheight=1)

        cols_holder = tk.Frame(self._content_wrap, bg=t["bg"])
        cols_holder.place(x=16, y=16, relwidth=1, relheight=1, width=-32, height=-32)
        self._cols_holder = cols_holder
        cols_holder.lift()

        left_col = tk.Frame(cols_holder, bg=t["bg"])
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        self._left_col = left_col

        right_col = tk.Frame(cols_holder, bg=t["bg"])
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 0))
        self._right_col = right_col

        self._build_wakeup_panel()
        self._build_activity_panel()

    # ── Wake Up panel ──────────────────────────────────────────────────────────

    def _build_wakeup_panel(self):
        t = self._t

        self._wu_card = ctk.CTkFrame(self._left_col,
                                      fg_color=t["card_bg"], corner_radius=20,
                                      border_width=1, border_color=t["card_border"])
        self._wu_card.pack(fill=tk.BOTH, expand=True)

        pad = ctk.CTkFrame(self._wu_card, fg_color="transparent")
        pad.pack(fill=tk.BOTH, expand=True, padx=26, pady=22)
        self._wu_pad = pad

        # Hero row
        hero = ctk.CTkFrame(pad, fg_color="transparent")
        hero.pack(fill=tk.X, pady=(0, 18))

        if self._hero_img:
            self._wu_icon_lbl = tk.Label(hero, image=self._hero_img,
                                          bg=t["card_bg"], bd=0)
            self._wu_icon_lbl.pack(side=tk.LEFT, padx=(0, 18))
        else:
            self._wu_icon_lbl = None

        tcol = ctk.CTkFrame(hero, fg_color="transparent")
        tcol.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._wu_title = ctk.CTkLabel(tcol, text="Wake Up API",
                                       font=(None, 24, "bold"),
                                       text_color=t["fg"])
        self._wu_title.pack(anchor="w")

        self._wu_sub = ctk.CTkLabel(tcol, text="Schedule HTTP requests on repeat",
                                     font=(None, 10),
                                     text_color=t["text_secondary"])
        self._wu_sub.pack(anchor="w", pady=(3, 0))

        # URL
        ctk.CTkLabel(pad, text="TARGET URL", font=(None, 9, "bold"),
                     text_color=t["text_secondary"], anchor="w").pack(
            fill=tk.X, pady=(0, 4))

        self._url_entry = ctk.CTkEntry(
            pad,
            placeholder_text="https://example.com/api/ping",
            fg_color=t["input_bg"], border_color=t["input_border"],
            text_color=t["fg"], placeholder_text_color=t["text_muted"],
            font=(None, 11), height=42, corner_radius=8, border_width=1,
        )
        self._url_entry.pack(fill=tk.X, pady=(0, 14))

        # Timing row
        timing = ctk.CTkFrame(pad, fg_color="transparent")
        timing.pack(fill=tk.X, pady=(0, 14))
        timing.columnconfigure(0, weight=2, minsize=110)
        timing.columnconfigure(1, weight=1, minsize=88)
        timing.columnconfigure(2, weight=1, minsize=88)

        # Method
        mc = ctk.CTkFrame(timing, fg_color="transparent")
        mc.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        ctk.CTkLabel(mc, text="METHOD", font=(None, 9, "bold"),
                     text_color=t["text_secondary"], anchor="w").pack(
            fill=tk.X, pady=(0, 4))
        self._method_var = tk.StringVar(value="GET")
        self._method_cb = ctk.CTkComboBox(
            mc, variable=self._method_var, values=_METHODS,
            fg_color=t["input_bg"], border_color=t["input_border"],
            button_color=t["input_bg"], button_hover_color=t["card_border"],
            dropdown_fg_color=t["card_bg"],
            dropdown_hover_color=t["filter_bg"],
            text_color=t["fg"], font=(None, 11, "bold"),
            height=40, corner_radius=8, state="readonly",
        )
        self._method_cb.pack(fill=tk.X)

        # Interval
        ic = ctk.CTkFrame(timing, fg_color="transparent")
        ic.grid(row=0, column=1, padx=(0, 8), sticky="nsew")
        ctk.CTkLabel(ic, text="EVERY (s)", font=(None, 9, "bold"),
                     text_color=t["text_secondary"], anchor="w").pack(
            fill=tk.X, pady=(0, 4))
        self._interval_entry = ctk.CTkEntry(
            ic, placeholder_text="5",
            fg_color=t["input_bg"], border_color=t["input_border"],
            text_color=t["fg"], placeholder_text_color=t["text_muted"],
            font=(None, 11), height=40, corner_radius=8, border_width=1,
        )
        self._interval_entry.pack(fill=tk.X)

        # Stop time
        sc = ctk.CTkFrame(timing, fg_color="transparent")
        sc.grid(row=0, column=2, sticky="nsew")
        ctk.CTkLabel(sc, text="UNTIL  HH:MM", font=(None, 9, "bold"),
                     text_color=t["text_secondary"], anchor="w").pack(
            fill=tk.X, pady=(0, 4))
        self._stop_entry = ctk.CTkEntry(
            sc, placeholder_text="23:59",
            fg_color=t["input_bg"], border_color=t["input_border"],
            text_color=t["fg"], placeholder_text_color=t["text_muted"],
            font=(None, 11), height=40, corner_radius=8, border_width=1,
        )
        self._stop_entry.pack(fill=tk.X)

        # Extras
        extras = ctk.CTkFrame(pad, fg_color="transparent")
        extras.pack(fill=tk.X, pady=(0, 18))

        self._headers_btn = ctk.CTkLabel(extras, text="✎  Headers",
                                          font=(None, 10),
                                          text_color=t["text_secondary"],
                                          cursor="hand2")
        self._headers_btn.pack(side=tk.LEFT, padx=(0, 20))
        self._headers_btn.bind("<Button-1>", lambda _: self._open_headers_dialog())

        self._body_btn = ctk.CTkLabel(extras, text="✎  Body",
                                       font=(None, 10),
                                       text_color=t["text_secondary"],
                                       cursor="hand2")
        self._body_btn.pack(side=tk.LEFT)
        self._body_btn.bind("<Button-1>", lambda _: self._open_body_dialog())

        # Wake button
        self._wake_btn = ctk.CTkButton(
            pad, text="▶   WAKE UP API",
            command=self._on_wake_click,
            fg_color=t["accent"], hover_color=t["accent_hover"],
            text_color=t["bg"], font=(None, 14, "bold"),
            height=52, corner_radius=12,
        )
        self._wake_btn.pack(fill=tk.X, pady=(0, 14))

        # Status row
        st_row = ctk.CTkFrame(pad, fg_color="transparent")
        st_row.pack(fill=tk.X, pady=(0, 8))
        self._wu_st_row = st_row

        self._wu_dot = AnimatedDot(st_row, color=t["text_muted"],
                                    size=10, bg=t["card_bg"])
        self._wu_dot.pack(side=tk.LEFT, padx=(0, 8))

        self._wu_status = ctk.CTkLabel(st_row, text="Ready to wake up an API.",
                                        font=(None, 10),
                                        text_color=t["text_secondary"])
        self._wu_status.pack(side=tk.LEFT)

        # Progress bar
        self._wu_bar = ctk.CTkProgressBar(pad,
                                           fg_color=t["filter_bg"],
                                           progress_color=t["accent"],
                                           height=5, corner_radius=3)
        self._wu_bar.pack(fill=tk.X)
        self._wu_bar.set(0)

    # ── Activity panel ─────────────────────────────────────────────────────────

    def _build_activity_panel(self):
        t = self._t

        self._act_card = ctk.CTkFrame(self._right_col,
                                       fg_color=t["card_bg"], corner_radius=20,
                                       border_width=1, border_color=t["card_border"])
        self._act_card.pack(fill=tk.BOTH, expand=True)

        wrap = ctk.CTkFrame(self._act_card, fg_color="transparent")
        wrap.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self._act_wrap = wrap

        # Title row
        trow = ctk.CTkFrame(wrap, fg_color="transparent")
        trow.pack(fill=tk.X, pady=(0, 14))

        self._act_title = ctk.CTkLabel(trow, text="Activity",
                                        font=(None, 20, "bold"),
                                        text_color=t["fg"])
        self._act_title.pack(side=tk.LEFT)

        self._export_btn = ctk.CTkButton(
            trow, text="⬇ Export", command=self._export_log,
            fg_color=t["filter_bg"], hover_color=t["border"],
            text_color=t["text_secondary"], font=(None, 9, "bold"),
            width=80, height=28, corner_radius=6,
        )
        self._export_btn.pack(side=tk.RIGHT, padx=(4, 0))

        self._clear_btn = ctk.CTkButton(
            trow, text="🗑 Clear", command=self._on_clear,
            fg_color=t["filter_bg"], hover_color=t["border"],
            text_color=t["text_secondary"], font=(None, 9, "bold"),
            width=80, height=28, corner_radius=6,
        )
        self._clear_btn.pack(side=tk.RIGHT, padx=(4, 0))

        # Stats
        stats_frame = ctk.CTkFrame(wrap, fg_color="transparent")
        stats_frame.pack(fill=tk.X, pady=(0, 14))
        self._act_stats = stats_frame

        specs = [("Total", "—", t["accent"]),
                 ("Success", "—%", t["success"]),
                 ("Avg", "—ms", t["warning"]),
                 ("Status", "—", t["text_secondary"])]
        self._stat_cards: list[dict] = []
        for i, (lbl, val, col) in enumerate(specs):
            card = self._make_stat_card(stats_frame, lbl, val, col, t)
            card["frame"].grid(row=0, column=i,
                               padx=(0 if i == 0 else 6, 0), sticky="nsew")
            stats_frame.columnconfigure(i, weight=1)
            self._stat_cards.append(card)

        # Filter buttons
        frow = ctk.CTkFrame(wrap, fg_color="transparent")
        frow.pack(fill=tk.X, pady=(0, 10))
        self._filter_btns = {}
        for fname in ["ALL", "2xx", "3xx", "4xx", "5xx", "ERR"]:
            is_active = (fname == "ALL")
            btn = ctk.CTkButton(
                frow, text=fname,
                command=lambda f=fname: self._on_filter(f),
                fg_color=t["filter_act"] if is_active else t["filter_bg"],
                hover_color=t["accent_hover"] if is_active else t["border"],
                text_color=t["bg"] if is_active else t["text_secondary"],
                font=(None, 9, "bold"),
                width=46, height=26, corner_radius=6,
            )
            btn.pack(side=tk.LEFT, padx=(0, 4))
            self._filter_btns[fname] = btn

        # Log textbox
        self._log = ctk.CTkTextbox(
            wrap,
            fg_color=t["log_bg"],
            text_color=t["fg"],
            font=("Courier", 9),
            corner_radius=10,
            border_width=1,
            border_color=t["card_border"],
            scrollbar_button_color=t["scroll_fg"],
            scrollbar_button_hover_color=t["accent"],
            state="disabled",
            wrap="word",
        )
        self._log.pack(fill=tk.BOTH, expand=True)

        tb = self._log._textbox
        for tag in ("2xx", "3xx", "4xx", "5xx", "error",
                    "info", "ts", "method", "ms"):
            tb.tag_config(tag, foreground=t[f"tag_{tag}"])

    def _make_stat_card(self, parent, label, value, color, t) -> dict:
        frame = ctk.CTkFrame(parent, fg_color=t["input_bg"],
                              corner_radius=10, border_width=0)
        bar = ctk.CTkFrame(frame, fg_color=color, height=3, corner_radius=0)
        bar.pack(fill=tk.X)
        body = ctk.CTkFrame(frame, fg_color="transparent")
        body.pack(fill=tk.X, padx=10, pady=8)
        val_var = tk.StringVar(value=value)
        val_lbl = ctk.CTkLabel(body, textvariable=val_var,
                                font=(None, 20, "bold"), text_color=color)
        val_lbl.pack(anchor="w")
        name_lbl = ctk.CTkLabel(body, text=label, font=(None, 8),
                                  text_color=t["text_secondary"])
        name_lbl.pack(anchor="w")
        return {
            "frame": frame, "bar": bar, "body": body,
            "val_var": val_var, "val_lbl": val_lbl, "name_lbl": name_lbl,
            "color": color,
        }

    # ── sidebar profiles ───────────────────────────────────────────────────────

    def _refresh_profiles_list(self):
        t = self._t
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
                font=(None, 9), text_color=t["text_muted"], justify="center",
            )
            lbl.pack(fill=tk.X, padx=8, pady=20)
            self._profile_widgets.append(lbl)
            return

        for name in names:
            data = load_profile(name)
            item = self._build_profile_item(name, data)
            item.pack(fill=tk.X, pady=(0, 4), padx=2)
            self._profile_widgets.append(item)

    def _build_profile_item(self, name: str, data: dict) -> ctk.CTkFrame:
        t = self._t
        norm_bg  = t["card_bg"]
        hover_bg = t["filter_bg"]

        outer = ctk.CTkFrame(self._prof_scroll, fg_color=norm_bg,
                              corner_radius=8, cursor="hand2")

        inner = ctk.CTkFrame(outer, fg_color="transparent")
        inner.pack(fill=tk.X, padx=12, pady=9)

        row1 = ctk.CTkFrame(inner, fg_color="transparent")
        row1.pack(fill=tk.X)

        play = ctk.CTkLabel(row1, text="▶", font=(None, 7),
                             text_color=t["accent"])
        play.pack(side=tk.LEFT, padx=(0, 6))

        nlbl = ctk.CTkLabel(row1, text=name, font=(None, 9, "bold"),
                             text_color=t["fg"])
        nlbl.pack(side=tk.LEFT)

        del_btn = ctk.CTkLabel(row1, text="✕", font=(None, 9),
                                text_color=t["text_muted"], cursor="hand2")
        del_btn.pack(side=tk.RIGHT)
        del_btn.bind("<Button-1>",
                     lambda _, n=name: self._delete_profile_by_name(n))

        meta = ctk.CTkLabel(inner,
                             text=f"{data.get('method','GET')} · every {data.get('interval','?')}s",
                             font=(None, 8), text_color=t["text_secondary"])
        meta.pack(anchor="w", pady=(2, 0))

        click_handler = lambda _, n=name: self._load_profile_by_name(n)
        for w in (outer, inner, row1, play, nlbl, meta):
            w.bind("<Button-1>", click_handler)

        def _enter(_):
            outer.configure(fg_color=hover_bg)
        def _leave(_):
            outer.configure(fg_color=norm_bg)

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
        self._interval_entry.insert(0, data.get("interval", ""))
        self._stop_entry.delete(0, tk.END)
        self._stop_entry.insert(0, data.get("stop", ""))
        self._stored_headers = data.get("headers", {})
        self._stored_body    = data.get("body", "")
        self._update_extra_indicators()

    def _delete_profile_by_name(self, name: str):
        if messagebox.askyesno("Delete Profile", f"Delete '{name}'?"):
            delete_profile(name)
            self._refresh_profiles_list()

    # ── dialogs ────────────────────────────────────────────────────────────────

    def _open_headers_dialog(self):
        t = self._t
        dlg = ctk.CTkToplevel(self._root)
        dlg.title("HTTP Headers")
        dlg.geometry("520x440")
        dlg.configure(fg_color=t["bg"])
        dlg.transient(self._root)
        dlg.grab_set()

        ctk.CTkLabel(dlg, text="HTTP Headers", font=(None, 14, "bold"),
                     text_color=t["fg"]).pack(anchor="w", padx=20, pady=(18, 4))
        ctk.CTkLabel(dlg, text="Key / value pairs sent with every request.",
                     font=(None, 9), text_color=t["text_secondary"]).pack(
            anchor="w", padx=20)

        # Accent bar + card
        card = ctk.CTkFrame(dlg, fg_color=t["card_bg"], corner_radius=10,
                             border_width=1, border_color=t["card_border"])
        card.pack(fill=tk.BOTH, expand=True, padx=20, pady=12)
        ctk.CTkFrame(card, fg_color=t["accent"], height=3,
                     corner_radius=0).pack(fill=tk.X)

        body = ctk.CTkScrollableFrame(card, fg_color="transparent",
                                       corner_radius=0)
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        rows: list = []

        def add_row(key="", value=""):
            row = ctk.CTkFrame(body, fg_color="transparent")
            row.pack(fill=tk.X, pady=2)
            ke = ctk.CTkEntry(row, placeholder_text="Header",
                               fg_color=t["input_bg"],
                               border_color=t["input_border"],
                               text_color=t["fg"], font=(None, 9),
                               height=32, corner_radius=6)
            ke.pack(side=tk.LEFT, padx=(0, 6), fill=tk.X, expand=True)
            if key:
                ke.insert(0, key)
            ve = ctk.CTkEntry(row, placeholder_text="Value",
                               fg_color=t["input_bg"],
                               border_color=t["input_border"],
                               text_color=t["fg"], font=(None, 9),
                               height=32, corner_radius=6)
            ve.pack(side=tk.LEFT, padx=(0, 6), fill=tk.X, expand=True)
            if value:
                ve.insert(0, value)
            idx = len(rows)
            db = ctk.CTkButton(row, text="✕", width=28, height=28,
                                corner_radius=6,
                                fg_color=t["danger_bg"],
                                hover_color=t["danger"],
                                text_color=t["danger"],
                                font=(None, 10, "bold"),
                                command=lambda i=idx: _remove(i))
            db.pack(side=tk.LEFT)
            rows.append((ke, ve, db, row))

        def _remove(idx):
            if idx < len(rows) and rows[idx] is not None:
                rows[idx][3].destroy()
                rows[idx] = None

        # Seed existing headers
        for k, v in self._stored_headers.items():
            add_row(k, v)

        # Add button row
        add_bar = ctk.CTkFrame(card, fg_color="transparent")
        add_bar.pack(fill=tk.X, padx=12, pady=(0, 8))
        ctk.CTkButton(add_bar, text="＋  Add Header", command=add_row,
                      fg_color=t["filter_bg"], hover_color=t["border"],
                      text_color=t["text_secondary"], font=(None, 9),
                      height=28, corner_radius=6).pack(anchor="w")

        btn_row = ctk.CTkFrame(dlg, fg_color="transparent")
        btn_row.pack(fill=tk.X, padx=20, pady=(0, 18))

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
                      fg_color=t["accent"], hover_color=t["accent_hover"],
                      text_color=t["bg"], font=(None, 10, "bold"),
                      height=36, corner_radius=8).pack(side=tk.RIGHT)
        ctk.CTkButton(btn_row, text="Cancel", command=dlg.destroy,
                      fg_color=t["filter_bg"], hover_color=t["border"],
                      text_color=t["text_secondary"], font=(None, 10, "bold"),
                      height=36, corner_radius=8).pack(side=tk.RIGHT, padx=(0, 8))

    def _open_body_dialog(self):
        t = self._t
        dlg = ctk.CTkToplevel(self._root)
        dlg.title("Request Body")
        dlg.geometry("520x440")
        dlg.configure(fg_color=t["bg"])
        dlg.transient(self._root)
        dlg.grab_set()

        ctk.CTkLabel(dlg, text="Request Body", font=(None, 14, "bold"),
                     text_color=t["fg"]).pack(anchor="w", padx=20, pady=(18, 4))
        ctk.CTkLabel(dlg, text="Sent only with POST / PUT / PATCH.",
                     font=(None, 9), text_color=t["text_secondary"]).pack(
            anchor="w", padx=20)

        card = ctk.CTkFrame(dlg, fg_color=t["card_bg"], corner_radius=10,
                             border_width=1, border_color=t["card_border"])
        card.pack(fill=tk.BOTH, expand=True, padx=20, pady=12)
        ctk.CTkFrame(card, fg_color=t["accent"], height=3,
                     corner_radius=0).pack(fill=tk.X)

        text = ctk.CTkTextbox(card, fg_color=t["input_bg"],
                               text_color=t["fg"], font=("Courier", 10),
                               corner_radius=0, border_width=0)
        text.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        if self._stored_body:
            text.insert("1.0", self._stored_body)

        btn_row = ctk.CTkFrame(dlg, fg_color="transparent")
        btn_row.pack(fill=tk.X, padx=20, pady=(0, 18))

        def _save():
            self._stored_body = text.get("1.0", tk.END).strip()
            self._update_extra_indicators()
            dlg.destroy()

        ctk.CTkButton(btn_row, text="Save", command=_save,
                      fg_color=t["accent"], hover_color=t["accent_hover"],
                      text_color=t["bg"], font=(None, 10, "bold"),
                      height=36, corner_radius=8).pack(side=tk.RIGHT)
        ctk.CTkButton(btn_row, text="Cancel", command=dlg.destroy,
                      fg_color=t["filter_bg"], hover_color=t["border"],
                      text_color=t["text_secondary"], font=(None, 10, "bold"),
                      height=36, corner_radius=8).pack(side=tk.RIGHT, padx=(0, 8))

    def _update_extra_indicators(self):
        t = self._t
        has_h = bool(self._stored_headers)
        has_b = bool(self._stored_body)
        self._headers_btn.configure(
            text=f"✎  Headers · {len(self._stored_headers)}" if has_h else "✎  Headers",
            text_color=t["accent"] if has_h else t["text_secondary"])
        self._body_btn.configure(
            text="✎  Body · set" if has_b else "✎  Body",
            text_color=t["accent"] if has_b else t["text_secondary"])

    # ── theme ──────────────────────────────────────────────────────────────────

    def _toggle_theme(self):
        self._t = LIGHT_THEME if self._t["name"] == "dark" else DARK_THEME
        is_dark = self._t["name"] == "dark"
        ctk.set_appearance_mode("dark" if is_dark else "light")
        self._theme_btn.configure(text="🌙" if not is_dark else "☀️")
        self._apply_theme()

    def _apply_theme(self):
        t = self._t

        self._root.configure(fg_color=t["bg"])

        # Sidebar
        self._sidebar.configure(fg_color=t["sidebar_bg"])
        self._sb_sep.configure(fg_color=t["border"])
        self._sb_div1.configure(fg_color=t["border"])
        self._sb_div2.configure(fg_color=t["border"])
        self._sb_title.configure(text_color=t["accent"])
        self._sb_sub.configure(text_color=t["text_secondary"])
        self._sb_plbl.configure(text_color=t["text_muted"])
        if self._sb_icon_lbl:
            self._sb_icon_lbl.configure(bg=t["sidebar_bg"])
        self._theme_lbl.configure(text_color=t["text_secondary"])
        self._prof_scroll.configure(
            scrollbar_button_color=t["scroll_fg"],
            scrollbar_button_hover_color=t["accent"])
        self._save_prof_btn.configure(
            fg_color=t["filter_bg"], hover_color=t["card_border"],
            text_color=t["text_secondary"])
        self._refresh_profiles_list()

        # Content
        self._content_wrap.configure(bg=t["bg"])
        self._cols_holder.configure(bg=t["bg"])
        self._left_col.configure(bg=t["bg"])
        self._right_col.configure(bg=t["bg"])
        self._stars.apply_theme(t)

        # Wake Up card
        self._wu_card.configure(fg_color=t["card_bg"], border_color=t["card_border"])
        self._wu_title.configure(text_color=t["fg"])
        self._wu_sub.configure(text_color=t["text_secondary"])
        if self._wu_icon_lbl:
            self._wu_icon_lbl.configure(bg=t["card_bg"])
        self._url_entry.configure(fg_color=t["input_bg"],
                                   border_color=t["input_border"],
                                   text_color=t["fg"],
                                   placeholder_text_color=t["text_muted"])
        self._method_cb.configure(fg_color=t["input_bg"],
                                   border_color=t["input_border"],
                                   button_color=t["input_bg"],
                                   text_color=t["fg"])
        self._interval_entry.configure(fg_color=t["input_bg"],
                                        border_color=t["input_border"],
                                        text_color=t["fg"])
        self._stop_entry.configure(fg_color=t["input_bg"],
                                    border_color=t["input_border"],
                                    text_color=t["fg"])
        self._update_extra_indicators()
        if self._is_running:
            self._wake_btn.configure(fg_color=t["danger"],
                                      hover_color=t["danger_hover"],
                                      text_color="white")
        else:
            self._wake_btn.configure(fg_color=t["accent"],
                                      hover_color=t["accent_hover"],
                                      text_color=t["bg"])
        self._wu_dot.set_bg(t["card_bg"])
        self._wu_status.configure(text_color=t["text_secondary"])
        self._wu_bar.configure(fg_color=t["filter_bg"],
                                progress_color=t["accent"])

        # Activity card
        self._act_card.configure(fg_color=t["card_bg"], border_color=t["card_border"])
        self._act_title.configure(text_color=t["fg"])
        self._export_btn.configure(fg_color=t["filter_bg"], hover_color=t["border"],
                                    text_color=t["text_secondary"])
        self._clear_btn.configure(fg_color=t["filter_bg"], hover_color=t["border"],
                                   text_color=t["text_secondary"])
        for card in self._stat_cards:
            card["frame"].configure(fg_color=t["input_bg"])
            card["val_lbl"].configure(text_color=card["color"])
            card["name_lbl"].configure(text_color=t["text_secondary"])

        active = self._log_filter
        for fname, btn in self._filter_btns.items():
            is_active = (fname == active)
            btn.configure(
                fg_color=t["filter_act"] if is_active else t["filter_bg"],
                hover_color=t["accent_hover"] if is_active else t["border"],
                text_color=t["bg"] if is_active else t["text_secondary"])

        self._log.configure(fg_color=t["log_bg"], text_color=t["fg"],
                             border_color=t["card_border"],
                             scrollbar_button_color=t["scroll_fg"],
                             scrollbar_button_hover_color=t["accent"])
        tb = self._log._textbox
        for tag in ("2xx", "3xx", "4xx", "5xx", "error",
                    "info", "ts", "method", "ms"):
            tb.tag_config(tag, foreground=t[f"tag_{tag}"])

    # ── scheduler wiring ───────────────────────────────────────────────────────

    def _wire_scheduler(self):
        sch = self._scheduler
        (sch
         .on("response",    self._on_response)
         .on("req_error",   self._on_req_error)
         .on("countdown",   self._on_countdown)
         .on("completed",   self._on_completed)
         .on("finished",    self._on_finished)
         .on("error_event", self._on_error_event))

    def _safe(self, fn, *a, **kw):
        self._root.after(0, lambda: fn(*a, **kw))

    def _on_response(self, d):     self._safe(self._handle_response, d)
    def _on_req_error(self, d):    self._safe(self._handle_req_error, d)
    def _on_countdown(self, r, t): self._safe(self._handle_countdown, r, t)
    def _on_completed(self, st):   self._safe(self._handle_completed, st)
    def _on_finished(self):        self._safe(self._handle_finished)
    def _on_error_event(self, m):  self._safe(self._handle_error_event, m)

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
        self._wu_status.configure(text=f"Next request in {remaining}s…",
                                   text_color=self._t["text_secondary"])

    def _handle_completed(self, stop_time):
        msg = f"Completed at {stop_time.strftime('%H:%M')}"
        self._wu_status.configure(text=msg, text_color=self._t["success"])
        self._wu_dot.set_color(self._t["success"])
        self._wu_bar.set(0)

    def _handle_finished(self):
        self._set_running(False)
        self._wu_dot.stop()
        self._wu_bar.set(0)
        status_text = self._wu_status.cget("text")
        if "Running" in (status_text or ""):
            self._wu_status.configure(text="Stopped",
                                       text_color=self._t["danger"])

    def _handle_error_event(self, msg: str):
        self._wu_status.configure(text=f"Error: {msg}",
                                   text_color=self._t["danger"])

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
        t = self._t
        if running:
            self._wake_btn.configure(text="⏹  STOP  WAKING",
                                      fg_color=t["danger"],
                                      hover_color=t["danger_hover"],
                                      text_color="white")
        else:
            self._wake_btn.configure(text="▶   WAKE UP API",
                                      fg_color=t["accent"],
                                      hover_color=t["accent_hover"],
                                      text_color=t["bg"])

    def _on_wake_click(self):
        if self._is_running:
            self._on_stop()
        else:
            self._on_start()

    def _on_start(self):
        url      = self._url_entry.get().strip()
        int_str  = self._interval_entry.get().strip()
        stop_str = self._stop_entry.get().strip()

        if not url:
            messagebox.showerror("おはよう", "Please enter a URL.")
            return
        if not int_str:
            messagebox.showerror("おはよう", "Please enter an interval (seconds).")
            return
        if not stop_str:
            messagebox.showerror("おはよう", "Please enter a stop time (HH:MM).")
            return
        try:
            interval = int(int_str)
            if interval <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("おはよう", "Interval must be a positive integer.")
            return
        try:
            stop_time = datetime.strptime(stop_str, "%H:%M").time()
        except ValueError:
            messagebox.showerror("おはよう", "Stop time must be HH:MM (24-hour).")
            return

        method  = self._method_var.get()
        headers = self._stored_headers
        body    = self._stored_body if method in ("POST", "PUT", "PATCH") else ""

        self._set_running(True)
        self._wu_status.configure(text="Running…", text_color=self._t["success"])
        self._wu_dot.set_color(self._t["success"])
        self._wu_dot.start()
        self._wu_bar.set(1.0)
        self._scheduler.start(url, method, headers, body, interval, stop_time)

    def _on_stop(self):
        self._scheduler.stop()
        self._wu_status.configure(text="Stopped", text_color=self._t["danger"])
        self._wu_dot.set_color(self._t["danger"])
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
        t = self._t
        for f, btn in self._filter_btns.items():
            is_active = (f == fname)
            btn.configure(
                fg_color=t["filter_act"] if is_active else t["filter_bg"],
                hover_color=t["accent_hover"] if is_active else t["border"],
                text_color=t["bg"] if is_active else t["text_secondary"])

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
