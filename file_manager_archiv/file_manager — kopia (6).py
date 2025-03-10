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
        self.deleted_files = set()  # Set to track deleted files
        
        self.control_frame = tk.Frame(root)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        self.load_button = tk.Button(self.control_frame, text="Scan Directory", command=self.scan_directory)
        self.load_button.pack()
        
        self.compare_name_check = tk.Checkbutton(self.control_frame, text="Compare by Name", variable=self.compare_by_name, command=self.refresh_list)
        self.compare_name_check.pack()
        self.compare_size_check = tk.Checkbutton(self.control_frame, text="Compare by Size", variable=self.compare_by_size, command=self.refresh_list)
        self.compare_size_check.pack()
        
        self.refresh_button = tk.Button(self.control_frame, text="Refresh", command=self.refresh_list)
        self.refresh_button.pack()
        
        self.file_listbox = tk.Listbox(self.control_frame, height=40, width=30)
        self.file_listbox.pack(fill=tk.Y, expand=True)
        self.file_listbox.bind("<<ListboxSelect>>", self.select_file)
        
        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.info_label = tk.Label(root, text="")
        self.info_label.pack()
    
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
        self.refresh_list()
        self.show_comparison()
    
    def refresh_list(self):
        self.file_listbox.delete(0, tk.END)
        for i, name in enumerate(self.file_data.keys()):
            self.file_listbox.insert(tk.END, name)
            # Check if any files for this name have been deleted
            files_for_name = [path for _, path in self.file_data[name]]
            has_deleted = any(path in self.deleted_files for path in files_for_name)
            if has_deleted:
                self.file_listbox.itemconfig(i, fg="red")
        
        self.show_comparison()
    
    def select_file(self, event):
        selection = self.file_listbox.curselection()
        if selection:
            self.current_index = selection[0]
            self.show_comparison()
    
    def show_comparison(self):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        
        if not self.file_data:
            self.info_label.config(text="No more files to compare.")
            return
        
        name, files = list(self.file_data.items())[self.current_index]
        num_files = len(files)
        thumbnail_size = max(100, min(400, int(1200 / num_files) - 20))
        
        for i, (size, path) in enumerate(files):
            frame = tk.Frame(self.canvas_frame)
            frame.pack(side=tk.LEFT, padx=10, pady=10)
            
            label = tk.Label(frame, text=f"Found_{i+1}\nSize: {size}\nPath: {path}")
            label.pack()
            
            open_button = tk.Button(frame, text="Open Location", command=lambda p=path: os.startfile(os.path.dirname(p)))
            open_button.pack()
            
            run_button = tk.Button(frame, text="Run", command=lambda p=path: os.startfile(p))
            run_button.pack()
            
            # Display file preview before delete button
            self.display_file(path, frame, thumbnail_size)
            
            # Move delete button below the preview
            delete_button = tk.Button(frame, text="Delete", command=lambda p=path, f=frame, n=name: self.delete_file(p, f, n))
            delete_button.pack()
    
    def display_file(self, file_path, frame, thumbnail_size):
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            try:
                image = Image.open(file_path)
                image.thumbnail((thumbnail_size, thumbnail_size))
                img = ImageTk.PhotoImage(image)
                lbl = tk.Label(frame, image=img)
                lbl.image = img
                lbl.pack()
            except Exception as e:
                error_label = tk.Label(frame, text="Error loading image")
                error_label.pack()
        elif file_path.lower().endswith('.mp4'):
            try:
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
            except Exception as e:
                error_label = tk.Label(frame, text="Error loading video")
                error_label.pack()
    
    def delete_file(self, file_path, frame, file_name):
        try:
            os.remove(file_path)
            self.deleted_files.add(file_path)  # Add path to deleted files set
            frame.destroy()
            self.info_label.config(text=f"Deleted: {file_path}", fg="green")
            
            # Update file list and color in the listbox
            names = list(self.file_data.keys())
            if file_name in names:
                idx = names.index(file_name)
                self.file_listbox.itemconfig(idx, fg="red")
            
            # Clean up data structure if needed
            remaining_files = [(size, path) for size, path in self.file_data[file_name] if path != file_path]
            if remaining_files:
                self.file_data[file_name] = remaining_files
            else:
                del self.file_data[file_name]
                
            # Refresh the display
            self.root.after(500, self.refresh_list)
        except Exception as e:
            self.info_label.config(text=f"Failed to delete: {file_path} - {str(e)}", fg="red")
    
if __name__ == "__main__":
    root = tk.Tk()
    app = FileComparator(root)
    root.mainloop()