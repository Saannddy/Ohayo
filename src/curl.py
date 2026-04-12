import threading
import requests
import time
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

is_running = False


def show_error(message):
    messagebox.showerror("エラー", message)


def update_status(status_label, text, status_type, theme):
    status_label.config(text=text)
    if status_type == "running":
        status_label.config(fg=theme["success"])
    elif status_type == "completed":
        status_label.config(fg=theme["accent"])
    elif status_type == "error":
        status_label.config(fg=theme["danger"])
    elif status_type == "stopped":
        status_label.config(fg=theme["danger"])


def start_curling(url_entry, interval_entry, stop_time_entry, start_button, stop_button, status_label, log_text, root, theme):
    url = url_entry.get().strip()
    interval_str = interval_entry.get().strip()
    stop_time_str = stop_time_entry.get().strip()

    if not url:
        show_error("Please enter a URL")
        return
    if not interval_str:
        show_error("Please enter an interval (in seconds)")
        return
    if not stop_time_str:
        show_error("Please enter a stop time (HH:MM format)")
        return

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

    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    update_status(status_label, "Running...", "running", theme)

    thread = threading.Thread(
        target=curl_loop,
        args=(url, interval, stop_time, status_label, log_text, root, start_button, stop_button, theme),
    )
    thread.daemon = True
    thread.start()


def curl_loop(url, interval, stop_time, status_label, log_text, root, start_button, stop_button, theme):
    global is_running
    is_running = True
    request_count = 0

    try:
        while is_running:
            current_time = datetime.now().time()
            if current_time >= stop_time:
                update_status(status_label, f"Completed at {stop_time.strftime('%H:%M')}", "completed", theme)
                break

            try:
                response = requests.get(url, timeout=5)
                request_count += 1
                timestamp = datetime.now().strftime("%H:%M:%S")
                status_code = response.status_code
                log_message = f"[{timestamp}] Request #{request_count}: {status_code}"
                log_text.insert(tk.END, log_message + "\n", "green" if 200 <= status_code < 300 else "orange" if 300 <= status_code < 400 else "red")
                log_text.see(tk.END)
                root.update()
            except requests.exceptions.RequestException as e:
                timestamp = datetime.now().strftime("%H:%M:%S")
                log_text.insert(tk.END, f"[{timestamp}] Error: {str(e)}\n", "error")
                log_text.see(tk.END)
                root.update()

            time.sleep(interval)
    except Exception as e:
        update_status(status_label, f"Error: {str(e)}", "error", theme)
    finally:
        is_running = False
        start_button.config(state=tk.NORMAL)
        stop_button.config(state=tk.DISABLED)


def stop_curling(start_button, stop_button, status_label, theme):
    global is_running
    is_running = False
    update_status(status_label, "Stopped", "stopped", theme)
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)


def clear_log(log_text):
    log_text.delete(1.0, tk.END)
