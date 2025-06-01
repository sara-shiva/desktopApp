import tkinter as tk
from tkinter import ttk
import time
import threading
from datetime import timedelta
import json
import os
import datetime
from PIL import Image, ImageTk
import requests

######## save and loads ###########

WEATHER_FILE = "weather_cache.json"

def fetch_temperature():
    try:
        response = requests.get("https://wttr.in/Berlin?format=%t")
        if response.status_code == 200:
            temp = response.text.strip()
            save_temperature_to_file(temp)
            return temp
    except:
        pass
    return load_cached_temperature()

def save_temperature_to_file(temp):
    with open(WEATHER_FILE, "w") as f:
        json.dump({"temperature": temp, "timestamp": time.time()}, f)

def load_cached_temperature():
    if os.path.exists(WEATHER_FILE):
        with open(WEATHER_FILE) as f:
            data = json.load(f)
            if time.time() - data["timestamp"] < 1800:
                return data["temperature"]
    return "N/A"

WEATHER_CONDITION_FILE = "weather_condition_cache.json"

def fetch_condition():
    try:
        response = requests.get("https://wttr.in/Berlin?format=%C")  # %C = full weather condition like "Partly cloudy"
        if response.status_code == 200:
            condition = response.text.strip()
            save_condition_to_file(condition)
            return condition
    except:
        pass
    return load_cached_condition()

def save_condition_to_file(condition):
    with open(WEATHER_CONDITION_FILE, "w") as f:
        json.dump({"condition": condition, "timestamp": time.time()}, f)

def load_cached_condition():
    if os.path.exists(WEATHER_CONDITION_FILE):
        with open(WEATHER_CONDITION_FILE) as f:
            data = json.load(f)
            if time.time() - data["timestamp"] < 1800:  # 30 min cache
                return data["condition"]
    return "Unknown"

def save_state(pet, filename="save.json"):
    with open(filename, "w") as f:
        json.dump(vars(pet), f)

def load_state(pet, filename="save.json"):
    if os.path.exists(filename):
        with open(filename) as f:
            data = json.load(f)
            pet.__dict__.update(data)

