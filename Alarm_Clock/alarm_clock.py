import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import time
import threading
import pygame
import os
import math

# Initialize pygame mixer
pygame.mixer.init()

class AlarmClock:
    def __init__(self, root):
        self.root = root
        self.root.title("⏰ Stylish Python Alarm Clock")
        self.root.geometry("480x620")
        self.root.configure(bg="#f4f7fc")

        self.alarm_time = None
        self.alarm_thread = None
        self.alarm_active = False
        self.snooze_minutes = 5
        self.alarm_tone = None

        # Title Label
        tk.Label(root, text="Alarm Clock", font=("Poppins", 22, "bold"), fg="#333", bg="#f4f7fc").pack(pady=15)

        # Clock Display with Circular Frame & numbers 3,6,9,12 + ticks
        self.clock_canvas = tk.Canvas(root, width=300, height=300, bg="#f4f7fc", highlightthickness=0)
        self.clock_canvas.pack()
        self.clock_radius = 125
        self.center_x = 150
        self.center_y = 150

        self.clock_canvas.create_oval(
            self.center_x - self.clock_radius,
            self.center_y - self.clock_radius,
            self.center_x + self.clock_radius,
            self.center_y + self.clock_radius,
            outline="#6c63ff", width=5, fill="#dcdcff"
        )

        # Draw hour numbers and ticks
        self.draw_clock_face()

        # Hands of the clock: create lines, to be updated every second
        self.hour_hand = self.clock_canvas.create_line(self.center_x, self.center_y, self.center_x, self.center_y - 50,
                                                      width=6, fill="#333", capstyle=tk.ROUND)
        self.minute_hand = self.clock_canvas.create_line(self.center_x, self.center_y, self.center_x, self.center_y - 70,
                                                        width=4, fill="#555", capstyle=tk.ROUND)
        self.second_hand = self.clock_canvas.create_line(self.center_x, self.center_y, self.center_x, self.center_y - 90,
                                                        width=2, fill="#f00", capstyle=tk.ROUND)

        self.update_clock_time()

        # Alarm Time Inputs
        time_frame = tk.Frame(root, bg="#f4f7fc")
        time_frame.pack(pady=15)

        self.hour_var = tk.StringVar(value="00")
        self.min_var = tk.StringVar(value="00")

        tk.Label(time_frame, text="Hour", font=("Helvetica", 12), bg="#f4f7fc").grid(row=0, column=0, padx=8)
        tk.Entry(time_frame, textvariable=self.hour_var, width=5, font=("Helvetica", 12)).grid(row=0, column=1, padx=5)

        tk.Label(time_frame, text="Minute", font=("Helvetica", 12), bg="#f4f7fc").grid(row=0, column=2, padx=8)
        tk.Entry(time_frame, textvariable=self.min_var, width=5, font=("Helvetica", 12)).grid(row=0, column=3, padx=5)

        # Alarm Tone Dropdown
        tk.Label(root, text="🎵 Select Alarm Tone", font=("Helvetica", 12, "bold"), bg="#f4f7fc").pack(pady=(10, 5))
        self.tones = ["tone1.mp3", "tone2.mp3", "tone3.mp3", "tone4.mp3", "tone5.mp3"]
        self.tone_var = tk.StringVar()
        self.tone_dropdown = ttk.Combobox(root, values=self.tones, textvariable=self.tone_var, state="readonly", font=("Helvetica", 11))
        self.tone_dropdown.set("tone1.mp3")
        self.tone_dropdown.pack()

        # Snooze Spinner
        tk.Label(root, text="😴 Snooze Duration (minutes)", font=("Helvetica", 12, "bold"), bg="#f4f7fc").pack(pady=(15, 5))
        self.snooze_spin = ttk.Spinbox(root, from_=1, to=30, width=5, font=("Helvetica", 11))
        self.snooze_spin.set(self.snooze_minutes)
        self.snooze_spin.pack()

        # Buttons
        btn_frame = tk.Frame(root, bg="#f4f7fc")
        btn_frame.pack(pady=20)

        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 11, "bold"), padding=6)
        style.map("TButton", foreground=[('active', '#fff')], background=[('active', '#6c63ff')])

        ttk.Button(btn_frame, text="✅ Set Alarm", command=self.set_alarm).grid(row=0, column=0, padx=15)
        ttk.Button(btn_frame, text="⛔ Stop Alarm", command=self.stop_alarm).grid(row=0, column=1, padx=15)

    def draw_clock_face(self):
        # Draw numbers 3, 6, 9, 12
        numbers = {3: (self.center_x + self.clock_radius - 30, self.center_y),
                   6: (self.center_x, self.center_y + self.clock_radius - 30),
                   9: (self.center_x - self.clock_radius + 30, self.center_y),
                   12: (self.center_x, self.center_y - self.clock_radius + 30)}

        for num, (x, y) in numbers.items():
            self.clock_canvas.create_text(x, y, text=str(num), font=("Helvetica", 20, "bold"), fill="#333")

        # Draw tick marks for other hours (1,2,4,5,7,8,10,11)
        for hour in range(1, 13):
            if hour in numbers:
                continue
            angle = math.pi / 6 * (hour - 3)  # shift to make 3 o'clock at 0 radians
            inner_radius = self.clock_radius - 15
            outer_radius = self.clock_radius - 5

            x_inner = self.center_x + inner_radius * math.cos(angle)
            y_inner = self.center_y + inner_radius * math.sin(angle)
            x_outer = self.center_x + outer_radius * math.cos(angle)
            y_outer = self.center_y + outer_radius * math.sin(angle)

            self.clock_canvas.create_line(x_inner, y_inner, x_outer, y_outer, fill="#555", width=2)

    def update_clock_time(self):
        now = datetime.now()

        # Calculate angles for hands
        sec_angle = math.radians(now.second * 6 - 90)  # 6 degrees per second, -90 to start at top
        min_angle = math.radians(now.minute * 6 - 90)
        hour_angle = math.radians((now.hour % 12) * 30 + now.minute * 0.5 - 90)  # 30 degrees per hour + half degree per minute

        # Calculate hand end points
        hour_length = self.clock_radius * 0.5
        minute_length = self.clock_radius * 0.7
        second_length = self.clock_radius * 0.9

        hour_x = self.center_x + hour_length * math.cos(hour_angle)
        hour_y = self.center_y + hour_length * math.sin(hour_angle)

        min_x = self.center_x + minute_length * math.cos(min_angle)
        min_y = self.center_y + minute_length * math.sin(min_angle)

        sec_x = self.center_x + second_length * math.cos(sec_angle)
        sec_y = self.center_y + second_length * math.sin(sec_angle)

        # Update hands
        self.clock_canvas.coords(self.hour_hand, self.center_x, self.center_y, hour_x, hour_y)
        self.clock_canvas.coords(self.minute_hand, self.center_x, self.center_y, min_x, min_y)
        self.clock_canvas.coords(self.second_hand, self.center_x, self.center_y, sec_x, sec_y)

        self.root.after(1000, self.update_clock_time)

    def set_alarm(self):
        try:
            hour = int(self.hour_var.get())
            minute = int(self.min_var.get())
            now = datetime.now()
            alarm_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

            if alarm_time < now:
                alarm_time += timedelta(days=1)

            self.alarm_time = alarm_time
            self.snooze_minutes = int(self.snooze_spin.get())

            selected_tone = self.tone_var.get()
            tone_path = os.path.join("alarm_tones", selected_tone)

            if not os.path.exists(tone_path):
                messagebox.showerror("Tone Missing", f"{selected_tone} not found in alarm_tones folder.")
                return

            self.alarm_tone = tone_path
            self.alarm_active = True

            self.alarm_thread = threading.Thread(target=self.check_alarm)
            self.alarm_thread.daemon = True
            self.alarm_thread.start()

            messagebox.showinfo("Alarm Set", f"Alarm set for {alarm_time.strftime('%H:%M')}")

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for hour and minute.")

    def check_alarm(self):
        while self.alarm_active:
            if datetime.now() >= self.alarm_time:
                self.play_alarm()
                self.show_snooze_popup()
                break
            time.sleep(1)

    def play_alarm(self):
        pygame.mixer.music.load(self.alarm_tone)
        pygame.mixer.music.play(-1)

    def stop_alarm(self):
        self.alarm_active = False
        pygame.mixer.music.stop()

    def snooze(self):
        pygame.mixer.music.stop()
        self.alarm_time = datetime.now() + timedelta(minutes=self.snooze_minutes)
        self.alarm_thread = threading.Thread(target=self.check_alarm)
        self.alarm_thread.daemon = True
        self.alarm_thread.start()

    def show_snooze_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("⏰ Alarm")
        popup.geometry("260x130")
        popup.config(bg="#fff3cd")

        tk.Label(popup, text="🔔 Wake Up!", font=("Helvetica", 16, "bold"), bg="#fff3cd").pack(pady=10)
        ttk.Button(popup, text="Snooze", command=lambda: [popup.destroy(), self.snooze()]).pack(side="left", padx=20, pady=10)
        ttk.Button(popup, text="Stop", command=lambda: [popup.destroy(), self.stop_alarm()]).pack(side="right", padx=20, pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = AlarmClock(root)
    root.mainloop()
