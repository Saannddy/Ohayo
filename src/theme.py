import tkinter as tk

LIGHT_THEME = {
    "bg": "#F5F7FA",
    "fg": "#1A202C",
    "accent": "#3182CE",
    "accent_hover": "#2C5AA0",
    "success": "#38A169",
    "success_hover": "#2D5A47",
    "danger": "#E53E3E",
    "danger_hover": "#C53030",
    "input_bg": "#FFFFFF",
    "input_border": "#CBD5E0",
    "card_bg": "#FFFFFF",
    "text_secondary": "#718096",
    "border_color": "#E2E8F0",
}

DARK_THEME = {
    "bg": "#1A202C",
    "fg": "#F7FAFC",
    "accent": "#4299E1",
    "accent_hover": "#3182CE",
    "success": "#48BB78",
    "success_hover": "#38A169",
    "danger": "#F56565",
    "danger_hover": "#E53E3E",
    "input_bg": "#2D3748",
    "input_border": "#4A5568",
    "card_bg": "#2D3748",
    "text_secondary": "#A0AEC0",
    "border_color": "#4A5568",
}

class ModernEntry(tk.Entry):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.default_color = LIGHT_THEME["input_border"]
        self.focus_color = LIGHT_THEME["accent"]
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)

    def _on_focus_in(self, event):
        pass

    def _on_focus_out(self, event):
        pass

class ModernButton(tk.Button):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, event):
        if self["state"] != tk.DISABLED:
            self.config(relief=tk.SUNKEN)

    def _on_leave(self, event):
        self.config(relief=tk.RAISED if self["relief"] == tk.SUNKEN else tk.RAISED)