######### classes #################

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

        style = ttk.Style()
        style.theme_use('default')

            # --- IMAGE FRAME for PET and WEATHER GIF ---
        self.image_frame = tk.Frame(root, width=300, height=300, bg="#AD62CA")
        self.image_frame.pack(pady=(10, 0))

        self.pet_label = tk.Label(self.image_frame, width=300, height=300)
        self.pet_label.pack()

        self.sunny_label = tk.Label(self.image_frame, bg=self.root["bg"])
        self.sunny_label.place(relx=1.0, rely=0.0, anchor="ne")

        # --- INFO/BARS FRAME BELOW GIFs ---
        self.info_frame = tk.Frame(root, bg="#AD62CA")
        self.info_frame.pack(pady=10)

        self.clock_label = tk.Label(self.info_frame, font=("Arial", 14), bg="#AD62CA", fg="#FCC3F9")
        self.clock_label.pack(pady=2)

        self.hunger_label = tk.Label(self.info_frame, text="Hunger", font=("Arial", 12), bg="#AD62CA", fg="#FCC3F9")
        self.hunger_label.pack()
        style.configure("Hunger.Horizontal.TProgressbar", troughcolor='#ddd', background='#5F3470')
        self.hunger_bar = ttk.Progressbar(self.info_frame, length=200, maximum=3600, style="Hunger.Horizontal.TProgressbar")
        self.hunger_bar.pack(pady=2)

        self.happiness_label = tk.Label(self.info_frame, text="Happiness", font=("Arial", 12), bg="#AD62CA", fg="#FCC3F9")
        self.happiness_label.pack()
        style.configure("happiness.Horizontal.TProgressbar", troughcolor='#ddd', background="#5F3470")
        self.happiness_bar = ttk.Progressbar(self.info_frame, length=200, maximum=3600, style="happiness.Horizontal.TProgressbar")
        self.happiness_bar.pack(pady=2)

        # --- BUTTONS at very bottom ---
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=10)

        self.feed_btn = tk.Button(self.button_frame, text="Feed", command=self.feed, font=("Arial", 12), bg="#AD62CA", fg="#FCC3F9")
        self.feed_btn.pack(side="left", padx=10)

        self.play_btn = tk.Button(self.button_frame, text="Play", command=self.play, font=("Arial", 12), bg="#AD62CA", fg="#FCC3F9")
        self.play_btn.pack(side="left", padx=10)


        # Load GIFs for day and night
        self.day_gif_frames = self.load_gif("cat_is_chillin(11).gif")
        self.night_gif_frames = self.load_gif("sleep.gif")
        self.pet_frames = self.day_gif_frames
        self.current_frame = 0
        # Load GIF for Sunny times
        self.sunny_gif_frames = self.load_gif("shiny_sun(1).gif")
        self.sunny_label = tk.Label(root, bg=self.root["bg"]) 
        self.sunny_label.place(relx=1.0, rely=0.0, anchor="ne")  # Top-right corner
        self.sunny_frame = 0

        self.night_static_image = ImageTk.PhotoImage(Image.open("cat_sleeps.png").resize((300, 300)))

        self.animate_gif()
        self.animate_sunny_gif()

        # self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        # self.update_thread.start()
        self.update_loop()

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
    

    def get_temperature_wttr():
        try:
            response = requests.get("https://wttr.in/Berlin?format=%t")
            if response.status_code == 200:
                return response.text.strip()
            else:
                return "N/A"
        except:
            return "N/A"

    def update_clock(self):
        now = datetime.datetime.now()
        time_str = now.strftime("%H:%M:%S")
        # self.clock_label.config(text=f"Time: {time_str}")

        temp = fetch_temperature()
        condition = fetch_condition()
        self.clock_label.config(text=f"Time: {time_str} | Berlin: {temp} | {condition}")

        self.update_theme(now.hour, condition)
        self.root.after(1000, self.update_clock)

    def update_theme(self, hour, condition):
        if 6 <= hour < 12:
            bg = "#64F7CB"
            self.pet_frames = self.day_gif_frames
        elif 12 <= hour < 18:
            bg = "#75C8F8"
            self.pet_frames = self.day_gif_frames
        elif 18 <= hour < 21:
            bg = "#F381B0"
            self.pet_frames = self.day_gif_frames
        else:
            bg = "#5E3683"
            self.pet_frames = []  # Clear to avoid animation
            self.pet_label.config(image=self.night_static_image)

        if "sun" in condition.lower():
            self.sunny_label.place(relx=1.0, rely=0.0, anchor="ne")  # Show
            self.sunny_label.configure(bg=bg)
        else:
            self.sunny_label.place_forget()

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

    def animate_sunny_gif(self):
        if self.sunny_gif_frames:
            self.sunny_label.configure(image=self.sunny_gif_frames[self.sunny_frame])
            self.sunny_frame = (self.sunny_frame + 1) % len(self.sunny_gif_frames)
        self.root.after(300, self.animate_sunny_gif)

    def feed(self):
        self.pet.feed()
        self.update_ui()

    def play(self):
        self.pet.play()
        self.update_ui()

    def update_loop(self):
       # while True:
            # time.sleep(1)
        self.pet.decay()
        self.update_ui()
        self.root.after(1000, self.update_ui) 

    def format_time(self, seconds):
        return str(timedelta(seconds=seconds))

    def update_ui(self):
        # self.hunger_label.config(text=f"Hunger: {self.format_time(self.pet.hunger)}")
        # self.happiness_label.config(text=f"Happiness: {self.format_time(self.pet.happiness)}")
        self.hunger_bar["value"] = self.pet.hunger
        self.happiness_bar["value"] = self.pet.happiness

    def on_close(self):
        save_state(self.pet)
        self.root.destroy()

# --- Main App Launch ---
root = tk.Tk()
root.title("Tamagotchi Desktop Pet")
app = App(root)
root.protocol("WM_DELETE_WINDOW", app.on_close)
root.mainloop()
