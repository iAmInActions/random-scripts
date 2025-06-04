import tkinter as tk
from tkinter import messagebox
from threading import Thread
import time
import subprocess
import sys
import os
import pystray
from PIL import Image, ImageDraw, ImageFont


class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pizza Timer")
        self.root.geometry("240x350")
        self.root.configure(bg="#2e2e2e")  # Dark gray background
        self.running = False
        self.remaining_seconds = 0
        self.original_minutes = 0

        # Timer display label
        self.timer_label = tk.Label(root, text="00:00", font=("Helvetica", 32), bg="#2e2e2e", fg="#ff00ff")
        self.timer_label.pack(pady=2)
        
        # Separator
        tk.Frame(root, bg="#cccccc", height=2).pack(fill=tk.X, pady=5)

        # Input for minutes
        self.minutes_var = tk.IntVar(value=1)
        tk.Label(root, text="Minutes:", bg="#2e2e2e", fg="#ffffff").pack()
        self.minutes_entry = tk.Entry(root, textvariable=self.minutes_var, bg="#3a3a3a", fg="#ffffff", insertbackground="white")
        self.minutes_entry.pack()

        # Alert message
        tk.Label(root, text="Message:", bg="#2e2e2e", fg="#ffffff").pack()
        self.message_text = tk.Text(root, height=5, width=25, bg="#3a3a3a", fg="#ffffff", insertbackground="white")
        self.message_text.pack(pady=5)

        # Notification method
        self.method_var = tk.StringVar(value="beep")
        tk.Label(root, text="Notification backend:", bg="#2e2e2e", fg="#ffffff").pack()
        self.method_var.set("beep")  # Set default

        OPTIONS = ["beep", "aplay", "mplayer"]
        self.method_dropdown = tk.OptionMenu(root, self.method_var, *OPTIONS)
        self.method_dropdown.config(bg="#2e2e2e", fg="#acacac", activebackground="#444444", activeforeground="#ffffff", highlightthickness=0)
        self.method_dropdown["menu"].config(bg="#2e2e2e", fg="#acacac", activebackground="#444444", activeforeground="#ffffff")
        self.method_dropdown.pack()

        # Buttons
        button_frame = tk.Frame(root, bg="#2e2e2e")
        button_frame.pack(pady=10)
        start_button = tk.Button(
            button_frame,
            text="Start",
            command=self.start_timer,
            bg="#444444",
            fg="#ffffff",
            activebackground="#666666",
            activeforeground="#ffffff",
            relief=tk.FLAT
        )
        start_button.pack(side=tk.LEFT, padx=5)

        reset_button = tk.Button(
            button_frame,
            text="Reset",
            command=self.reset_timer,
            bg="#444444",
            fg="#ffffff",
            activebackground="#666666",
            activeforeground="#ffffff",
            relief=tk.FLAT
        )
        reset_button.pack(side=tk.LEFT, padx=5)

        # Hide on close
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)

        # Tray icon setup
        self.icon = self.create_tray_icon()

    def create_tray_icon(self):
        icon_image = self.create_icon_image()
        return pystray.Icon("timer", icon_image, "Pizza Timer", menu=pystray.Menu(
            pystray.MenuItem("Show", self.show_window),
            pystray.MenuItem("Quit", self.quit_app)
        ))

    def create_icon_image(self):
        # Draw a simple clock face
        image = Image.new('RGB', (64, 64), "#2e2e2e")
        draw = ImageDraw.Draw(image)
        draw.ellipse((8, 8, 56, 56), outline="white", width=4)

        # Coordinates for triangle (pizza slice)
        center = (32, 32)
        point1 = (48, 0)  # Top center
        point2 = (64, 16)  # Right center

        # Draw filled triangle
        draw.polygon([center, point1, point2], fill="orange", outline="yellow")
        draw.ellipse((48, 15, 52, 22), fill="red")  # mini pepperoni
        return image

    def update_tray_icon_image(self, minutes, seconds):
        img = Image.new("RGB", (64, 64), "#2e2e2e")
        draw = ImageDraw.Draw(img)
        draw.line((0, 32, 64, 32), fill="green", width=4) # Separator

        time_m = f"{minutes:02}"
        time_s = f"{seconds:02}"

        try:
            font = ImageFont.truetype("DejaVuSansMono.ttf", 28)
        except:
            font = ImageFont.load_default()

        # Center each number in its 64x32 half
        def draw_centered_text(text, top_offset):
            bbox = font.getbbox(text)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            x = (64 - w) // 2
            y = top_offset - 6 + (32 - h) // 2
            draw.text((x, y), text, fill="white", font=font)

        draw_centered_text(time_m, 0)   # Top half for MM
        draw_centered_text(time_s, 32)  # Bottom half for SS

        if self.icon.visible:
            self.icon.icon = img

    def update_timer_display(self):
        mins, secs = divmod(self.remaining_seconds, 60)
        time_str = f"{mins:02}:{secs:02}"
        self.timer_label.config(text=time_str)
        if self.icon.visible:
            self.icon.title = f"Pizza Timer - {time_str}"
            self.update_tray_icon_image(mins, secs)

    def hide_window(self):
        self.root.withdraw()
        Thread(target=self.icon.run, daemon=True).start()

    def show_window(self, icon=None, item=None):
        self.icon.stop()
        self.root.after(0, self.root.deiconify)

    def quit_app(self, icon=None, item=None):
        self.icon.stop()
        self.root.quit()

    def start_timer(self):
        if self.running:
            return

        try:
            minutes = int(self.minutes_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid number of minutes.")
            return

        if minutes <= 0:
            messagebox.showerror("Error", "Minutes must be greater than 0.")
            return

        self.original_minutes = minutes
        self.remaining_seconds = minutes * 60
        self.running = True
        Thread(target=self.countdown, daemon=True).start()

    def reset_timer(self):
        self.running = False
        self.remaining_seconds = self.original_minutes * 60
        self.update_timer_display()

    def countdown(self):
        while self.remaining_seconds > 0 and self.running:
            self.root.after(0, self.update_timer_display)
            time.sleep(1)
            self.remaining_seconds -= 1

        if self.running and self.remaining_seconds <= 0:
            self.running = False
            self.root.after(0, self.update_timer_display)
            self.root.after(0, self.trigger_alarm)

    def trigger_alarm(self):
        message = self.message_text.get("1.0", tk.END).strip()
        messagebox.showinfo("TIMER ALERT", message or "Go grab your Pizza!")

        method = self.method_var.get()
        if method == "beep":
            subprocess.Popen(["beep", "-f", "2000", "-l", "2000"])
        elif method == "aplay":
            subprocess.Popen(["aplay", "DING.WAV"])
        elif method == "mplayer":
            subprocess.Popen(["mplayer", "DING.WAV"])


def main():
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
