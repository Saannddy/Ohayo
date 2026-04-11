import tkinter as tk
from tkinter import messagebox
import requests
import threading
from datetime import datetime
import time
import sys

# Beautiful color themes
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
        self.default_color = theme["input_border"]
        self.focus_color = theme["accent"]
        
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

def start_curling():
    """Start making curl requests at specified intervals until stop time"""
    try:
        url = url_entry.get().strip()
        interval_str = interval_entry.get().strip()
        stop_time_str = stop_time_entry.get().strip()
        
        # Validation
        if not url:
            show_error("Please enter a URL")
            return
        if not interval_str:
            show_error("Please enter an interval (in seconds)")
            return
        if not stop_time_str:
            show_error("Please enter a stop time (HH:MM format)")
            return
        
        # Parse inputs
        try:
            interval = int(interval_str)
            if interval <= 0:
                show_error("Interval must be greater than 0")
                return
        except ValueError:
            show_error("Interval must be a valid number")
            return
        
        try:
            stop_time = datetime.strptime(stop_time_str, "%H:%M").time()
        except ValueError:
            show_error("Stop time must be in HH:MM format (24-hour)")
            return
        
        # Disable button during execution
        start_button.config(state=tk.DISABLED)
        stop_button.config(state=tk.NORMAL)
        update_status("Running...", "running")
        
        # Run in background thread
        thread = threading.Thread(target=curl_loop, args=(url, interval, stop_time))
        thread.daemon = True
        thread.start()
        
    except Exception as e:
        show_error(f"An error occurred: {str(e)}")

def curl_loop(url, interval, stop_time):
    """Loop to make requests at specified interval until stop time"""
    global is_running
    is_running = True
    request_count = 0
    
    try:
        while is_running:
            current_time = datetime.now().time()
            
            # Check if we've reached the stop time
            if current_time >= stop_time:
                update_status(f"Completed at {stop_time.strftime('%H:%M')}", "completed")
                break
            
            try:
                response = requests.get(url, timeout=5)
                request_count += 1
                timestamp = datetime.now().strftime("%H:%M:%S")
                status_code = response.status_code
                
                # Color code based on status
                if 200 <= status_code < 300:
                    color = "green"
                elif 300 <= status_code < 400:
                    color = "orange"
                else:
                    color = "red"
                
                log_message = f"[{timestamp}] Request #{request_count}: {status_code}"
                log_text.insert(tk.END, log_message + "\n", color)
                log_text.see(tk.END)
                root.update()
            except requests.exceptions.RequestException as e:
                timestamp = datetime.now().strftime("%H:%M:%S")
                log_text.insert(tk.END, f"[{timestamp}] Error: {str(e)}\n", "error")
                log_text.see(tk.END)
                root.update()
            
            # Wait for interval or until stop is clicked
            time.sleep(interval)
    
    except Exception as e:
        update_status(f"Error: {str(e)}", "error")
    finally:
        is_running = False
        start_button.config(state=tk.NORMAL)
        stop_button.config(state=tk.DISABLED)

def stop_curling():
    """Stop the curling process"""
    global is_running
    is_running = False
    update_status("Stopped", "stopped")
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)

def clear_log():
    """Clear the log"""
    log_text.delete(1.0, tk.END)

def show_error(message):
    """Show error dialog"""
    messagebox.showerror("エラー", message)

def update_status(text, status_type):
    """Update status with proper styling"""
    status_label.config(text=text)
    if status_type == "running":
        status_label.config(fg=theme["success"])
    elif status_type == "completed":
        status_label.config(fg=theme["accent"])
    elif status_type == "error":
        status_label.config(fg=theme["danger"])
    elif status_type == "stopped":
        status_label.config(fg=theme["danger"])

def toggle_theme():
    """Toggle between dark and light theme"""
    global theme, is_dark_mode
    is_dark_mode = not is_dark_mode
    theme = DARK_THEME if is_dark_mode else LIGHT_THEME
    apply_theme()

