import tkinter as tk
import time
import threading
from datetime import timedelta
import json
import os
import datetime

def save_state(pet, filename="save.json"):
    with open(filename, "w") as f:
        json.dump(vars(pet), f)

def load_state(pet, filename="save.json"):
    if os.path.exists(filename):
        with open(filename) as f:
            data = json.load(f)
            pet.__dict__.update(data)

class Tamagotchi:
    def __init__(self):
        self.hunger = 3600
        self.happiness = 3600

    def feed(self):
        self.hunger = min(self.hunger + 3600, 3600)

    def play(self):
        self.happiness = min(self.happiness + 3600, 3600)

    def decay(self):
        self.hunger = max(self.hunger - 1, 0)
        self.happiness = max(self.happiness - 1, 0)

class App:
    def __init__(self, root):
        self.root = root
        root.geometry("500x500")
        self.pet = Tamagotchi()
        load_state(self.pet)

        # UI Elements
        self.clock_label = tk.Label(root, font=("Arial", 14), fg="white")
        self.clock_label.pack(pady=5)

        self.hunger_label = tk.Label(root, text="Hunger: 1:00:00", font=("Arial", 14))
        self.hunger_label.pack(pady=5)
        self.happiness_label = tk.Label(root, text="Happiness: 1:00:00", font=("Arial", 14))
        self.happiness_label.pack(pady=5)

        self.image_frame = tk.Frame(root, width=300, height=300)
        self.image_frame.pack(pady=10)
        self.pet_label = tk.Label(self.image_frame, width=300, height=300)
        self.pet_label.pack()

        self.button_frame = tk.Frame(root)
        self.button_frame.pack(side="bottom", pady=5)

        self.feed_btn = tk.Button(self.button_frame, text="Feed", command=self.feed, font=("Arial", 12))
        self.feed_btn.pack(side="left", padx=10)

        self.play_btn = tk.Button(self.button_frame, text="Play", command=self.play, font=("Arial", 12))
        self.play_btn.pack(side="left", padx=10)

        # Load GIFs for day and night
        self.day_gif_frames = self.load_gif("cat_is_chillin(11).gif")
        self.night_gif_frames = self.load_gif("sleep.gif")
        self.pet_frames = self.day_gif_frames
        self.current_frame = 0

        self.animate_gif()

        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()

        self.update_clock()

    def load_gif(self, filename):
        frames = []
        i = 0
        while True:
            try:
                frame = tk.PhotoImage(file=filename, format=f"gif -index {i}")
                frames.append(frame)
                i += 1
            except tk.TclError:
                break
        return frames

    def update_clock(self):
        now = datetime.datetime.now()
        time_str = now.strftime("%H:%M:%S")
        self.clock_label.config(text=f"Time: {time_str}")
        self.update_theme(now.hour)
        self.root.after(1000, self.update_clock)

    def update_theme(self, hour):
        if 6 <= hour < 12:
            bg = "#FFF5BA"
            self.pet_frames = self.day_gif_frames
        elif 12 <= hour < 18:
            bg = "#87CEFA"
            self.pet_frames = self.day_gif_frames
        elif 18 <= hour < 21:
            bg = "#FFDAB9"
            self.pet_frames = self.day_gif_frames
        else:
            bg = "#2C3E50"
            self.pet_frames = self.night_gif_frames

        widgets = [
            self.root, self.clock_label, self.hunger_label, self.happiness_label,
            self.image_frame, self.pet_label, self.button_frame,
            self.feed_btn, self.play_btn
        ]
        for widget in widgets:
            widget.configure(bg=bg)

    def animate_gif(self):
        if self.pet_frames:
            self.pet_label.configure(image=self.pet_frames[self.current_frame])
            self.current_frame = (self.current_frame + 1) % len(self.pet_frames)
        self.root.after(300, self.animate_gif)

    def feed(self):
        self.pet.feed()
        self.update_ui()

    def play(self):
        self.pet.play()
        self.update_ui()

    def update_loop(self):
        while True:
            time.sleep(1)
            self.pet.decay()
            self.update_ui()

    def format_time(self, seconds):
        return str(timedelta(seconds=seconds))

    def update_ui(self):
        self.hunger_label.config(text=f"Hunger: {self.format_time(self.pet.hunger)}")
        self.happiness_label.config(text=f"Happiness: {self.format_time(self.pet.happiness)}")

    def on_close(self):
        save_state(self.pet)
        self.root.destroy()

# --- Main App Launch ---
root = tk.Tk()
root.title("Tamagotchi Desktop Pet")
app = App(root)
root.protocol("WM_DELETE_WINDOW", app.on_close)
root.mainloop()
