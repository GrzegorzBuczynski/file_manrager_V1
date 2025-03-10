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
        self.root.geometry("1000x600")
        
        self.file_data = []  # Lista plików do porównania
        self.current_index = 0  # Indeks aktualnie porównywanych plików

        self.load_button = tk.Button(root, text="Scan Directory", command=self.scan_directory)
        self.load_button.pack()
        
        self.canvas_left = tk.Label(root)
        self.canvas_left.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.canvas_right = tk.Label(root)
        self.canvas_right.pack(side=tk.RIGHT, padx=10, pady=10)
        
        self.info_label = tk.Label(root, text="")
        self.info_label.pack()
        
        self.next_button = tk.Button(root, text="Next", command=self.next_pair)
        self.next_button.pack()
        
        self.delete_left_button = tk.Button(root, text="Delete Left", command=lambda: self.delete_file(0))
        self.delete_left_button.pack(side=tk.LEFT, padx=20)
        
        self.delete_right_button = tk.Button(root, text="Delete Right", command=lambda: self.delete_file(1))
        self.delete_right_button.pack(side=tk.RIGHT, padx=20)
    
    def scan_directory(self):
        folder = filedialog.askdirectory()
        if not folder:
            return
        
        file_info = []
        file_names = defaultdict(list)
        name_variants = defaultdict(list)
        
        for root, _, files in os.walk(folder):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(file_path)
                    file_info.append((file, size, file_path))
                    file_names[(file, size)].append(file_path)
                    name_variants[file].append((size, file_path))
                except OSError:
                    print(f'Błąd dostępu do pliku: {file_path}')
        
        duplicates = {key: paths for key, paths in file_names.items() if len(paths) > 1}
        
        sorted_files = []
        for name, size, path in file_info:
            if (name, size) in duplicates:
                status = "DUP"
                sorted_files.append((status, size, name, path))
        
        sorted_files.sort(key=lambda x: (-x[1]))
        self.file_data = sorted_files
        self.current_index = 0
        self.show_pair()
    
    def show_pair(self):
        if self.current_index >= len(self.file_data) - 1:
            self.info_label.config(text="No more files to compare.")
            return
        
        left_file = self.file_data[self.current_index][3]
        right_file = self.file_data[self.current_index + 1][3]
        
        self.display_file(left_file, self.canvas_left)
        self.display_file(right_file, self.canvas_right)
        
        self.info_label.config(text=f"Comparing: {os.path.basename(left_file)} vs {os.path.basename(right_file)}")
    
    def display_file(self, file_path, canvas):
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            image = Image.open(file_path)
            image.thumbnail((400, 400))
            img = ImageTk.PhotoImage(image)
            canvas.config(image=img)
            canvas.image = img
        elif file_path.lower().endswith('.mp4'):
            cap = cv2.VideoCapture(file_path)
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame)
                image.thumbnail((400, 400))
                img = ImageTk.PhotoImage(image)
                canvas.config(image=img)
                canvas.image = img
            cap.release()
    
    def delete_file(self, side):
        file_path = self.file_data[self.current_index + side][3]
        try:
            os.remove(file_path)
            self.info_label.config(text=f"Deleted: {file_path}")
            del self.file_data[self.current_index + side]
            self.show_pair()
        except Exception as e:
            self.info_label.config(text=f"Error deleting {file_path}: {e}")
    
    def next_pair(self):
        self.current_index += 2
        self.show_pair()

if __name__ == "__main__":
    root = tk.Tk()
    app = FileComparator(root)
    root.mainloop()
