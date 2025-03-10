import os
import csv
import cv2
import datetime
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
from collections import defaultdict

class FileComparator:
    def __init__(self, root):
        self.root = root
        self.root.title("File Comparator")
        self.root.geometry("1200x800")
        
        self.file_data = []  # Lista plików do porównania
        self.current_index = 0  # Indeks aktualnie porównywanych plików
        self.compare_by_name = tk.BooleanVar()
        self.compare_by_size = tk.BooleanVar()
        
        self.load_button = tk.Button(root, text="Scan Directory", command=self.scan_directory)
        self.load_button.pack()
        
        self.compare_name_check = tk.Checkbutton(root, text="Compare by Name", variable=self.compare_by_name)
        self.compare_name_check.pack()
        self.compare_size_check = tk.Checkbutton(root, text="Compare by Size", variable=self.compare_by_size)
        self.compare_size_check.pack()
        
        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack()
        
        self.info_label = tk.Label(root, text="")
        self.info_label.pack()
        
        self.next_button = tk.Button(root, text="Next", command=self.next_pair)
        self.next_button.pack()
        
    def scan_directory(self):
        folder = filedialog.askdirectory()
        if not folder:
            return
        
        file_info = []
        file_dict = defaultdict(list)
        
        for root, _, files in os.walk(folder):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(file_path)
                    file_info.append((file, size, file_path))
                    file_dict[file].append((size, file_path))
                except OSError:
                    print(f'Błąd dostępu do pliku: {file_path}')
        
        filtered_files = {}
        for name, items in file_dict.items():
            if len(items) > 1:
                filtered_files[name] = sorted(items, key=lambda x: -x[0])
        
        self.file_data = filtered_files
        self.current_index = 0
        self.show_comparison()
    
    def show_comparison(self):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        
        if not self.file_data:
            self.info_label.config(text="No more files to compare.")
            return
        
        name, files = list(self.file_data.items())[self.current_index]
        num_files = len(files)
        thumbnail_size = 400 if num_files == 1 else min(400, int(1200 / num_files) - 20)
        
        for i, (size, path) in enumerate(files):
            frame = tk.Frame(self.canvas_frame)
            frame.pack(side=tk.LEFT, padx=10, pady=10)
            
            label = tk.Label(frame, text=f"Found_{i+1}\nSize: {size}\nPath: {path}")
            label.pack()
            
            open_button = tk.Button(frame, text="Open Location", command=lambda p=path: os.startfile(os.path.dirname(p)))
            open_button.pack()
            
            run_button = tk.Button(frame, text="Run", command=lambda p=path: os.startfile(p))
            run_button.pack()
            
            self.display_file(path, frame, thumbnail_size)
        
    def display_file(self, file_path, frame, thumbnail_size):
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            image = Image.open(file_path)
            image.thumbnail((thumbnail_size, thumbnail_size))
            img = ImageTk.PhotoImage(image)
            lbl = tk.Label(frame, image=img)
            lbl.image = img
            lbl.pack()
        elif file_path.lower().endswith('.mp4'):
            cap = cv2.VideoCapture(file_path)
            ret, frame_img = cap.read()
            if ret:
                frame_img = cv2.cvtColor(frame_img, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame_img)
                image.thumbnail((thumbnail_size, thumbnail_size))
                img = ImageTk.PhotoImage(image)
                lbl = tk.Label(frame, image=img)
                lbl.image = img
                lbl.pack()
            cap.release()
    
    def next_pair(self):
        self.current_index += 1
        if self.current_index >= len(self.file_data):
            self.current_index = 0
        self.show_comparison()

if __name__ == "__main__":
    root = tk.Tk()
    app = FileComparator(root)
    root.mainloop()