def apply_theme():
    """Apply theme to all widgets"""
    root.config(bg=theme["bg"])
    
    # Update all labels
    for label in all_labels:
        label.config(bg=theme["bg"], fg=theme["fg"])
    
    # Update entries
    for entry in all_entries:
        entry.config(bg=theme["input_bg"], fg=theme["fg"], 
                    insertbackground=theme["fg"], borderwidth=1,
                    relief=tk.FLAT)
    
    # Update buttons
    start_button.config(bg=theme["success"], activebackground=theme["success_hover"])
    stop_button.config(bg=theme["danger"], activebackground=theme["danger_hover"])
    clear_button.config(bg=theme["accent"], activebackground=theme["accent_hover"])
    theme_button.config(bg=theme["text_secondary"], activebackground=theme["input_bg"],
                       fg=theme["fg"] if is_dark_mode else theme["bg"])
    
    # Update text widget
    log_text.config(bg=theme["input_bg"], fg=theme["fg"], 
                   insertbackground=theme["fg"],
                   relief=tk.FLAT, borderwidth=0)
    
    # Configure tags for log text
    log_text.tag_config("green", foreground="#48BB78")
    log_text.tag_config("orange", foreground="#ED8936")
    log_text.tag_config("red", foreground="#F56565")
    log_text.tag_config("error", foreground="#F56565")
    
    # Update button frame background
    button_frame.config(bg=theme["bg"])

# Global flags
is_running = False
is_dark_mode = False
theme = LIGHT_THEME

# 1. Initialize the main window
root = tk.Tk()
root.title("おはよう - URL Curl Scheduler")
root.geometry("700x700")
root.resizable(True, True)

# Set minimum window size
root.minsize(600, 500)

# Configure style
root.config(bg=theme["bg"])

# Font definitions
TITLE_FONT = ("Segoe UI" if sys.platform == "win32" else "SF Pro Display", 24, "bold")
HEADER_FONT = ("Segoe UI" if sys.platform == "win32" else "SF Pro Display", 11, "bold")
BODY_FONT = ("Segoe UI" if sys.platform == "win32" else "SF Pro Display", 10)
SMALL_FONT = ("Segoe UI" if sys.platform == "win32" else "SF Pro Display", 9)

# Track all widgets
all_labels = []
all_entries = []

# ===== HEADER =====
header_frame = tk.Frame(root, bg=theme["bg"])
header_frame.pack(pady=(20, 10), padx=20, fill=tk.X)

title = tk.Label(header_frame, text="おはよう", font=TITLE_FONT, 
                bg=theme["bg"], fg=theme["fg"])
title.pack(side=tk.LEFT)

theme_button = ModernButton(header_frame, text="🌙", font=("Arial", 14), 
                           command=toggle_theme, relief=tk.FLAT, 
                           bg=theme["text_secondary"], fg=theme["fg"],
                           padx=10, pady=5)
theme_button.pack(side=tk.RIGHT)

# ===== DIVIDER =====
divider1 = tk.Frame(root, bg=theme["border_color"], height=1)
divider1.pack(fill=tk.X, padx=20)

# ===== INPUT SECTION =====
input_section = tk.Frame(root, bg=theme["bg"])
input_section.pack(pady=20, padx=20, fill=tk.X)

# URL Input
url_label = tk.Label(input_section, text="📍 URL to Request", font=HEADER_FONT, 
                    bg=theme["bg"], fg=theme["fg"])
url_label.pack(anchor="w", pady=(0, 8))
all_labels.append(url_label)

url_entry = ModernEntry(input_section, font=BODY_FONT, width=50)
url_entry.pack(fill=tk.X, pady=(0, 15), ipady=8)
url_entry.config(bg=theme["input_bg"], fg=theme["fg"], 
                insertbackground=theme["fg"], relief=tk.FLAT, borderwidth=1)
