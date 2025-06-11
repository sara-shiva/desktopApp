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

#------ Temperature -------#

WEATHER_FILE = "weather_cache.json" # make a gitignore for that, otherwise its getting anoing

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

#------ Weather Condition -------#

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

#------ save status -------#

def save_state(pet, filename="save.json"):
    with open(filename, "w") as f:
        json.dump(vars(pet), f)

def load_state(pet, filename="save.json"):
    if os.path.exists(filename):
        with open(filename) as f:
            data = json.load(f)
            pet.__dict__.update(data)

#------ classes -------#

class Cat:
    def __init__(self):
        # initialisierung der Bedürfnisse mit entsprenchenden Zeiten
        # TODO: add Energy (so viele stunden wie du wach sein solltest)
        self.hunger = 3600
        self.happiness = 3600 

        # Ansteigen der bars
        def feed(self):
            self.hunger = min(self.hunger + 3600, 3600)
        def play(self):
            self.happiness = min(self.happiness + 3600, 3600)

        # sinken der bars
        def decay(self):
            self.hunger = max(self.hunger - 1, 0)
            self.happiness = max(self.happiness - 1, 0)

class App:
    def __init__(self, root):
        # Fenster
        self.root = root
        self.root.configure(bg="#AD62CA") # Background color
        root.geometry("400x500")

        # include pet class
        self.pet = Cat()
        load_state(self.pet)

        style = ttk.Style()
        style.theme_use('clam') #  andere themes: default, alt, classic
        style.configure("Hunger.Horizontal.TProgressbar", troughcolor='#ddd', background='#5F3470')
        style.configure("Happiness.Horizontal.TProgressbar", troughcolor='#ddd', background='#5F3470')


        # background
        original_image = Image.open("backgroundCloudsFLower.jpeg")
        resized_image = original_image.resize((240, 320), Image.Resampling.LANCZOS)  # 4:5 Verhältnis
        self.tk_image = ImageTk.PhotoImage(resized_image)
        self.image_label = tk.Label(root, image=self.tk_image, bg="#AD62CA")
        self.image_label.pack(pady=2)

        # bars and their names (yet only name and decaying time)
        self.info_frame = tk.Frame(root, bg=self.root["bg"])
        self.info_frame.pack(pady=10)

        #--- Hunger-Progressbar mit Emoji ---#
        self.hunger_container = tk.Frame(self.info_frame, bg="#92458E")
        self.hunger_container.pack(pady=2)

        self.hunger_bar = ttk.Progressbar(self.hunger_container, length=200, maximum=3600, style="Hunger.Horizontal.TProgressbar")
        self.hunger_bar.pack(side="left")

        self.hunger_icon = tk.Label(self.hunger_container, text="🦴", font=("Arial", 14), bg="#AD62CA", fg="#5C2859")
        self.hunger_icon.pack(side="right", padx=5)

        #--- Happiness-Progressbar mit Emoji ---#
        self.happiness_container = tk.Frame(self.info_frame, bg="#92458E")
        self.happiness_container.pack(pady=2)

        self.happiness_bar = ttk.Progressbar(self.happiness_container, length=200, maximum=3600, style="Happiness.Horizontal.TProgressbar")
        self.happiness_bar.pack(side="left")

        self.happiness_icon = tk.Label(self.happiness_container, text="😺", font=("Arial", 14), bg="#AD62CA", fg="#5C2859")
        self.happiness_icon.pack(side="left", padx=5)

        # # background für buttons to press, dont like them
        # self.button_frame = tk.Frame(root, bg="#694e80")
        # self.button_frame.pack(side="bottom", pady=5)

        # --- buttons ----#
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=10)

        # self.feed_btn = tk.Button(self.button_frame, text="Feed", command=self.feed, font=("Arial", 10), bg="#EC9CE8", fg="#5C2859", activebackground="#abd1f1")
        # self.feed_btn.pack(side="bottom", padx=10) # top, buttom, left, right
        # self.play_btn = tk.Button( self.button_frame, text="Play", command=self.play, font=("Arial", 10), bg="#EC9CE8", fg="#5C2859", activebackground="#abd1f1")
        # self.play_btn.pack(side="left", padx=10)

        # "Feed"-Button: ganz unten zentriert
        self.feed_btn = tk.Button(root, text="Feed", command=self.feed, font=("Arial", 10), bg="#EC9CE8", fg="#5C2859", activebackground="#abd1f1")
        self.feed_btn.place(relx=0.5, rely=1.0, anchor="s", y=-10)  # s = south (unten)

        # "Play"-Button: unten links
        self.play_btn = tk.Button(root, text="Play", command=self.play, font=("Arial", 10), bg="#EC9CE8", fg="#5C2859", activebackground="#abd1f1")
        self.play_btn.place(x=10, rely=1.0, anchor="sw", y=-10)  # sw = bottom-left

        # # clock managemnt, but not using, TODO: good digital clock drawing
        # self.clock_label = tk.Label(root, font=("Arial", 12), bg="#AD62CA", fg="white")
        # self.clock_label.pack(pady=5)
        # self.update_clock()

        #--- Gifs ----#
        self.day_gif_frames = self.load_gif("cat_is_chillin(11).gif")
        self.pet_frames = self.day_gif_frames
        self.current_frame = 0
        self.pet_label = tk.Label(root, bg="#DDE0E0")
        self.pet_label.place(relx=0.5, rely=0.45, anchor="center")  # zentriert über JPEG
        self.animate_catGif()

    #----- Outside of init -------#

    # upade ui and time configuration
    def update_ui(self):
        hunger_str = self.format_time(self.pet.hunger)
        happiness_str = self.format_time(self.pet.happiness)
        self.hunger_label.config(text=f"Hunger: {hunger_str}")
        self.happiness_label.config(text=f"Happiness: {happiness_str}")

    def update_loop(self):
        while True:
            time.sleep(1)
            self.pet.decay()
            self.update_ui()

    def format_time(self, seconds):
        return str(timedelta(seconds=seconds))

    def feed(self):
        self.pet.feed()
        self.update_ui()

    def play(self):
        self.pet.play()
        self.update_ui()

    def animate_catGif(self):
        if self.pet_frames:
            self.pet_label.configure(image=self.pet_frames[self.current_frame])
            self.current_frame = (self.current_frame + 1) % len(self.pet_frames)
        self.root.after(300, self.animate_catGif)
    
    def load_gif(self, filename):
        frames = []
        i = 0
        while True:
            try:
                frame = tk.PhotoImage(file=filename, format=f"gif -index {i}")
                # Optionale Skalierung z. B. halb so groß:
                frame = frame.subsample(2, 2)  # Verkleinert das GIF
                frames.append(frame)
                i += 1
            except tk.TclError:
                break
        return frames

    # def update_clock(self):
    #     now = datetime.datetime.now()
    #     time_str = now.strftime("%H:%M:%S")
    #     self.clock_label.config(text=f"Time: {time_str}")

    # save state when close app
    def on_close(self):
        save_state(self.pet)
        self.root.destroy()
            
        
# --- Main App Launch ---
root = tk.Tk()
root.title("Cat Desktop Pet")
app = App(root)
root.protocol("WM_DELETE_WINDOW", app.on_close)
root.mainloop()