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
        self.root.configure(bg="#AD62CA") 
        root.geometry("400x400")
        self.pet = Tamagotchi()
        load_state(self.pet)

        self.button_frame = tk.Frame(root, bg="#694e80")
        self.button_frame.pack(side="bottom", pady=5)

        self.hunger_label = tk.Label(root, text="Hunger: 1:00:00", font=("Arial", 14), bg="#EC9CE8", fg="#5C2859")
        self.hunger_label.pack(pady=5)
        self.happiness_label = tk.Label(root, text="Happiness: 1:00:00", font=("Arial", 14), bg="#EC9CE8", fg="#5C2859")
        self.happiness_label.pack(pady=5)

        self.feed_btn = tk.Button(self.button_frame, text="Feed", command=self.feed, font=("Arial", 10), bg="#EC9CE8", fg="#5C2859", activebackground="#abd1f1")
        self.feed_btn.pack(side="left", padx=10)
        self.play_btn = tk.Button(self.button_frame, text="Play", command=self.play, font=("Arial", 10), bg="#EC9CE8", fg="#5C2859", activebackground="#abd1f1")
        self.play_btn.pack(side="left", padx=10)

        self.pet_frames = []
        i = 0
        while True:
            try:
                frame = tk.PhotoImage(file="cat_is_chillin(11).gif", format=f"gif -index {i}")
                self.pet_frames.append(frame)
                i += 1
            except tk.TclError:
                break

        # Create fixed-size label container for GIF
        self.image_frame = tk.Frame(root, width=300, height=300, bg="#FCC3F9")
        self.image_frame.pack(pady=10)
        self.pet_label = tk.Label(self.image_frame, bg="#FCC3F9", width=300, height=300)
        self.pet_label.pack()

        self.current_frame = 0
        self.animate_gif()

        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()

        self.clock_label = tk.Label(root, font=("Arial", 12), bg="#AD62CA", fg="white")
        self.clock_label.pack(pady=5)
        self.update_clock()

    def update_clock(self):
        now = datetime.datetime.now()
        time_str = now.strftime("%H:%M:%S")
        self.clock_label.config(text=f"Time: {time_str}")

        hour = now.hour
        # Change background based on hour
        if 6 <= hour < 12:
            # Morning
            bg_color = "#FFF5BA"  # soft yellow
        elif 12 <= hour < 18:
            # Afternoon
            bg_color = "#87CEFA"  # sky blue
        elif 18 <= hour < 21:
            # Evening
            bg_color = "#FFDAB9"  # peach
        else:
            # Night
            bg_color = "#2C3E50"  # dark blue

        # Apply to root and all relevant widgets
        self.root.configure(bg=bg_color)
        self.clock_label.configure(bg=bg_color)
        self.hunger_label.configure(bg=bg_color)
        self.happiness_label.configure(bg=bg_color)
        self.image_frame.configure(bg=bg_color)
        self.pet_label.configure(bg=bg_color)
        self.button_frame.configure(bg=bg_color)
        self.feed_btn.configure(bg=bg_color)
        self.play_btn.configure(bg=bg_color)

        self.root.after(1000, self.update_clock)
        

    def animate_gif(self):
        self.pet_label.configure(image=self.pet_frames[self.current_frame])
        self.current_frame = (self.current_frame + 1) % len(self.pet_frames)
        self.root.after(300, self.animate_gif)  # slower = smoother

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
        hunger_str = self.format_time(self.pet.hunger)
        happiness_str = self.format_time(self.pet.happiness)
        self.hunger_label.config(text=f"Hunger: {hunger_str}")
        self.happiness_label.config(text=f"Happiness: {happiness_str}")

    def on_close(self):
        save_state(self.pet)
        self.root.destroy()

# --- Main App Launch ---
root = tk.Tk()
root.title("Tamagotchi Desktop Pet")
app = App(root)
root.protocol("WM_DELETE_WINDOW", app.on_close)
root.mainloop()
