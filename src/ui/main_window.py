"""ui/main_window.py — Ohayo Spotify-style single-page layout."""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from datetime import datetime

from theme.themes import DARK_THEME, LIGHT_THEME
from core.scheduler import Scheduler
from core.profiles import (get_profile_names, save_profile,
                            load_profile, delete_profile)
from ui.widgets import (StarField, AnimatedDot, CountdownBar,
                        StatsCard, PlaceholderEntry, MiniEntry,
                        ActionButton, FilterButton, HeadersEditor)

try:
    from PIL import Image, ImageDraw, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD"]
_ICON_PATH = os.path.join(os.path.dirname(__file__),
                          "..", "..", "images", "icon.png")


# ── rounded-rect helper ───────────────────────────────────────────────────────

def _draw_rounded_bg(canvas, w, h, radius, fill, border=None):
    """Render a PIL rounded rect onto *canvas*. canvas._rr keeps the ref."""
    if not HAS_PIL or w < 4 or h < 4:
        return

    def _rgba(c):
        c = c.lstrip("#")
        return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), 255

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try:
        if border:
            draw.rounded_rectangle([0, 0, w - 1, h - 1],
                                    radius=radius, fill=_rgba(border))
            draw.rounded_rectangle([1, 1, w - 2, h - 2],
                                    radius=max(1, radius - 1), fill=_rgba(fill))
        else:
            draw.rounded_rectangle([0, 0, w - 1, h - 1],
                                    radius=radius, fill=_rgba(fill))
    except AttributeError:
        # Pillow < 8.2 fallback — plain rectangle
        if border:
            draw.rectangle([0, 0, w - 1, h - 1], fill=_rgba(border))
            draw.rectangle([1, 1, w - 2, h - 2], fill=_rgba(fill))
        else:
            draw.rectangle([0, 0, w - 1, h - 1], fill=_rgba(fill))

    canvas._rr = ImageTk.PhotoImage(img)
    canvas.delete("rr")
    canvas.create_image(0, 0, anchor="nw", image=canvas._rr, tags="rr")


# ── RoundedPanel ─────────────────────────────────────────────────────────────

class RoundedPanel:
    """Card with PIL-rendered rounded corners.

    Place `.outer` in the layout.  Add content widgets inside `.inner`.
    """

    def __init__(self, parent, theme, radius: int = 14):
        self._t = theme
        self._r = radius

        self.outer = tk.Frame(parent, bg=theme["bg"])

        self._cv = tk.Canvas(self.outer, bg=theme["bg"],
                              highlightthickness=0, bd=0)
        self._cv.place(relx=0, rely=0, relwidth=1, relheight=1)

        # 1 px inset so the border colour drawn by PIL is visible
        self.inner = tk.Frame(self.outer, bg=theme["card_bg"])
        self.inner.place(x=1, y=1, relwidth=1, relheight=1, width=-2, height=-2)

        self.outer.bind("<Configure>", self._redraw)

    def _redraw(self, _=None):
        w = self.outer.winfo_width()
        h = self.outer.winfo_height()
        if w < 4 or h < 4:
            return
        _draw_rounded_bg(self._cv, w, h, self._r,
                         self._t["card_bg"], self._t.get("card_border"))
        self.inner.lift()

    def apply_theme(self, t: dict):
        self._t = t
        self.outer.config(bg=t["bg"])
        self._cv.config(bg=t["bg"])
        self.inner.config(bg=t["card_bg"])
        self._redraw()


# ── MainWindow ────────────────────────────────────────────────────────────────

