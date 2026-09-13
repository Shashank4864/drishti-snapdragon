import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import threading
import time
import os

from Vision import read_image
from Language import simplify_and_translate, LANG_MAP
from Speech import speak

class DrishtiApp:
    def __init__(self, root):
        self.root = root
        root.title("Drishti — See it. Hear it. Understand it.")
        root.geometry("500x600")

        tk.Label(root, text="👁️ Drishti", font=("Arial", 20, "bold")).pack(pady=10)
        tk.Label(root, text="Fully offline · Runs entirely on-device", font=("Arial", 10)).pack()

        tk.Label(root, text="Choose language:").pack(pady=(20, 0))
        self.lang_var = tk.StringVar(value="Hindi")
        tk.OptionMenu(root, self.lang_var, *LANG_MAP.keys()).pack()

        tk.Button(root, text="Select Image", command=self.select_image, font=("Arial", 12)).pack(pady=20)

        self.image_label = tk.Label(root)
        self.image_label.pack()

        self.status_label = tk.Label(root, text="", font=("Arial", 10), fg="blue")
        self.status_label.pack(pady=10)

        self.result_text = tk.Text(root, height=8, width=55, wrap="word")
        self.result_text.pack(pady=10)

        self.image_path = None

    def select_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png")])
        if not path:
            return
        self.image_path = path

        img = Image.open(path)
        img.thumbnail((300, 300))
        photo = ImageTk.PhotoImage(img)
        self.image_label.config(image=photo)
        self.image_label.image = photo

        threading.Thread(target=self.process_image, daemon=True).start()

    def process_image(self):
        self.set_status("Reading image...")
        t0 = time.time()
        raw = read_image(self.image_path, instruction="Read all visible text word for word, exactly as written.")
        t1 = time.time()

        self.set_status(f"Translating to {self.lang_var.get()}...")
        translated = simplify_and_translate(raw, target_lang=self.lang_var.get())
        t2 = time.time()