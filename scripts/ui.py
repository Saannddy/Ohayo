import sys
import tkinter as tk
from scripts.theme import LIGHT_THEME, DARK_THEME, ModernEntry, ModernButton
from scripts.curl import start_curling, stop_curling, clear_log

TITLE_FONT = ("Segoe UI" if sys.platform == "win32" else "SF Pro Display", 24, "bold")
HEADER_FONT = ("Segoe UI" if sys.platform == "win32" else "SF Pro Display", 11, "bold")
BODY_FONT = ("Segoe UI" if sys.platform == "win32" else "SF Pro Display", 10)
SMALL_FONT = ("Segoe UI" if sys.platform == "win32" else "SF Pro Display", 9)


def apply_theme(widgets):
    theme = widgets["theme"]
    root = widgets["root"]

    root.config(bg=theme["bg"])

    for label in widgets["all_labels"]:
        label.config(bg=theme["bg"], fg=theme["fg"])

    for entry in widgets["all_entries"]:
        entry.config(
            bg=theme["input_bg"],
            fg=theme["fg"],
            insertbackground=theme["fg"],
            borderwidth=1,
            relief=tk.FLAT,
        )

    widgets["start_button"].config(
        bg=theme["success"],
        activebackground=theme["success_hover"],
    )
    widgets["stop_button"].config(
        bg=theme["danger"],
        activebackground=theme["danger_hover"],
    )
    widgets["clear_button"].config(
        bg=theme["accent"],
        activebackground=theme["accent_hover"],
    )
    widgets["theme_button"].config(
        bg=theme["text_secondary"],
        activebackground=theme["input_bg"],
        fg=theme["fg"] if widgets["is_dark_mode"] else theme["bg"],
    )

    widgets["log_text"].config(
        bg=theme["input_bg"],
        fg=theme["fg"],
        insertbackground=theme["fg"],
        relief=tk.FLAT,
        borderwidth=0,
    )

    widgets["log_text"].tag_config("green", foreground="#48BB78")
    widgets["log_text"].tag_config("orange", foreground="#ED8936")
    widgets["log_text"].tag_config("red", foreground="#F56565")
    widgets["log_text"].tag_config("error", foreground="#F56565")

    widgets["button_frame"].config(bg=theme["bg"])


def toggle_theme(widgets):
    widgets["is_dark_mode"] = not widgets["is_dark_mode"]
    widgets["theme"] = DARK_THEME if widgets["is_dark_mode"] else LIGHT_THEME
    widgets["theme_button"].config(text="☀️" if widgets["is_dark_mode"] else "🌙")
    apply_theme(widgets)