class MainWindow:
    """Spotify-style single-page layout — sidebar + two-column content."""

    def __init__(self):
        self._t = DARK_THEME
        self._scheduler = Scheduler()
        self._log_filter = "ALL"
        self._filter_btns: list[FilterButton] = []
        self._is_running = False
        self._stored_headers: dict = {}
        self._stored_body: str = ""
        self._profile_widgets: list = []
        self._panels: list[RoundedPanel] = []
        self._hero_img = None
        self._sb_icon_img = None

        self._root = tk.Tk()
        self._setup_window()
        self._setup_ttk()
        self._load_images()
        self._build_ui()
        self._wire_scheduler()
        self._apply_theme()

    # ── bootstrap ─────────────────────────────────────────────────────────────

    def _setup_window(self):
        r = self._root
        r.title("おはよう — The API Waker")
        r.geometry("1140x760")
        r.minsize(920, 640)
        r.configure(bg=self._t["bg"])
        try:
            img = tk.PhotoImage(file=_ICON_PATH)
            r.iconphoto(True, img)
        except Exception:
            pass

    def _setup_ttk(self):
        s = ttk.Style(self._root)
        s.theme_use("clam")
        t = self._t
        s.configure("Modern.TCombobox",
                     fieldbackground=t["input_bg"], background=t["input_bg"],
                     foreground=t["fg"], selectbackground=t["sel_bg"],
                     selectforeground=t["fg"], arrowcolor=t["accent"],
                     borderwidth=0, padding=8)
        s.map("Modern.TCombobox",
              fieldbackground=[("readonly", t["input_bg"])],
              foreground=[("readonly", t["fg"])])
        s.configure("Vertical.TScrollbar",
                     background=t["scroll_fg"], troughcolor=t["scroll_bg"],
                     arrowcolor=t["scroll_fg"], borderwidth=0)

    def _load_images(self):
        if not HAS_PIL:
            return
        try:
            im = Image.open(_ICON_PATH).convert("RGBA")
            self._hero_img    = ImageTk.PhotoImage(im.resize((72, 72),  Image.LANCZOS))
            self._sb_icon_img = ImageTk.PhotoImage(im.resize((36, 36),  Image.LANCZOS))
        except Exception:
            self._hero_img = self._sb_icon_img = None

    # ── top-level layout ──────────────────────────────────────────────────────

    def _build_ui(self):
        self._root_frame = tk.Frame(self._root, bg=self._t["bg"])
        self._root_frame.pack(fill=tk.BOTH, expand=True)
        self._build_sidebar()
        self._build_content()

    # ── sidebar ───────────────────────────────────────────────────────────────

    def _build_sidebar(self):
        t = self._t

        self._sidebar = tk.Frame(self._root_frame, bg=t["sidebar_bg"], width=230)
        self._sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self._sidebar.pack_propagate(False)

        self._sb_sep = tk.Frame(self._root_frame, bg=t["border"], width=1)
        self._sb_sep.pack(side=tk.LEFT, fill=tk.Y)

        # ── brand ──────────────────────────────────────────────────────────────
        brand = tk.Frame(self._sidebar, bg=t["sidebar_bg"], padx=20, pady=22)
        brand.pack(fill=tk.X)
        self._sb_brand = brand

        if self._sb_icon_img:
            self._sb_icon = tk.Label(brand, image=self._sb_icon_img,
                                      bg=t["sidebar_bg"], bd=0)
            self._sb_icon.pack(anchor="w", pady=(0, 10))
        else:
            self._sb_icon = None

        self._sb_title = tk.Label(brand, text="おはよう",
                                   font=("Helvetica", 20, "bold"),
                                   bg=t["sidebar_bg"], fg=t["accent"])
        self._sb_title.pack(anchor="w")

        self._sb_sub = tk.Label(brand, text="API Waker",
                                 font=("Helvetica", 9),
                                 bg=t["sidebar_bg"], fg=t["text_secondary"])
        self._sb_sub.pack(anchor="w", pady=(2, 0))

        # ── divider ────────────────────────────────────────────────────────────
        self._sb_div1 = tk.Frame(self._sidebar, bg=t["border"], height=1)
        self._sb_div1.pack(fill=tk.X, padx=16, pady=(0, 14))

        # ── profiles header ────────────────────────────────────────────────────
        phdr = tk.Frame(self._sidebar, bg=t["sidebar_bg"], padx=20)
        phdr.pack(fill=tk.X)
        self._sb_phdr = phdr

        self._sb_plbl = tk.Label(phdr, text="SAVED PROFILES",
                                  font=("Helvetica", 8, "bold"),
                                  bg=t["sidebar_bg"], fg=t["text_muted"])
        self._sb_plbl.pack(side=tk.LEFT, pady=(0, 10))

        # ── scrollable profile list ────────────────────────────────────────────
        plist_wrap = tk.Frame(self._sidebar, bg=t["sidebar_bg"])
        plist_wrap.pack(fill=tk.BOTH, expand=True, padx=8)
        self._sb_plist_wrap = plist_wrap

        self._prof_canvas = tk.Canvas(plist_wrap, bg=t["sidebar_bg"],
                                       highlightthickness=0, bd=0)
        self._prof_sb = ttk.Scrollbar(plist_wrap, orient="vertical",
                                       command=self._prof_canvas.yview,
                                       style="Vertical.TScrollbar")
        self._prof_canvas.configure(yscrollcommand=self._prof_sb.set)
        self._prof_sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._prof_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._prof_list = tk.Frame(self._prof_canvas, bg=t["sidebar_bg"])
        self._prof_list_win = self._prof_canvas.create_window(
            (0, 0), window=self._prof_list, anchor="nw")

        self._prof_list.bind("<Configure>", lambda _:
            self._prof_canvas.configure(
                scrollregion=self._prof_canvas.bbox("all")))
        self._prof_canvas.bind("<Configure>", lambda e:
            self._prof_canvas.itemconfig(self._prof_list_win, width=e.width))

        # ── bottom: save + theme ───────────────────────────────────────────────
        self._sb_div2 = tk.Frame(self._sidebar, bg=t["border"], height=1)
        self._sb_div2.pack(fill=tk.X, padx=16, side=tk.BOTTOM, pady=(0, 0))

        bottom = tk.Frame(self._sidebar, bg=t["sidebar_bg"], padx=16, pady=14)
        bottom.pack(fill=tk.X, side=tk.BOTTOM)
        self._sb_bottom = bottom

        self._save_prof_btn = ActionButton(
            bottom, text="＋  Save Profile",
            command=self._save_profile,
            bg=t["filter_bg"], hover_bg=t["card_border"],
            fg=t["text_secondary"],
            disabled_bg=t["disabled"], disabled_fg=t["disabled_fg"],
            font=("Helvetica", 9, "bold"), padx=10, pady=7)
        self._save_prof_btn.pack(fill=tk.X, pady=(0, 10))

        theme_row = tk.Frame(bottom, bg=t["sidebar_bg"])
        theme_row.pack(fill=tk.X)
        self._sb_theme_row = theme_row

        self._theme_lbl = tk.Label(theme_row, text="Theme",
                                    font=("Helvetica", 9),
                                    bg=t["sidebar_bg"], fg=t["text_secondary"])
        self._theme_lbl.pack(side=tk.LEFT)

        self._theme_btn = tk.Label(theme_row, text="☀️",
                                    font=("Helvetica", 14),
                                    bg=t["sidebar_bg"], cursor="hand2")
        self._theme_btn.pack(side=tk.RIGHT)
        self._theme_btn.bind("<Button-1>", lambda _: self._toggle_theme())

        self._refresh_profiles_list()

    # ── main content area ─────────────────────────────────────────────────────

    def _build_content(self):
        t = self._t

        self._content = tk.Frame(self._root_frame, bg=t["bg"])
        self._content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Star field background
        self._stars = StarField(self._content, theme=t, num_stars=110, seed=7)
        self._stars.place(x=0, y=0, relwidth=1, relheight=1)

        # Two-column holder (sits above stars via .lift())
        cols_holder = tk.Frame(self._content, bg=t["bg"])
        cols_holder.place(x=16, y=16, relwidth=1, relheight=1,
                          width=-32, height=-32)
        self._cols_holder = cols_holder

        left_col = tk.Frame(cols_holder, bg=t["bg"])
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        self._left_col = left_col

        right_col = tk.Frame(cols_holder, bg=t["bg"])
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0))
        self._right_col = right_col

        self._build_wakeup_panel()
        self._build_activity_panel()

        # Lift col holder above stars
        cols_holder.lift()

    # ── Wake Up panel ─────────────────────────────────────────────────────────

    def _build_wakeup_panel(self):
        t = self._t

        wu = RoundedPanel(self._left_col, t, radius=16)
        wu.outer.pack(fill=tk.BOTH, expand=True)
        self._wu_panel = wu
        self._panels.append(wu)

        pad = tk.Frame(wu.inner, bg=t["card_bg"], padx=26, pady=22)
        pad.pack(fill=tk.BOTH, expand=True)
        self._wu_pad = pad

        # ── hero row ──────────────────────────────────────────────────────────
        hero = tk.Frame(pad, bg=t["card_bg"])
        hero.pack(fill=tk.X, pady=(0, 18))
        self._wu_hero = hero

        if self._hero_img:
            self._wu_icon_lbl = tk.Label(hero, image=self._hero_img,
                                          bg=t["card_bg"], bd=0)
            self._wu_icon_lbl.pack(side=tk.LEFT, padx=(0, 18))
        else:
            self._wu_icon_lbl = None

        tcol = tk.Frame(hero, bg=t["card_bg"])
        tcol.pack(side=tk.LEFT)
        self._wu_tcol = tcol

        self._wu_title = tk.Label(tcol, text="Wake Up API",
                                   font=("Helvetica", 22, "bold"),
                                   bg=t["card_bg"], fg=t["fg"])
        self._wu_title.pack(anchor="w")

        self._wu_sub = tk.Label(tcol, text="Schedule HTTP requests on repeat",
                                 font=("Helvetica", 10),
                                 bg=t["card_bg"], fg=t["text_secondary"])
        self._wu_sub.pack(anchor="w", pady=(3, 0))

        # ── URL ───────────────────────────────────────────────────────────────
        self._url_entry = PlaceholderEntry(
            pad, label="TARGET URL",
            placeholder="https://example.com/api/ping",
            theme=t, font=("Helvetica", 11))
        self._url_entry.pack(fill=tk.X, pady=(0, 14))

        # ── timing row ────────────────────────────────────────────────────────
        timing = tk.Frame(pad, bg=t["card_bg"])
        timing.pack(fill=tk.X, pady=(0, 14))
        self._wu_timing = timing
        timing.columnconfigure(0, weight=2, minsize=110)
        timing.columnconfigure(1, weight=1, minsize=88)
        timing.columnconfigure(2, weight=1, minsize=88)

        method_col = tk.Frame(timing, bg=t["card_bg"])
        method_col.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        self._wu_method_col = method_col

        self._wu_method_lbl = tk.Label(method_col, text="METHOD",
                                        font=("Helvetica", 8, "bold"),
                                        bg=t["card_bg"], fg=t["text_secondary"])
        self._wu_method_lbl.pack(anchor="w", pady=(0, 4))

        self._method_var = tk.StringVar(value="GET")
        self._method_border = tk.Frame(method_col, bg=t["input_border"],
                                        padx=1, pady=1)
        self._method_border.pack(fill=tk.X)
        mi = tk.Frame(self._method_border, bg=t["input_bg"])
        mi.pack(fill=tk.X)
        self._method_inner = mi
        self._method_cb = ttk.Combobox(mi, textvariable=self._method_var,
                                        values=_METHODS, state="readonly",
                                        style="Modern.TCombobox",
                                        font=("Helvetica", 10, "bold"))
        self._method_cb.pack(fill=tk.X, padx=2, pady=4)

        self._interval_entry = MiniEntry(timing, label="EVERY (s)",
                                          placeholder="5", theme=t)
        self._interval_entry.grid(row=0, column=1, padx=(0, 10), sticky="nsew")

        self._stop_entry = MiniEntry(timing, label="UNTIL  HH:MM",
                                      placeholder="23:59", theme=t)
        self._stop_entry.grid(row=0, column=2, sticky="nsew")

        # ── optional links ────────────────────────────────────────────────────
        extras = tk.Frame(pad, bg=t["card_bg"])
        extras.pack(fill=tk.X, pady=(0, 18))
        self._wu_extras = extras

        self._headers_btn = tk.Label(extras, text="✎  Headers",
                                      font=("Helvetica", 9),
                                      bg=t["card_bg"], fg=t["text_secondary"],
                                      cursor="hand2")
        self._headers_btn.pack(side=tk.LEFT, padx=(0, 18))
        self._headers_btn.bind("<Button-1>", lambda _: self._open_headers_dialog())

        self._body_btn = tk.Label(extras, text="✎  Body",
                                   font=("Helvetica", 9),
                                   bg=t["card_bg"], fg=t["text_secondary"],
                                   cursor="hand2")
        self._body_btn.pack(side=tk.LEFT)
        self._body_btn.bind("<Button-1>", lambda _: self._open_body_dialog())

        self._stored_headers: dict = {}
        self._stored_body: str = ""

        # ── Wake Up button ────────────────────────────────────────────────────
        self._wake_btn = tk.Label(pad, text="▶   WAKE UP API",
                                   font=("Helvetica", 13, "bold"),
                                   bg=t["accent"], fg=t["bg"],
                                   padx=32, pady=16, cursor="hand2")
        self._wake_btn.pack(fill=tk.X, pady=(0, 14))
        self._wake_btn.bind("<Enter>", lambda _: self._wake_btn.config(
            bg=self._t["accent_hover"]))
        self._wake_btn.bind("<Leave>", lambda _: self._wake_btn.config(
            bg=self._t["accent"] if not self._is_running
              else self._t["danger"]))
        self._wake_btn.bind("<Button-1>", lambda _: self._on_wake_click())

        # ── status ────────────────────────────────────────────────────────────
        st_row = tk.Frame(pad, bg=t["card_bg"])
        st_row.pack(fill=tk.X, pady=(0, 8))
        self._wu_st_row = st_row

        self._wu_dot = AnimatedDot(st_row, color=t["text_muted"],
                                    size=10, bg=t["card_bg"])
        self._wu_dot.pack(side=tk.LEFT, padx=(0, 8))

        self._wu_status = tk.Label(st_row, text="Ready to wake up an API.",
                                    font=("Helvetica", 10),
                                    bg=t["card_bg"], fg=t["text_secondary"])
        self._wu_status.pack(side=tk.LEFT)

        self._wu_bar = CountdownBar(pad, bg=t["filter_bg"],
                                     fill=t["accent"], height=5)
        self._wu_bar.pack(fill=tk.X)

    # ── Activity panel ────────────────────────────────────────────────────────

    def _build_activity_panel(self):
        t = self._t

        act = RoundedPanel(self._right_col, t, radius=16)
        act.outer.pack(fill=tk.BOTH, expand=True)
        self._act_panel = act
        self._panels.append(act)

        wrap = tk.Frame(act.inner, bg=t["card_bg"], padx=20, pady=20)
        wrap.pack(fill=tk.BOTH, expand=True)
        self._act_wrap = wrap

        # ── title row ─────────────────────────────────────────────────────────
        trow = tk.Frame(wrap, bg=t["card_bg"])
        trow.pack(fill=tk.X, pady=(0, 14))
        self._act_trow = trow

        self._act_title = tk.Label(trow, text="Activity",
                                    font=("Helvetica", 18, "bold"),
                                    bg=t["card_bg"], fg=t["fg"])
        self._act_title.pack(side=tk.LEFT)

        self._export_btn = ActionButton(
            trow, text="⬇ Export", command=self._export_log,
            bg=t["filter_bg"], hover_bg=t["border"], fg=t["text_secondary"],
            disabled_bg=t["disabled"], disabled_fg=t["disabled_fg"],
            font=("Helvetica", 8, "bold"), padx=8, pady=4)
        self._export_btn.pack(side=tk.RIGHT, padx=(4, 0))

        self._clear_btn = ActionButton(
            trow, text="🗑 Clear", command=self._on_clear,
            bg=t["filter_bg"], hover_bg=t["border"], fg=t["text_secondary"],
            disabled_bg=t["disabled"], disabled_fg=t["disabled_fg"],
            font=("Helvetica", 8, "bold"), padx=8, pady=4)
        self._clear_btn.pack(side=tk.RIGHT, padx=(4, 0))

        # ── stats ─────────────────────────────────────────────────────────────
        stats = tk.Frame(wrap, bg=t["card_bg"])
        stats.pack(fill=tk.X, pady=(0, 14))
        self._act_stats = stats

        specs = [("Total",   "—",   t["accent"]),
                 ("Success", "—%",  t["success"]),
                 ("Avg",     "—ms", t["warning"]),
                 ("Status",  "—",   t["text_secondary"])]
        self._stat_cards: list[StatsCard] = []
        for i, (lbl, val, col) in enumerate(specs):
            c = StatsCard(stats, label=lbl, value=val, color=col, theme=t)
            c.grid(row=0, column=i, padx=(0 if i == 0 else 6, 0), sticky="nsew")
            stats.columnconfigure(i, weight=1)
            self._stat_cards.append(c)

        # ── filters ───────────────────────────────────────────────────────────
        frow = tk.Frame(wrap, bg=t["card_bg"])
        frow.pack(fill=tk.X, pady=(0, 10))
        self._act_frow = frow

        for fname in ["ALL", "2xx", "3xx", "4xx", "5xx", "ERR"]:
            btn = FilterButton(frow, text=fname,
                                on_toggle=self._on_filter,
                                active=(fname == "ALL"), theme=t)
            btn.pack(side=tk.LEFT, padx=(0, 4))
            btn._label = fname  # type: ignore
            self._filter_btns.append(btn)

        # ── log ───────────────────────────────────────────────────────────────
        log_outer = tk.Frame(wrap, bg=t["card_border"])
        log_outer.pack(fill=tk.BOTH, expand=True)
        self._log_outer = log_outer

        log_inner = tk.Frame(log_outer, bg=t["log_bg"])
        log_inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        self._log_inner = log_inner

        vsb = ttk.Scrollbar(log_inner, orient="vertical",
                             style="Vertical.TScrollbar")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self._log = tk.Text(log_inner, font=("Courier", 9),
                             bg=t["log_bg"], fg=t["fg"],
                             insertbackground=t["cursor"],
                             selectbackground=t["sel_bg"],
                             relief=tk.FLAT, bd=0,
                             state=tk.DISABLED, wrap=tk.WORD,
                             yscrollcommand=vsb.set, padx=12, pady=10)
        self._log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.config(command=self._log.yview)

        for tag in ("2xx", "3xx", "4xx", "5xx", "error",
                    "info", "ts", "method", "ms"):
            self._log.tag_config(tag, foreground=t[f"tag_{tag}"])

    # ── sidebar profiles ──────────────────────────────────────────────────────

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
            empty = tk.Label(self._prof_list,
                              text="No profiles yet.\n\nConfigure a request\nand click  ＋ Save.",
                              font=("Helvetica", 9),
                              bg=t["sidebar_bg"], fg=t["text_muted"],
                              justify="center", pady=20)
            empty.pack(fill=tk.X, padx=8)
            self._profile_widgets.append(empty)
            return

        for name in names:
            data = load_profile(name)
            item = self._build_profile_item(name, data)
            item.pack(fill=tk.X, pady=(0, 4), padx=4)
            self._profile_widgets.append(item)

    def _build_profile_item(self, name: str, data: dict) -> tk.Frame:
        t = self._t
        outer = tk.Frame(self._prof_list, bg=t["sidebar_bg"], cursor="hand2")
        inner = tk.Frame(outer, bg=t["card_bg"], padx=12, pady=10)
        inner.pack(fill=tk.X)

        row1 = tk.Frame(inner, bg=t["card_bg"])
        row1.pack(fill=tk.X)

        play = tk.Label(row1, text="▶", font=("Helvetica", 7),
                         bg=t["card_bg"], fg=t["accent"])
        play.pack(side=tk.LEFT, padx=(0, 6))

        nlbl = tk.Label(row1, text=name, font=("Helvetica", 9, "bold"),
                         bg=t["card_bg"], fg=t["fg"])
        nlbl.pack(side=tk.LEFT)

        del_btn = tk.Label(row1, text="✕", font=("Helvetica", 9),
                            bg=t["card_bg"], fg=t["text_muted"], cursor="hand2")
        del_btn.pack(side=tk.RIGHT)
        del_btn.bind("<Button-1>",
                     lambda _, n=name: self._delete_profile_by_name(n))

        meta = tk.Label(inner,
                         text=f"{data.get('method','GET')} · every {data.get('interval','?')}s",
                         font=("Helvetica", 8),
                         bg=t["card_bg"], fg=t["text_secondary"])
        meta.pack(anchor="w", pady=(2, 0))

        # click = load profile
        click_handler = lambda _, n=name: self._load_profile_by_name(n)
        for w in (outer, inner, row1, play, nlbl, meta):
            w.bind("<Button-1>", click_handler)

        # hover
        hover_bg = t["filter_bg"]
        norm_bg  = t["card_bg"]
        all_inner = [inner, row1, play, nlbl, meta, del_btn]

        def _enter(_):
            for w in all_inner:
                try:
                    w.config(bg=hover_bg)
                except Exception:
                    pass

        def _leave(_):
            for w in all_inner:
                try:
                    w.config(bg=norm_bg)
                except Exception:
                    pass

        outer.bind("<Enter>", _enter)
        inner.bind("<Enter>", _enter)
        outer.bind("<Leave>", _leave)
        inner.bind("<Leave>", _leave)

        return outer

    def _load_profile_by_name(self, name: str):
        data = load_profile(name)
        if not data:
            return
        self._url_entry.set(data.get("url", ""))
        self._method_var.set(data.get("method", "GET"))
        self._interval_entry.set(data.get("interval", ""))
        self._stop_entry.set(data.get("stop", ""))
        self._stored_headers = data.get("headers", {})
        self._stored_body    = data.get("body", "")
        self._update_extra_indicators()

    def _delete_profile_by_name(self, name: str):
        if messagebox.askyesno("Delete Profile", f"Delete '{name}'?"):
            delete_profile(name)
            self._refresh_profiles_list()

    # ── dialogs ───────────────────────────────────────────────────────────────

    def _open_headers_dialog(self):
        t = self._t
        dlg = tk.Toplevel(self._root)
        dlg.title("HTTP Headers")
        dlg.geometry("520x420")
        dlg.configure(bg=t["bg"])
        dlg.transient(self._root)

        tk.Label(dlg, text="HTTP Headers", font=("Helvetica", 12, "bold"),
                 bg=t["bg"], fg=t["fg"]).pack(anchor="w", padx=20, pady=(16, 4))
        tk.Label(dlg, text="Key / value pairs sent with every request.",
                 font=("Helvetica", 9), bg=t["bg"],
                 fg=t["text_secondary"]).pack(anchor="w", padx=20)

        wrap = tk.Frame(dlg, bg=t["card_bg"])
        wrap.pack(fill=tk.BOTH, expand=True, padx=20, pady=12)
        tk.Frame(wrap, bg=t["accent"], height=2).pack(fill=tk.X)
        body = tk.Frame(wrap, bg=t["card_bg"], padx=14, pady=12)
        body.pack(fill=tk.BOTH, expand=True)

        editor = HeadersEditor(body, theme=t)
        editor.pack(fill=tk.BOTH, expand=True)
        editor.set_headers(self._stored_headers)

        btn_row = tk.Frame(dlg, bg=t["bg"])
        btn_row.pack(fill=tk.X, padx=20, pady=(0, 16))

        def _save():
            self._stored_headers = editor.get_headers()
            self._update_extra_indicators()
            dlg.destroy()

        ActionButton(btn_row, text="Save", command=_save,
                     bg=t["accent"], hover_bg=t["accent_hover"], fg=t["bg"],
                     disabled_bg=t["disabled"], disabled_fg=t["disabled_fg"],
                     font=("Helvetica", 9, "bold"), padx=18, pady=8
                     ).pack(side=tk.RIGHT)
        ActionButton(btn_row, text="Cancel", command=dlg.destroy,
                     bg=t["filter_bg"], hover_bg=t["border"],
                     fg=t["text_secondary"],
                     disabled_bg=t["disabled"], disabled_fg=t["disabled_fg"],
                     font=("Helvetica", 9, "bold"), padx=18, pady=8
                     ).pack(side=tk.RIGHT, padx=(0, 8))

    def _open_body_dialog(self):
        t = self._t
        dlg = tk.Toplevel(self._root)
        dlg.title("Request Body")
        dlg.geometry("520x420")
        dlg.configure(bg=t["bg"])
        dlg.transient(self._root)

        tk.Label(dlg, text="Request Body", font=("Helvetica", 12, "bold"),
                 bg=t["bg"], fg=t["fg"]).pack(anchor="w", padx=20, pady=(16, 4))
        tk.Label(dlg, text="Sent only with POST / PUT / PATCH.",
                 font=("Helvetica", 9), bg=t["bg"],
                 fg=t["text_secondary"]).pack(anchor="w", padx=20)

        wrap = tk.Frame(dlg, bg=t["card_bg"])
        wrap.pack(fill=tk.BOTH, expand=True, padx=20, pady=12)
        tk.Frame(wrap, bg=t["accent"], height=2).pack(fill=tk.X)
        bwrap = tk.Frame(wrap, bg=t["card_bg"], padx=1, pady=1)
        bwrap.pack(fill=tk.BOTH, expand=True)

        text = tk.Text(bwrap, font=("Courier", 10),
                        bg=t["input_bg"], fg=t["fg"],
                        insertbackground=t["cursor"],
                        relief=tk.FLAT, bd=0, wrap=tk.WORD,
                        selectbackground=t["sel_bg"])
        text.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        if self._stored_body:
            text.insert("1.0", self._stored_body)

        btn_row = tk.Frame(dlg, bg=t["bg"])
        btn_row.pack(fill=tk.X, padx=20, pady=(0, 16))

        def _save():
            self._stored_body = text.get("1.0", tk.END).strip()
            self._update_extra_indicators()
            dlg.destroy()

        ActionButton(btn_row, text="Save", command=_save,
                     bg=t["accent"], hover_bg=t["accent_hover"], fg=t["bg"],
                     disabled_bg=t["disabled"], disabled_fg=t["disabled_fg"],
                     font=("Helvetica", 9, "bold"), padx=18, pady=8
                     ).pack(side=tk.RIGHT)
        ActionButton(btn_row, text="Cancel", command=dlg.destroy,
                     bg=t["filter_bg"], hover_bg=t["border"],
                     fg=t["text_secondary"],
                     disabled_bg=t["disabled"], disabled_fg=t["disabled_fg"],
                     font=("Helvetica", 9, "bold"), padx=18, pady=8
                     ).pack(side=tk.RIGHT, padx=(0, 8))

    def _update_extra_indicators(self):
        t = self._t
        has_h = bool(self._stored_headers)
        has_b = bool(self._stored_body)
        self._headers_btn.config(
            text=f"✎  Headers · {len(self._stored_headers)}" if has_h
                 else "✎  Headers",
            fg=t["accent"] if has_h else t["text_secondary"])
        self._body_btn.config(
            text="✎  Body · set" if has_b else "✎  Body",
            fg=t["accent"] if has_b else t["text_secondary"])

    # ── theme ─────────────────────────────────────────────────────────────────

    def _toggle_theme(self):
        self._t = LIGHT_THEME if self._t["name"] == "dark" else DARK_THEME
        self._theme_btn.config(
            text="🌙" if self._t["name"] == "light" else "☀️")
        self._apply_theme()

    def _apply_theme(self):
        t = self._t
        self._root.configure(bg=t["bg"])
        self._root_frame.config(bg=t["bg"])

        # Sidebar
        for w in (self._sidebar, self._sb_brand, self._sb_phdr,
                  self._sb_plist_wrap, self._sb_bottom, self._sb_theme_row):
            w.config(bg=t["sidebar_bg"])
        self._sb_sep.config(bg=t["border"])
        self._sb_div1.config(bg=t["border"])
        self._sb_div2.config(bg=t["border"])
        self._sb_title.config(bg=t["sidebar_bg"], fg=t["accent"])
        self._sb_sub.config(bg=t["sidebar_bg"], fg=t["text_secondary"])
        self._sb_plbl.config(bg=t["sidebar_bg"], fg=t["text_muted"])
        if self._sb_icon:
            self._sb_icon.config(bg=t["sidebar_bg"])
        self._theme_lbl.config(bg=t["sidebar_bg"], fg=t["text_secondary"])
        self._theme_btn.config(bg=t["sidebar_bg"])
        self._save_prof_btn.update_colors(t["filter_bg"], t["card_border"],
                                           t["text_secondary"],
                                           t["disabled"], t["disabled_fg"])
        self._prof_canvas.config(bg=t["sidebar_bg"])
        self._prof_list.config(bg=t["sidebar_bg"])
        self._refresh_profiles_list()

        # TTK
        s = ttk.Style()
        s.configure("Modern.TCombobox",
                     fieldbackground=t["input_bg"], background=t["input_bg"],
                     foreground=t["fg"], selectbackground=t["sel_bg"],
                     selectforeground=t["fg"], arrowcolor=t["accent"])
        s.map("Modern.TCombobox",
              fieldbackground=[("readonly", t["input_bg"])],
              foreground=[("readonly", t["fg"])])
        s.configure("Vertical.TScrollbar",
                     background=t["scroll_fg"], troughcolor=t["scroll_bg"],
                     arrowcolor=t["scroll_fg"])

        # Content
        self._content.config(bg=t["bg"])
        self._stars.apply_theme(t)
        self._cols_holder.config(bg=t["bg"])
        self._left_col.config(bg=t["bg"])
        self._right_col.config(bg=t["bg"])

        # Wake Up panel
        self._wu_panel.apply_theme(t)
        for w in (self._wu_pad, self._wu_hero, self._wu_tcol):
            w.config(bg=t["card_bg"])
        self._wu_title.config(bg=t["card_bg"], fg=t["fg"])
        self._wu_sub.config(bg=t["card_bg"], fg=t["text_secondary"])
        if self._wu_icon_lbl:
            self._wu_icon_lbl.config(bg=t["card_bg"])
        self._url_entry.apply_theme(t)
        self._wu_timing.config(bg=t["card_bg"])
        self._wu_method_col.config(bg=t["card_bg"])
        self._wu_method_lbl.config(bg=t["card_bg"], fg=t["text_secondary"])
        self._method_border.config(bg=t["input_border"])
        self._method_inner.config(bg=t["input_bg"])
        self._interval_entry.apply_theme(t)
        self._stop_entry.apply_theme(t)
        self._wu_extras.config(bg=t["card_bg"])
        self._update_extra_indicators()
        if self._is_running:
            self._wake_btn.config(bg=t["danger"], fg="white")
        else:
            self._wake_btn.config(bg=t["accent"], fg=t["bg"])
        self._wu_st_row.config(bg=t["card_bg"])
        self._wu_dot.set_bg(t["card_bg"])
        self._wu_status.config(bg=t["card_bg"], fg=t["text_secondary"])
        self._wu_bar.update_theme(t["filter_bg"], t["accent"])

        # Activity panel
        self._act_panel.apply_theme(t)
        for w in (self._act_wrap, self._act_trow, self._act_stats,
                  self._act_frow):
            w.config(bg=t["card_bg"])
        self._act_title.config(bg=t["card_bg"], fg=t["fg"])
        self._export_btn.update_colors(t["filter_bg"], t["border"],
                                        t["text_secondary"],
                                        t["disabled"], t["disabled_fg"])
        self._clear_btn.update_colors(t["filter_bg"], t["border"],
                                       t["text_secondary"],
                                       t["disabled"], t["disabled_fg"])
        for c in self._stat_cards:
            c.apply_theme(t)
        for fb in self._filter_btns:
            fb.apply_theme(t)
        self._log_outer.config(bg=t["card_border"])
        self._log_inner.config(bg=t["log_bg"])
        self._log.config(bg=t["log_bg"], fg=t["fg"],
                          insertbackground=t["cursor"],
                          selectbackground=t["sel_bg"])
        for tag in ("2xx", "3xx", "4xx", "5xx", "error",
                    "info", "ts", "method", "ms"):
            self._log.tag_config(tag, foreground=t[f"tag_{tag}"])

    # ── scheduler wiring ──────────────────────────────────────────────────────

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

    # ── UI-thread handlers ────────────────────────────────────────────────────

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
        self._wu_bar.set_progress(remaining / total)
        self._wu_status.config(text=f"Next request in {remaining}s…",
                                fg=self._t["text_secondary"])

    def _handle_completed(self, stop_time):
        msg = f"Completed at {stop_time.strftime('%H:%M')}"
        self._wu_status.config(text=msg, fg=self._t["success"])
        self._wu_dot.set_color(self._t["success"])
        self._wu_bar.set_progress(0.0)

    def _handle_finished(self):
        self._set_running(False)
        self._wu_dot.stop()
        self._wu_bar.set_progress(0.0)
        if "Running" in (self._wu_status.cget("text") or ""):
            self._wu_status.config(text="Stopped", fg=self._t["danger"])

    def _handle_error_event(self, msg: str):
        self._wu_status.config(text=f"Error: {msg}", fg=self._t["danger"])

    # ── log helpers ───────────────────────────────────────────────────────────

    def _matches_filter(self, tag: str) -> bool:
        f = self._log_filter
        if f == "ALL":   return True
        if f == "ERR":   return tag == "error"
        return tag == f

    def _append_log(self, line: str, tag: str):
        self._log.config(state=tk.NORMAL)
        self._log.insert(tk.END, line + "\n", tag)
        self._log.see(tk.END)
        self._log.config(state=tk.DISABLED)

    def _update_stats(self):
        s = self._scheduler.stats
        self._stat_cards[0].set_value(str(s["total"]))
        self._stat_cards[1].set_value(f"{s['success_pct']:.1f}%")
        self._stat_cards[2].set_value(f"{s['avg_ms']:.0f}ms")
        st = s["last_status"]
        self._stat_cards[3].set_value(str(st) if st else "—")

    # ── actions ───────────────────────────────────────────────────────────────

    def _set_running(self, running: bool):
        self._is_running = running
        t = self._t
        if running:
            self._wake_btn.config(text="⏹  STOP  WAKING",
                                   bg=t["danger"], fg="white")
        else:
            self._wake_btn.config(text="▶   WAKE UP API",
                                   bg=t["accent"], fg=t["bg"])

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
        self._wu_status.config(text="Running…", fg=self._t["success"])
        self._wu_dot.set_color(self._t["success"])
        self._wu_dot.start()
        self._wu_bar.set_progress(1.0)
        self._scheduler.start(url, method, headers, body, interval, stop_time)

    def _on_stop(self):
        self._scheduler.stop()
        self._wu_status.config(text="Stopped", fg=self._t["danger"])
        self._wu_dot.set_color(self._t["danger"])
        self._wu_dot.stop()
        self._wu_bar.set_progress(0.0)

    def _on_clear(self):
        self._log.config(state=tk.NORMAL)
        self._log.delete("1.0", tk.END)
        self._log.config(state=tk.DISABLED)
        self._scheduler.reset_stats()
        for i, v in enumerate(["—", "—%", "—ms", "—"]):
            self._stat_cards[i].set_value(v)

    def _on_filter(self, clicked: FilterButton):
        for btn in self._filter_btns:
            btn.set_active(btn is clicked)
        self._log_filter = clicked._label  # type: ignore

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
        name = simpledialog.askstring(
            "Save Profile", "Profile name:", parent=self._root)
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

    # ── run ───────────────────────────────────────────────────────────────────

    def run(self):
        self._root.mainloop()


def run_app():
    app = MainWindow()
    app.run()
