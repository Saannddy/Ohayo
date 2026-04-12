import sys

PLATFORM = sys.platform


def _fonts():
    if PLATFORM == "darwin":
        sans, mono = "SF Pro Display", "SF Mono"
    elif PLATFORM == "win32":
        sans, mono = "Segoe UI", "Consolas"
    else:
        sans, mono = "Ubuntu", "Ubuntu Mono"
    return sans, mono


_SANS, _MONO = _fonts()

FONTS = {
    "title_jp": (_SANS, 26, "bold"),
    "title":    (_SANS, 13, "bold"),
    "subtitle": (_SANS, 9),
    "header":   (_SANS, 11, "bold"),
    "header_sm":(_SANS, 10, "bold"),
    "body":     (_SANS, 10),
    "body_sm":  (_SANS, 9),
    "label":    (_SANS, 9, "bold"),
    "caption":  (_SANS, 8),
    "mono":     (_MONO, 9),
    "stat_num": (_SANS, 20, "bold"),
    "stat_lbl": (_SANS, 8),
    "button":   (_SANS, 10, "bold"),
    "btn_sm":   (_SANS, 9),
}

DARK_THEME = {
    "name": "dark",
    # Backgrounds
    "bg":           "#0D1117",
    "panel_bg":     "#161B22",
    "sidebar_bg":   "#0D1117",
    "card_bg":      "#161B22",
    "input_bg":     "#0D1117",
    "log_bg":       "#0D1117",
    # Borders
    "input_border": "#30363D",
    "border":       "#21262D",
    "card_border":  "#30363D",
    # Text
    "fg":           "#E6EDF3",
    "text_secondary":"#8B949E",
    "text_muted":   "#484F58",
    # Accent — sunrise orange/coral
    "accent":       "#FF7043",
    "accent_hover": "#FF5722",
    "accent_bg":    "#1A0E09",
    "grad_start":   "#FF6B35",
    "grad_end":     "#F7931E",
    # Success — spring green
    "success":      "#56E39F",
    "success_hover":"#3ECF8E",
    "success_bg":   "#0A1F14",
    # Warning
    "warning":      "#F0A500",
    "warning_bg":   "#1A1200",
    # Danger
    "danger":       "#FF4757",
    "danger_hover": "#FF6470",
    "danger_bg":    "#1A0808",
    # Disabled
    "disabled":     "#21262D",
    "disabled_fg":  "#484F58",
    # Scrollbar
    "scroll_bg":    "#161B22",
    "scroll_fg":    "#30363D",
    # Filter buttons
    "filter_bg":    "#21262D",
    "filter_act":   "#FF7043",
    # Log tag colours
    "tag_2xx":      "#56E39F",
    "tag_3xx":      "#F0A500",
    "tag_4xx":      "#FF9F43",
    "tag_5xx":      "#FF4757",
    "tag_error":    "#FF6B6B",
    "tag_info":     "#74B9FF",
    "tag_ts":       "#484F58",
    "tag_method":   "#C084FC",
    "tag_ms":       "#8B949E",
    "cursor":       "#FF7043",
    "sel_bg":       "#2D3748",
}

LIGHT_THEME = {
    "name": "light",
    # Backgrounds
    "bg":           "#FFFAF0",
    "panel_bg":     "#FFFFFF",
    "sidebar_bg":   "#FFF6EC",
    "card_bg":      "#FFFFFF",
    "input_bg":     "#FFFFFF",
    "log_bg":       "#FAFAF7",
    # Borders
    "input_border": "#DCCDB8",
    "border":       "#EDE5D8",
    "card_border":  "#EDE5D8",
    # Text
    "fg":           "#1A1A2E",
    "text_secondary":"#6B7280",
    "text_muted":   "#9CA3AF",
    # Accent
    "accent":       "#E8713C",
    "accent_hover": "#D4602C",
    "accent_bg":    "#FEF3EA",
    "grad_start":   "#FF6B35",
    "grad_end":     "#F7931E",
    # Success
    "success":      "#27AE60",
    "success_hover":"#1E8449",
    "success_bg":   "#EAFAF1",
    # Warning
    "warning":      "#D4A017",
    "warning_bg":   "#FEF9E7",
    # Danger
    "danger":       "#E74C3C",
    "danger_hover": "#C0392B",
    "danger_bg":    "#FDEDEC",
    # Disabled
    "disabled":     "#D1D5DB",
    "disabled_fg":  "#9CA3AF",
    # Scrollbar
    "scroll_bg":    "#F3EDE4",
    "scroll_fg":    "#DCCDB8",
    # Filter buttons
    "filter_bg":    "#F3EDE4",
    "filter_act":   "#E8713C",
    # Log tag colours
    "tag_2xx":      "#27AE60",
    "tag_3xx":      "#D4A017",
    "tag_4xx":      "#E67E22",
    "tag_5xx":      "#E74C3C",
    "tag_error":    "#C0392B",
    "tag_info":     "#2980B9",
    "tag_ts":       "#9CA3AF",
    "tag_method":   "#7C3AED",
    "tag_ms":       "#6B7280",
    "cursor":       "#E8713C",
    "sel_bg":       "#FDEBD0",
}
