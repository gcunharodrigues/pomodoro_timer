#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk
import json
import time
from datetime import datetime, timedelta
from tkinter import messagebox
import os  # Added for macOS sound support


class PomodoroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Timer")
        self.root.resizable(False, False)

        # Load configuration
        self.config = self.load_config()

        # Timer state
        self.running = False
        self.current_session = 1
        self.time_left = 0
        self.timer_id = None

        self.create_gui()

    def load_config(self):
        default_config = {
            "work_duration": 25,
            "short_break": 5,
            "long_break": 15,
            "sessions_before_long_break": 4,
            "notification_sound": True,
            "auto_start": False
        }

        try:
            with open("pomodoro_config.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            with open("pomodoro_config.json", "w") as f:
                json.dump(default_config, f, indent=4)
            return default_config

    def save_config(self):
        with open("pomodoro_config.json", "w") as f:
            json.dump(self.config, f, indent=4)

    def create_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Title label
        title_label = ttk.Label(
            main_frame,
            text="Pomodoro",
            font=("Arial", 24, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Timer display (update row number)
        self.timer_label = ttk.Label(
            main_frame,
            text="25:00",
            font=("Arial", 48)
        )
        self.timer_label.grid(row=1, column=0, columnspan=2, pady=20)

        # Session info (update row number)
        self.session_label = ttk.Label(
            main_frame,
            text=f"Work Session {self.current_session}",
            font=("Arial", 12)
        )
        self.session_label.grid(row=2, column=0, columnspan=2, pady=5)

        # Control buttons (update row numbers)
        self.start_button = ttk.Button(
            main_frame,
            text="Start",
            command=self.start_timer
        )
        self.start_button.grid(row=3, column=0, pady=10, padx=5)

        self.reset_button = ttk.Button(
            main_frame,
            text="Reset",
            command=self.reset_timer
        )
        self.reset_button.grid(row=3, column=1, pady=10, padx=5)

        # Settings button (update row number)
        self.settings_button = ttk.Button(
            main_frame,
            text="Settings",
            command=self.show_settings
        )
        self.settings_button.grid(row=4, column=0, columnspan=2, pady=10)

        # Auto-start checkbox (update row number)
        self.auto_start_var = tk.BooleanVar(value=self.config["auto_start"])
        self.auto_start_checkbox = ttk.Checkbutton(
            main_frame,
            text="Auto-start sessions",
            variable=self.auto_start_var,
            command=self.update_auto_start
        )
        self.auto_start_checkbox.grid(row=5, column=0, columnspan=2, pady=5)

        # Initialize timer display
        self.time_left = self.config["work_duration"] * 60
        self.update_timer_display()

    def update_timer_display(self):
        minutes = self.time_left // 60
        seconds = self.time_left % 60
        self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")

    def start_timer(self):
        if not self.running:
            self.running = True
            self.start_button.config(text="Pause")
            self.timer_tick()
        else:
            self.running = False
            self.start_button.config(text="Resume")
            if self.timer_id:
                self.root.after_cancel(self.timer_id)

    def timer_tick(self):
        if self.running and self.time_left > 0:
            self.time_left -= 1
            self.update_timer_display()
            self.timer_id = self.root.after(1000, self.timer_tick)
        elif self.running:
            self.timer_completed()

    def timer_completed(self):
        def sound_play(x):
            for i in range(4):
                x.play()
        if self.config["notification_sound"]:
            if os.name == 'nt':  # Windows
                for i in range(3):
                    import winsound
                    winsound.Beep(1000, 500)
                    time.sleep(0.3)
            else:  # macOS/Linux
                for i in range(3):
                    os.system('afplay /System/Library/Sounds/Glass.aiff')

        is_break = self.session_label.cget("text").endswith("Break")

        if is_break:
            self.current_session += 1
            self.time_left = self.config["work_duration"] * 60
            self.session_label.config(
                text=f"Work Session {self.current_session}")
        else:
            # After completing a work session
            if (self.current_session) % self.config["sessions_before_long_break"] == 0:
                self.time_left = self.config["long_break"] * 60
                self.session_label.config(text="Long Break")
            else:
                self.time_left = self.config["short_break"] * 60
                self.session_label.config(text="Short Break")

        self.running = False
        self.start_button.config(text="Start")
        self.update_timer_display()

        # Auto-start next session if enabled
        if self.config["auto_start"]:
            # Start after 1 second delay
            self.root.after(1000, self.start_timer)

    def reset_timer(self):
        self.running = False
        self.current_session = 1
        self.time_left = self.config["work_duration"] * 60
        self.session_label.config(text=f"Work Session {self.current_session}")
        self.start_button.config(text="Start")
        self.update_timer_display()
        if self.timer_id:
            self.root.after_cancel(self.timer_id)

    def show_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.resizable(False, False)

        frame = ttk.Frame(settings_window, padding="20")
        frame.grid(row=0, column=0)

        # Create entry fields for each setting
        entries = {}
        row = 0
        for key, value in self.config.items():
            ttk.Label(frame, text=key.replace("_", " ").title()
                      ).grid(row=row, column=0, pady=5, padx=5)
            entry = ttk.Entry(frame)
            entry.insert(0, str(value))
            entry.grid(row=row, column=1, pady=5, padx=5)
            entries[key] = entry
            row += 1

        def save_settings():
            try:
                for key, entry in entries.items():
                    value = entry.get()
                    if key == "notification_sound" or key == "auto_start":
                        # Handle boolean values
                        self.config[key] = value.lower() == "true"
                    else:
                        # Handle integer values
                        self.config[key] = int(value)
                self.save_config()
                self.reset_timer()
                settings_window.destroy()
                messagebox.showinfo("Success", "Settings saved!")
            except ValueError:
                messagebox.showerror(
                    "Error", "Please enter valid values (numbers for durations, true/false for checkboxes)")

        ttk.Button(frame, text="Save", command=save_settings).grid(
            row=row, column=0, columnspan=2, pady=20)

    def update_auto_start(self):
        self.config["auto_start"] = self.auto_start_var.get()
        self.save_config()


if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroApp(root)
    root.mainloop()