def build_main_window():
    root = tk.Tk()
    root.title("おはよう - URL Curl Scheduler")
    root.geometry("700x700")
    root.resizable(True, True)
    root.minsize(600, 500)

    widgets = {
        "root": root,
        "theme": LIGHT_THEME,
        "is_dark_mode": False,
        "all_labels": [],
        "all_entries": [],
    }

    header_frame = tk.Frame(root, bg=LIGHT_THEME["bg"])
    header_frame.pack(pady=(20, 10), padx=20, fill=tk.X)

    title = tk.Label(
        header_frame,
        text="おはよう",
        font=TITLE_FONT,
        bg=LIGHT_THEME["bg"],
        fg=LIGHT_THEME["fg"],
    )
    title.pack(side=tk.LEFT)
    widgets["all_labels"].append(title)

    widgets["theme_button"] = ModernButton(
        header_frame,
        text="🌙",
        font=("Arial", 14),
        command=lambda: toggle_theme(widgets),
        relief=tk.FLAT,
        bg=LIGHT_THEME["text_secondary"],
        fg=LIGHT_THEME["fg"],
        padx=10,
        pady=5,
    )
    widgets["theme_button"].pack(side=tk.RIGHT)

    divider1 = tk.Frame(root, bg=LIGHT_THEME["border_color"], height=1)
    divider1.pack(fill=tk.X, padx=20)

    input_section = tk.Frame(root, bg=LIGHT_THEME["bg"])
    input_section.pack(pady=20, padx=20, fill=tk.X)

    url_label = tk.Label(
        input_section,
        text="📍 URL to Request",
        font=HEADER_FONT,
        bg=LIGHT_THEME["bg"],
        fg=LIGHT_THEME["fg"],
    )
    url_label.pack(anchor="w", pady=(0, 8))
    widgets["all_labels"].append(url_label)

    widgets["url_entry"] = ModernEntry(input_section, font=BODY_FONT, width=50)
    widgets["url_entry"].pack(fill=tk.X, pady=(0, 15), ipady=8)
    widgets["url_entry"].config(
        bg=LIGHT_THEME["input_bg"],
        fg=LIGHT_THEME["fg"],
        insertbackground=LIGHT_THEME["fg"],
        relief=tk.FLAT,
        borderwidth=1,
    )
    widgets["all_entries"].append(widgets["url_entry"])

    interval_label = tk.Label(
        input_section,
        text="⏱️  Interval (seconds)",
        font=HEADER_FONT,
        bg=LIGHT_THEME["bg"],
        fg=LIGHT_THEME["fg"],
    )
    interval_label.pack(anchor="w", pady=(0, 8))
    widgets["all_labels"].append(interval_label)

    widgets["interval_entry"] = ModernEntry(input_section, font=BODY_FONT, width=50)
    widgets["interval_entry"].pack(fill=tk.X, pady=(0, 15), ipady=8)
    widgets["interval_entry"].config(
        bg=LIGHT_THEME["input_bg"],
        fg=LIGHT_THEME["fg"],
        insertbackground=LIGHT_THEME["fg"],
        relief=tk.FLAT,
        borderwidth=1,
    )
    widgets["all_entries"].append(widgets["interval_entry"])

    stop_time_label = tk.Label(
        input_section,
        text="🛑 Stop Time (HH:MM)",
        font=HEADER_FONT,
        bg=LIGHT_THEME["bg"],
        fg=LIGHT_THEME["fg"],
    )
    stop_time_label.pack(anchor="w", pady=(0, 8))
    widgets["all_labels"].append(stop_time_label)

    widgets["stop_time_entry"] = ModernEntry(input_section, font=BODY_FONT, width=50)
    widgets["stop_time_entry"].pack(fill=tk.X, pady=(0, 15), ipady=8)
    widgets["stop_time_entry"].config(
        bg=LIGHT_THEME["input_bg"],
        fg=LIGHT_THEME["fg"],
        insertbackground=LIGHT_THEME["fg"],
        relief=tk.FLAT,
        borderwidth=1,
    )
    widgets["all_entries"].append(widgets["stop_time_entry"])

    widgets["button_frame"] = tk.Frame(root, bg=LIGHT_THEME["bg"])
    widgets["button_frame"].pack(pady=15)

    widgets["start_button"] = ModernButton(
        widgets["button_frame"],
        text="▶️  START",
        command=lambda: start_curling(
            widgets["url_entry"],
            widgets["interval_entry"],
            widgets["stop_time_entry"],
            widgets["start_button"],
            widgets["stop_button"],
            widgets["status_label"],
            widgets["log_text"],
            root,
            widgets["theme"],
        ),
        font=HEADER_FONT,
        fg="white",
        padx=20,
        pady=10,
        bg=LIGHT_THEME["success"],
        relief=tk.RAISED,
        cursor="hand2",
    )
    widgets["start_button"].pack(side=tk.LEFT, padx=8)

    widgets["stop_button"] = ModernButton(
        widgets["button_frame"],
        text="⏸  STOP",
        command=lambda: stop_curling(
            widgets["start_button"],
            widgets["stop_button"],
            widgets["status_label"],
            widgets["theme"],
        ),
        font=HEADER_FONT,
        fg="white",
        padx=20,
        pady=10,
        bg=LIGHT_THEME["danger"],
        relief=tk.RAISED,
        cursor="hand2",
        state=tk.DISABLED,
    )
    widgets["stop_button"].pack(side=tk.LEFT, padx=8)

    widgets["clear_button"] = ModernButton(
        widgets["button_frame"],
        text="🗑️  CLEAR",
        command=lambda: clear_log(widgets["log_text"]),
        font=HEADER_FONT,
        fg="white",
        padx=20,
        pady=10,
        bg=LIGHT_THEME["accent"],
        relief=tk.RAISED,
        cursor="hand2",
    )
    widgets["clear_button"].pack(side=tk.LEFT, padx=8)

    widgets["status_label"] = tk.Label(
        root,
        text="Ready to start",
        font=BODY_FONT,
        bg=LIGHT_THEME["bg"],
        fg=LIGHT_THEME["text_secondary"],
    )
    widgets["status_label"].pack(pady=(0, 10))
    widgets["all_labels"].append(widgets["status_label"])

    divider2 = tk.Frame(root, bg=LIGHT_THEME["border_color"], height=1)
    divider2.pack(fill=tk.X, padx=20)

    log_label = tk.Label(
        root,
        text="📋 Request Log",
        font=HEADER_FONT,
        bg=LIGHT_THEME["bg"],
        fg=LIGHT_THEME["fg"],
    )
    log_label.pack(anchor="w", pady=(15, 8), padx=20)
    widgets["all_labels"].append(log_label)

    log_frame = tk.Frame(root, bg=LIGHT_THEME["bg"])
    log_frame.pack(padx=20, pady=(0, 20), fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(log_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    widgets["log_text"] = tk.Text(log_frame, font=SMALL_FONT, height=12, wrap=tk.WORD)
    widgets["log_text"].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    widgets["log_text"].config(
        yscrollcommand=scrollbar.set,
        relief=tk.FLAT,
        borderwidth=0,
    )
    widgets["log_text"].tag_config("green", foreground="#48BB78")
    widgets["log_text"].tag_config("orange", foreground="#ED8936")
    widgets["log_text"].tag_config("red", foreground="#F56565")
    widgets["log_text"].tag_config("error", foreground="#F56565")

    scrollbar.config(command=widgets["log_text"].yview)

    apply_theme(widgets)

    return root


def run_app():
    root = build_main_window()
    root.mainloop()
