import os
import csv
import cv2
import datetime
import tkinter as tk
from tkinter import filedialog, ttk, font as tkfont
from PIL import Image, ImageTk
from collections import defaultdict

class FileComparator:
    def __init__(self, root):
        self.root = root
        self.root.title("File Comparator")
        self.root.geometry("1200x800")
        
        # Increase default font size
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(size=default_font.cget("size") + 2)
        text_font = tkfont.nametofont("TkTextFont")
        text_font.configure(size=text_font.cget("size") + 2)
        
        self.file_data = []  # Lista plików do porównania
        self.current_index = 0  # Indeks aktualnie porównywanych plików
        self.compare_by_name = tk.BooleanVar(value=True)  # Default to true for name comparison
        self.compare_by_size = tk.BooleanVar(value=False)
        self.deleted_files = set()  # Set to track deleted files
        self.current_directory = ""  # Store the currently scanned directory
        
        self.control_frame = tk.Frame(root)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        self.load_button = tk.Button(self.control_frame, text="Scan Directory", command=self.scan_directory)
        self.load_button.pack(pady=5)
        
        self.compare_name_check = tk.Checkbutton(self.control_frame, text="Compare by Name", variable=self.compare_by_name)
        self.compare_name_check.pack(pady=2)
        self.compare_size_check = tk.Checkbutton(self.control_frame, text="Compare by Size", variable=self.compare_by_size)
        self.compare_size_check.pack(pady=2)
        
        self.refresh_button = tk.Button(self.control_frame, text="Refresh", command=self.rescan_directory)
        self.refresh_button.pack(pady=5)
        
        self.file_listbox = tk.Listbox(self.control_frame, height=40, width=30, font=("TkDefaultFont", default_font.cget("size")))
        self.file_listbox.pack(fill=tk.Y, expand=True)
        self.file_listbox.bind("<<ListboxSelect>>", self.select_file)
        
        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.info_label = tk.Label(root, text="", font=("TkDefaultFont", default_font.cget("size")))
        self.info_label.pack(pady=5)
    
    def scan_directory(self):
        folder = filedialog.askdirectory()
        if not folder:
            return
        
        self.current_directory = folder
        self.process_directory(folder)
    
    def rescan_directory(self):
        """Rescans the current directory with the current filter settings"""
        if not self.current_directory:
            self.info_label.config(text="No directory selected yet. Please scan a directory first.", fg="red")
            return
        
        self.process_directory(self.current_directory)
    
    def process_directory(self, folder):
        """Process the directory according to the current filter settings"""
        file_info = []
        
        for root, _, files in os.walk(folder):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(file_path)
                    file_info.append((file, size, file_path))
                except OSError:
                    print(f'Błąd dostępu do pliku: {file_path}')
        
        # Group files according to selected criteria
        filtered_files = {}
        
        if self.compare_by_name.get() and self.compare_by_size.get():
            # Group by both name and size
            file_dict = defaultdict(list)
            for name, size, path in file_info:
                key = (name, size)  # Use tuple of name and size as key
                file_dict[key].append((size, path))
            
            # Filter to show only duplicates
            for (name, size), items in file_dict.items():
                if len(items) > 1:
                    display_name = f"{name} ({size} bytes)"
                    filtered_files[display_name] = items
        
        elif self.compare_by_size.get():
            # Group only by size
            file_dict = defaultdict(list)
            for name, size, path in file_info:
                file_dict[size].append((size, path))
            
            # Filter to show only duplicates
            for size, items in file_dict.items():
                if len(items) > 1:
                    display_name = f"Size: {size} bytes ({len(items)} files)"
                    filtered_files[display_name] = items
        
        elif self.compare_by_name.get():
            # Group by name only
            file_dict = defaultdict(list)
            for name, size, path in file_info:
                file_dict[name].append((size, path))
            
            # Filter to show only duplicates
            for name, items in file_dict.items():
                if len(items) > 1:
                    filtered_files[name] = sorted(items, key=lambda x: -x[0])  # Sort by size descending
        
        else:
            # If no criteria selected, default to name comparison
            self.compare_by_name.set(True)
            self.process_directory(folder)
            return
        
        self.file_data = filtered_files
        self.current_index = 0
        self.refresh_list()
    
    def refresh_list(self):
        self.file_listbox.delete(0, tk.END)
        
        if not self.file_data:
            self.info_label.config(text="No duplicate files found with current criteria.")
            # Clear comparison view
            for widget in self.canvas_frame.winfo_children():
                widget.destroy()
            return
            
        for i, name in enumerate(self.file_data.keys()):
            self.file_listbox.insert(tk.END, name)
            # Check if any files for this name have been deleted
            files_for_name = [path for _, path in self.file_data[name]]
            has_deleted = any(path in self.deleted_files for path in files_for_name)
            if has_deleted:
                self.file_listbox.itemconfig(i, fg="red")
        
        # Select first item in the list
        if self.file_listbox.size() > 0:
            self.file_listbox.selection_set(0)
            self.current_index = 0
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
        
        # Display file comparison title
        title_label = tk.Label(self.canvas_frame, text=f"Comparing: {name}", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Create a frame for the file previews
        previews_frame = tk.Frame(self.canvas_frame)
        previews_frame.pack(fill=tk.BOTH, expand=True)
        
        for i, (size, path) in enumerate(files):
            frame = tk.Frame(previews_frame)
            frame.pack(side=tk.LEFT, padx=10, pady=10)
            
            # Create label with wrapped text for path
            path_frame = tk.Frame(frame, width=thumbnail_size)
            path_frame.pack(fill=tk.X)
            path_frame.pack_propagate(False)  # Don't let the frame resize to fit contents
            
            # File info label with increased font
            info_label = tk.Label(path_frame, 
                                text=f"Found_{i+1}\nSize: {size} bytes",
                                wraplength=thumbnail_size)
            info_label.pack(fill=tk.X)
            
            # Path label with wrapping
            path_label = tk.Label(path_frame, 
                                text=f"Path: {path}",
                                wraplength=thumbnail_size,
                                justify=tk.LEFT)
            path_label.pack(fill=tk.X)
            
            # Action buttons
            buttons_frame = tk.Frame(frame)
            buttons_frame.pack(fill=tk.X, pady=5)
            
            open_button = tk.Button(buttons_frame, text="Open Location",
                                  command=lambda p=path: os.startfile(os.path.dirname(p)))
            open_button.pack(side=tk.LEFT, padx=2)
            
            run_button = tk.Button(buttons_frame, text="Run",
                                command=lambda p=path: os.startfile(p))
            run_button.pack(side=tk.LEFT, padx=2)
            
            # Display file preview
            self.display_file(path, frame, thumbnail_size)
            
            # Move delete button below the preview
            delete_button = tk.Button(frame, text="Delete", bg="#ff9999", 
                                    command=lambda p=path, f=frame, n=name: self.delete_file(p, f, n))
            delete_button.pack(fill=tk.X, pady=5)
    
    def display_file(self, file_path, frame, thumbnail_size):
        preview_frame = tk.Frame(frame, width=thumbnail_size, height=thumbnail_size)
        preview_frame.pack(pady=5)
        
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            try:
                image = Image.open(file_path)
                image.thumbnail((thumbnail_size, thumbnail_size))
                img = ImageTk.PhotoImage(image)
                lbl = tk.Label(preview_frame, image=img)
                lbl.image = img
                lbl.pack()
            except Exception as e:
                error_label = tk.Label(preview_frame, text="Error loading image")
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
                    lbl = tk.Label(preview_frame, image=img)
                    lbl.image = img
                    lbl.pack()
                cap.release()
            except Exception as e:
                error_label = tk.Label(preview_frame, text="Error loading video")
                error_label.pack()
        else:
            # For non-media files, show file type icon or text
            file_ext = os.path.splitext(file_path)[1]
            type_label = tk.Label(preview_frame, 
                                text=f"File type:\n{file_ext}", 
                                width=thumbnail_size//10,
                                height=thumbnail_size//20)
            type_label.pack(expand=True)
    
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