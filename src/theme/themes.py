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

# Deep midnight blue — electric night sky palette
DARK_THEME = {
    "name": "dark",
    # Backgrounds — deep midnight blue
    "bg":           "#080E1C",
    "panel_bg":     "#0B1526",
    "sidebar_bg":   "#060C18",
    "card_bg":      "#0E1B30",
    "input_bg":     "#0A1422",
    "log_bg":       "#080E1C",
    # Borders — subtle blue glow
    "input_border": "#1A3058",
    "border":       "#12284A",
    "card_border":  "#1E3562",
    # Text
    "fg":           "#E0EAFF",
    "text_secondary":"#6080A8",
    "text_muted":   "#2C4060",
    # Accent — golden star (brand identity against deep blue)
    "accent":       "#FFD166",
    "accent_hover": "#F5B800",
    "accent_bg":    "#1A1200",
    # Header gradient — warm sunrise
    "grad_start":   "#FF7B3E",
    "grad_end":     "#F5A623",
    # Success — aqua
    "success":      "#4DD9C0",
    "success_hover":"#38C5AC",
    "success_bg":   "#091C1A",
    # Warning — amber
    "warning":      "#F5A623",
    "warning_bg":   "#1A1000",
    # Danger — soft rose
    "danger":       "#FF6B9D",
    "danger_hover": "#FF4B8A",
    "danger_bg":    "#1A0810",
    # Disabled
    "disabled":     "#12284A",
    "disabled_fg":  "#2C4060",
    # Scrollbar
    "scroll_bg":    "#0B1526",
    "scroll_fg":    "#1A3058",
    # Filter buttons
    "filter_bg":    "#0E1B30",
    "filter_act":   "#FFD166",
    # Log tag colours
    "tag_2xx":      "#4DD9C0",
    "tag_3xx":      "#F5A623",
    "tag_4xx":      "#FF9F43",
    "tag_5xx":      "#FF6B9D",
    "tag_error":    "#FF4B8A",
    "tag_info":     "#74B9FF",
    "tag_ts":       "#2C4060",
    "tag_method":   "#C084FC",
    "tag_ms":       "#6080A8",
    "cursor":       "#FFD166",
    "sel_bg":       "#1A3058",
}

def T(key: str) -> tuple:
    """Return (light_color, dark_color) tuple for CTk auto-switching widgets."""
    return (LIGHT_THEME[key], DARK_THEME[key])


# Light morning — clean blue-white palette
LIGHT_THEME = {
    "name": "light",
    # Backgrounds
    "bg":           "#EEF2FF",
    "panel_bg":     "#FFFFFF",
    "sidebar_bg":   "#E4EAFF",
    "card_bg":      "#FFFFFF",
    "input_bg":     "#F4F7FF",
    "log_bg":       "#F8FAFF",
    # Borders
    "input_border": "#B8C8E8",
    "border":       "#CAD6F0",
    "card_border":  "#B8C8E8",
    # Text
    "fg":           "#0A1628",
    "text_secondary":"#486080",
    "text_muted":   "#90A8C8",
    # Accent — warm orange-gold
    "accent":       "#E8840A",
    "accent_hover": "#D06800",
    "accent_bg":    "#FEF0E0",
    # Header gradient
    "grad_start":   "#FF7B3E",
    "grad_end":     "#F5A623",
    # Success
    "success":      "#2EAF9C",
    "success_hover":"#259B8A",
    "success_bg":   "#E8FAF8",
    # Warning
    "warning":      "#D4881A",
    "warning_bg":   "#FEF4E0",
    # Danger
    "danger":       "#E8547A",
    "danger_hover": "#D03D62",
    "danger_bg":    "#FEECF1",
    # Disabled
    "disabled":     "#CAD6F0",
    "disabled_fg":  "#90A8C8",
    # Scrollbar
    "scroll_bg":    "#E4EAFF",
    "scroll_fg":    "#B8C8E8",
    # Filter buttons
    "filter_bg":    "#E4EAFF",
    "filter_act":   "#E8840A",
    # Log tag colours
    "tag_2xx":      "#2EAF9C",
    "tag_3xx":      "#D4881A",
    "tag_4xx":      "#E67E22",
    "tag_5xx":      "#E8547A",
    "tag_error":    "#C0392B",
    "tag_info":     "#2980B9",
    "tag_ts":       "#90A8C8",
    "tag_method":   "#7C3AED",
    "tag_ms":       "#486080",
    "cursor":       "#E8840A",
    "sel_bg":       "#C8DCFF",
}
