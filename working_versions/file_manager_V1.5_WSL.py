import os
import csv
import cv2
import datetime
import tkinter as tk
import subprocess
import sys
from tkinter import filedialog, ttk, font as tkfont
from PIL import Image, ImageTk
from collections import defaultdict

def open_location(p):
    try:
        path = os.path.dirname(p)
        # Sprawdź czy to WSL
        if "microsoft" in os.uname().release.lower():
            # Konwertuj ścieżkę do formatu Windows
            if path.startswith("/mnt/"):
                drive = path[5:6].upper()
                windows_path = f"{drive}:{path[6:]}".replace("/", "\\")
            else:
                windows_path = path  # Obsługa przypadku, gdy ścieżka nie zaczyna się od /mnt/
            
            print(f"Otwieranie w WSL, konwertowana ścieżka: {windows_path}")
            subprocess.run(["explorer.exe", windows_path])
        elif sys.platform == "win32":
            # Windows
            os.startfile(path)
        else:
            # Standardowy Linux
            subprocess.run(["xdg-open", path])
    except Exception as e:
        print(f"Błąd otwierania lokalizacji: {str(e)}")
        update_info_label(app, f"Błąd: {str(e)}", "red")

def run_file(p):
    try:
        # Sprawdź czy to WSL
        if "microsoft" in os.uname().release.lower():
            # Konwertuj ścieżkę do formatu Windows
            if p.startswith("/mnt/"):
                drive = p[5:6].upper()
                windows_path = f"{drive}:{p[6:]}".replace("/", "\\")
            else:
                windows_path = p
            
            print(f"Uruchamianie w WSL, konwertowana ścieżka: {windows_path}")
            subprocess.run(["cmd.exe", "/c", "start", "", windows_path])
        elif sys.platform == "win32":
            # Windows
            os.startfile(p)
        else:
            # Standardowy Linux
            subprocess.run(["xdg-open", p])
    except Exception as e:
        print(f"Błąd uruchamiania pliku: {str(e)}")
        update_info_label(app, f"Błąd: {str(e)}", "red")


def create_action_buttons(frame, path):
    buttons_frame = tk.Frame(frame)
    buttons_frame.pack(fill=tk.X, pady=5)

    open_button = tk.Button(buttons_frame, text="Open Location",
                            command=lambda p=path: open_location(p))
    open_button.pack(side=tk.LEFT, padx=2)

    run_button = tk.Button(buttons_frame, text="Run",
                           command=lambda p=path: run_file(p))
    run_button.pack(side=tk.LEFT, padx=2)

