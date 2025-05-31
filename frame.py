import tkinter as tk
import time
import threading
from datetime import timedelta
import json
import os

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
        root.geometry("400x300")
        self.pet = Tamagotchi()
        load_state(self.pet)

        self.button_frame = tk.Frame(root, bg="#694e80")
        self.button_frame.pack(side="bottom", pady=1)

        self.hunger_label = tk.Label(root, text="Hunger: 1:00:00", font=("Arial", 14), bg="#EC9CE8", fg="#5C2859")
        self.hunger_label.pack(pady=10)
        self.happiness_label = tk.Label(root, text="Happiness: 1:00:00", font=("Arial", 14), bg="#EC9CE8", fg="#5C2859")
        self.happiness_label.pack(pady=10)

        self.feed_btn = tk.Button(self.button_frame, text="Feed", command=self.feed, font=("Arial", 10), bg="#EC9CE8", fg="#5C2859", activebackground="#abd1f1") # activebackground="#528bbd"
        self.feed_btn.pack(pady=5)
        self.play_btn = tk.Button(self.button_frame, text="Play", command=self.play, font=("Arial", 10), bg="#EC9CE8", fg="#5C2859", activebackground="#abd1f1")
        self.play_btn.pack(pady=5)

        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()

        self.pet_frames = []
        i = 0
        while True:
            try:
                frame = tk.PhotoImage(file="catGIF_edit.gif", format=f"gif -index {i}")
                self.pet_frames.append(frame)
                i += 1
            except tk.TclError:
                break
        #self.pet_frames = [tk.PhotoImage(file="catGIF.gif", format=f"gif -index {i}") for i in range(6)]
        self.pet_label = tk.Label(root, bg="#FCC3F9")
        self.pet_label.pack(pady=20)
        self.current_frame = 0
        self.animate_gif()

    def animate_gif(self):
        self.pet_label.configure(image=self.pet_frames[self.current_frame])
        self.current_frame = (self.current_frame + 1) % len(self.pet_frames)
        self.root.after(100, self.animate_gif)  # change frame every 100 ms

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