all_entries.append(url_entry)

# Interval Input
interval_label = tk.Label(input_section, text="⏱️  Interval (seconds)", font=HEADER_FONT,
                         bg=theme["bg"], fg=theme["fg"])
interval_label.pack(anchor="w", pady=(0, 8))
all_labels.append(interval_label)

interval_entry = ModernEntry(input_section, font=BODY_FONT, width=50)
interval_entry.pack(fill=tk.X, pady=(0, 15), ipady=8)
interval_entry.config(bg=theme["input_bg"], fg=theme["fg"],
                     insertbackground=theme["fg"], relief=tk.FLAT, borderwidth=1)
all_entries.append(interval_entry)

# Stop Time Input
stop_time_label = tk.Label(input_section, text="🛑 Stop Time (HH:MM)", font=HEADER_FONT,
                          bg=theme["bg"], fg=theme["fg"])
stop_time_label.pack(anchor="w", pady=(0, 8))
all_labels.append(stop_time_label)

stop_time_entry = ModernEntry(input_section, font=BODY_FONT, width=50)
stop_time_entry.pack(fill=tk.X, pady=(0, 15), ipady=8)
stop_time_entry.config(bg=theme["input_bg"], fg=theme["fg"],
                      insertbackground=theme["fg"], relief=tk.FLAT, borderwidth=1)
all_entries.append(stop_time_entry)

# ===== BUTTON SECTION =====
button_frame = tk.Frame(root, bg=theme["bg"])
button_frame.pack(pady=15)

start_button = ModernButton(button_frame, text="▶️  START", command=start_curling, 
                           font=HEADER_FONT, fg="white", padx=20, pady=10,
                           bg=theme["success"], relief=tk.RAISED, cursor="hand2")
start_button.pack(side=tk.LEFT, padx=8)

stop_button = ModernButton(button_frame, text="⏸  STOP", command=stop_curling,
                          font=HEADER_FONT, fg="white", padx=20, pady=10,
                          bg=theme["danger"], relief=tk.RAISED, cursor="hand2",
                          state=tk.DISABLED)
stop_button.pack(side=tk.LEFT, padx=8)

clear_button = ModernButton(button_frame, text="🗑️  CLEAR", command=clear_log,
                           font=HEADER_FONT, fg="white", padx=20, pady=10,
                           bg=theme["accent"], relief=tk.RAISED, cursor="hand2")
clear_button.pack(side=tk.LEFT, padx=8)

# ===== STATUS =====
status_label = tk.Label(root, text="Ready to start", font=BODY_FONT,
                       bg=theme["bg"], fg=theme["text_secondary"])
status_label.pack(pady=(0, 10))
all_labels.append(status_label)

# ===== DIVIDER =====
divider2 = tk.Frame(root, bg=theme["border_color"], height=1)
divider2.pack(fill=tk.X, padx=20)

# ===== LOG SECTION =====
log_label = tk.Label(root, text="📋 Request Log", font=HEADER_FONT,
                    bg=theme["bg"], fg=theme["fg"])
log_label.pack(anchor="w", pady=(15, 8), padx=20)
all_labels.append(log_label)

# Log text with scrollbar
log_frame = tk.Frame(root, bg=theme["bg"])
log_frame.pack(padx=20, pady=(0, 20), fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(log_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

log_text = tk.Text(log_frame, font=SMALL_FONT, height=12, wrap=tk.WORD)
log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
log_text.config(yscrollcommand=scrollbar.set, relief=tk.FLAT, borderwidth=0)
log_text.tag_config("green", foreground="#48BB78")
log_text.tag_config("orange", foreground="#ED8936")
log_text.tag_config("red", foreground="#F56565")
log_text.tag_config("error", foreground="#F56565")

scrollbar.config(command=log_text.yview)

# Apply initial theme
apply_theme()

# 8. Start the application loop
root.mainloop()