def display_file(file_path, frame, thumbnail_size):
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
        file_ext = os.path.splitext(file_path)[1]
        type_label = tk.Label(preview_frame, 
                            text=f"File type:\n{file_ext}", 
                            width=thumbnail_size//10,
                            height=thumbnail_size//20)
        type_label.pack(expand=True)

def create_delete_button(frame, path, name, app):
    delete_button = tk.Button(frame, text="Delete", bg="#ff9999", 
                              command=lambda p=path, f=frame, n=name: delete_file(app, p, f, n))
    delete_button.pack(fill=tk.X, pady=5)

def format_size(size):
    size_kb = size / 1024
    return f"{size_kb:,.0f} KB"


def scan_directory(app):
    update_info_label(app, "Selecting directory: .....", "blue")
    folder = filedialog.askdirectory()  # Otwieramy okno dialogowe wyboru katalogu
    if not folder:
        update_info_label(app, "No directory selected.", "red")
        return
    
    # Zapisujemy katalog
    app.current_directory = folder
    refresh_app(app)

def refresh_app(app):
    if not app.current_directory:
        update_info_label(app, "No directory selected.", "red")
        return

    # Resetujemy dane aplikacji
    app.file_data = {}
    app.current_index = 0
    
    # Przetwarzamy katalog
    process_directory(app)
    
    # Odświeżamy listę 
    refresh_list(app)
    
    # Pokazujemy porównanie, jeśli są dane
    if app.file_data:
        show_comparison(app)
    else:
        update_info_label(app, "No duplicate files found with current criteria.", "green")

def update_info_label(app, text, color):
    app.info_label.config(text=text, fg=color)
    app.root.update()  # Odświeżamy UI

def scan_files(folder):
    file_info = []  # Lista krotek (nazwa, rozmiar, ścieżka)
    for root, _, files in os.walk(folder):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                size = os.path.getsize(file_path)
                file_info.append((file, size, file_path))
            except OSError:
                print(f'Błąd dostępu do pliku: {file_path}')
    return file_info

def filter_files(app, file_info):
    filtered_files = {}
    if app.compare_by_name.get() and app.compare_by_size.get():
        file_dict = defaultdict(list)
        for name, size, path in file_info:
            key = (name, size)
            file_dict[key].append((size, path))
        for (name, size), items in file_dict.items():
            if len(items) > 1:
                display_name = f"{name} ({size} bytes)"
                filtered_files[display_name] = items
    elif app.compare_by_size.get():
        file_dict = defaultdict(list)
        for name, size, path in file_info:
            file_dict[size].append((size, path))
        for size, items in file_dict.items():
            if len(items) > 1:
                display_name = f"Size: {size} bytes ({len(items)} files)"
                filtered_files[display_name] = items
    elif app.compare_by_name.get():
        file_dict = defaultdict(list)
        for name, size, path in file_info:
            file_dict[name].append((size, path))
        for name, items in file_dict.items():
            if len(items) > 1:
                filtered_files[name] = sorted(items, key=lambda x: -x[0])
    else:
        app.compare_by_name.set(True)
        return filter_files(app, file_info)
    return filtered_files

def update_file_data(app, filtered_files):
    app.file_data = filtered_files
    if app.file_data:
        update_info_label(app, f"Found {len(app.file_data)} groups of duplicate files.", "green")
    else:
        update_info_label(app, "No duplicate files found with current criteria.", "blue")

def process_directory(app):
    update_info_label(app, f"Scanning directory: {app.current_directory}...", "blue")
    file_info = scan_files(app.current_directory)
    filtered_files = filter_files(app, file_info)
    update_file_data(app, filtered_files)

def refresh_list(app):
    # Zachowujemy bieżący wybór
    current_selection = app.file_listbox.curselection() # Pobieramy indeksy zaznaczonych elementów
    if current_selection:
        current_selection = current_selection[0] # Pobieramy pierwszy zaznaczony element
    else:
        current_selection = 0

    # Czyścimy listę
    app.file_listbox.delete(0, tk.END) # Usuwamy wszystkie elementy z listboxa
    
    # Sprawdzamy czy są dane
    if not app.file_data:
        for widget in app.canvas_frame.winfo_children(): # Usuwamy wszystkie widgety z ramki canvas
            widget.destroy()
        create_info_frame(app)  # Tworzymy ramkę informacyjną
        app.info_label.config(text="No duplicate files found with current criteria.")
        return
    
    # Wypełniamy listę
    for i, name in enumerate(app.file_data.keys()):
        app.file_listbox.insert(tk.END, name)
        files_for_name = [path for _, path in app.file_data[name]]
        has_deleted = any(path in app.deleted_files for path in files_for_name)
        if has_deleted:
            app.file_listbox.itemconfig(i, fg="red")
    
    # Wybieramy element
    if app.file_listbox.size() > 0:
        if current_selection >= app.file_listbox.size():
            current_selection = app.file_listbox.size() - 1
        app.file_listbox.selection_set(current_selection)
        app.current_index = current_selection

def select_file(app, event):
    selection = app.file_listbox.curselection()
    if selection:
        app.current_index = selection[0]
        show_comparison(app)

def show_comparison(app):
    # Czyścimy ramkę canvas
    for widget in app.canvas_frame.winfo_children():
        widget.destroy()
    
    create_info_frame(app)
    
    # Sprawdzamy czy są dane
    if not app.file_data:
        create_info_frame(app)
        app.info_label.config(text="No more files to compare.")
        return
    
    # Sprawdzamy czy indeks jest prawidłowy
    if app.current_index >= len(list(app.file_data.keys())):
        if len(app.file_data) > 0:
            app.current_index = 0
        else:
            create_info_frame(app)
            app.info_label.config(text="No more files to compare.")
            return
    
    # Pobieramy dane dla bieżącego indeksu
    name, files = list(app.file_data.items())[app.current_index]
    num_files = len(files)
    
    # Obliczamy rozmiar miniaturki
    thumbnail_size = max(100, min(400, int(1200 / num_files) - 20))

    # Tworzymy ramkę informacyjną
    # create_info_frame(app)
    
    # Tworzymy tytuł porównania
    create_comparison_title(app, name)
    
    # Tworzymy ramkę z ścieżkami
    create_paths_frame(app, files, thumbnail_size)
    
    # Tworzymy ramkę z akcjami
    create_actions_frame(app, files, thumbnail_size, name)

def create_info_frame(app):
    info_frame = tk.Frame(app.canvas_frame)
    info_frame.pack(fill=tk.X, pady=(0, 10))
    
    app.info_label = tk.Label(info_frame, text="", font=("TkDefaultFont", app.default_font.cget("size")))
    app.info_label.pack(fill=tk.X)

def create_comparison_title(app, name):
    comparison_title = tk.Frame(app.canvas_frame, height=int(0.2 * app.canvas_frame.winfo_toplevel().winfo_height()))
    comparison_title.pack(fill=tk.X, expand=False)

    title_label = tk.Label(comparison_title, text=f"Comparing: {name}", font=("Arial", 14, "bold"))
    title_label.pack(fill=tk.X, pady=5)

def create_paths_frame(app, files, thumbnail_size):
    paths_frame = tk.Frame(app.canvas_frame)
    paths_frame.pack(fill=tk.BOTH, expand=False)

    for i, (size, path) in enumerate(files):
        path_frame = tk.Frame(paths_frame, width=thumbnail_size, height=(0.5 * thumbnail_size))
        path_frame.grid(row=0, column=i, padx=0, pady=10)
        formatted_size = format_size(size)
        info_label = tk.Label(path_frame, text=f"Found_{i+1}\nSize: {formatted_size}", wraplength=thumbnail_size)
        info_label.pack(fill=tk.X)
        path_label = tk.Label(path_frame, text=f"Path: {path}", wraplength=thumbnail_size, justify=tk.LEFT, anchor="w")
        path_label.pack(fill=tk.X)

def create_actions_frame(app, files, thumbnail_size, name):
    actions_frame = tk.Frame(app.canvas_frame)
    actions_frame.pack(fill=tk.BOTH, expand=False)

    for i, (size, path) in enumerate(files):
        frame = tk.Frame(actions_frame)
        frame.pack(side=tk.LEFT, padx=10, pady=10)
        create_action_buttons(frame, path)
        display_file(path, frame, thumbnail_size)
        create_delete_button(frame, path, name, app)

def delete_file(app, file_path, frame, file_name):
    try:
        os.remove(file_path)
        app.deleted_files.add(file_path)
        frame.destroy()
        app.info_label.config(text=f"Deleted: {file_path}", fg="green")
        
        names = list(app.file_data.keys())
        if file_name in names:
            idx = names.index(file_name)
            app.file_listbox.itemconfig(idx, fg="red")
        
        remaining_files = [(size, path) for size, path in app.file_data[file_name] if path != file_path]
        if remaining_files:
            app.file_data[file_name] = remaining_files
        else:
            del app.file_data[file_name]
            refresh_list(app)
            
        app.root.after(2000, lambda: show_comparison(app))
    except Exception as e:
        app.info_label.config(text=f"Failed to delete: {file_path} - {str(e)}", fg="red")



def setup_controls_frame(app):
    # Tworzymy ramkę kontrolną
    app.control_frame = tk.Frame(app.root)
    app.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

    # Dodajemy przycisk do skanowania katalogu
    app.load_button = tk.Button(app.control_frame, text="Scan Directory", command=lambda: scan_directory(app))
    app.load_button.pack(pady=5)

    # Dodajemy pola wyboru
    app.compare_name_check = tk.Checkbutton(app.control_frame, text="Compare by Name", variable=app.compare_by_name)
    app.compare_name_check.pack(pady=2)
    app.compare_size_check = tk.Checkbutton(app.control_frame, text="Compare by Size", variable=app.compare_by_size)
    app.compare_size_check.pack(pady=2)

    # Dodajemy przycisk do odświeżania
    app.refresh_button = tk.Button(app.control_frame, text="Refresh", command=lambda: refresh_app(app))
    app.refresh_button.pack(pady=5)

    # Dodajemy listę plików
    app.file_listbox = tk.Listbox(app.control_frame, height=40, width=30, font=("TkDefaultFont", app.default_font.cget("size")))
    app.file_listbox.pack(fill=tk.Y, expand=True)
    app.file_listbox.bind("<<ListboxSelect>>", lambda event: select_file(app, event))
        


def setup_canvas_frame(app):
    # Tworzymy ramkę canvas
    app.canvas_frame = tk.Frame(app.root)
    app.canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # Tworzymy ramkę informacyjną w ramce canvas
    info_frame = tk.Frame(app.canvas_frame)
    info_frame.pack(fill=tk.X, pady=(0, 10))
    
    # Tworzymy etykietę informacyjną w ramce informacyjnej
    # label do debugowania
    app.info_label = tk.Label(info_frame, text="", font=("TkDefaultFont", app.default_font.cget("size")))
    app.info_label.pack(fill=tk.X)
    app.info_label.config(text=f"test", fg="green")

def refresh_canvas(app):
    for widget in app.canvas_frame.winfo_children():
        widget.destroy()
    create_info_frame(app)
    # app.info_label.config(text="Canvas refreshed.", fg="blue")

class FileComparator:
    def __init__(self, root):
        self.root = root
        self.root.title("File Comparator")
        self.root.geometry("1200x800")
        
        self.default_font = tkfont.nametofont("TkDefaultFont")
        self.default_font.configure(size=self.default_font.cget("size") + 2)
        self.text_font = tkfont.nametofont("TkTextFont")
        self.text_font.configure(size=self.text_font.cget("size") + 2)
        
        self.file_data = {}  # Używamy słownika zamiast listy
        self.current_index = 0
        self.compare_by_name = tk.BooleanVar(value=True)
        self.compare_by_size = tk.BooleanVar(value=False)
        self.deleted_files = set() # Zbiór usuniętych plików (ścieżki)
        self.current_directory = ""
        
        for widget in self.root.winfo_children(): # Usuwamy wszystkie widgety z głównego okna
            widget.destroy()
        setup_controls_frame(self)
        setup_canvas_frame(self)
        
        # Bind the Escape key to close the application
        self.root.bind('<Escape>', lambda event: self.root.quit())
        self.root.bind('<Return>', lambda event: scan_directory(self))


if __name__ == "__main__":
    root = tk.Tk()
    app = FileComparator(root)
    root.mainloop()