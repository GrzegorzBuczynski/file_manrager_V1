import os
import csv
import cv2
import datetime
import tkinter as tk
from tkinter import filedialog, ttk, font as tkfont
from PIL import Image, ImageTk
from collections import defaultdict

def create_action_buttons(frame, path):
    buttons_frame = tk.Frame(frame)
    buttons_frame.pack(fill=tk.X, pady=5)

    open_button = tk.Button(buttons_frame, text="Open Location",
                            command=lambda p=path: os.startfile(os.path.dirname(p)))
    open_button.pack(side=tk.LEFT, padx=2)

    run_button = tk.Button(buttons_frame, text="Run",
                           command=lambda p=path: os.startfile(p))
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
    folder = filedialog.askdirectory()
    if not folder:
        return
    app.current_directory = folder
    process_directory(app, folder)
    setup_control_frame(app)  # Add this line to redraw the control frame

def refresh_app(app):
    if not app.current_directory:
        app.info_label.config(text="No directory selected yet. Please scan a directory first.", fg="red")
        return
    process_directory(app, app.current_directory)
    setup_control_frame(app)
    show_comparison(app)

def process_directory(app, folder):
    file_info = []
    for root, _, files in os.walk(folder):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                size = os.path.getsize(file_path)
                file_info.append((file, size, file_path))
            except OSError:
                print(f'Błąd dostępu do pliku: {file_path}')
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
        process_directory(app, folder)
        return
    
    app.file_data = filtered_files
    app.current_index = 0
    refresh_list(app)

def refresh_list(app):
    current_selection = app.file_listbox.curselection()
    if current_selection:
        current_selection = current_selection[0]
    else:
        current_selection = 0

    app.file_listbox.delete(0, tk.END)
    if not app.file_data:
        app.info_label.config(text="No duplicate files found with current criteria.")
        for widget in app.canvas_frame.winfo_children():
            widget.destroy()
        return
    for i, name in enumerate(app.file_data.keys()):
        app.file_listbox.insert(tk.END, name)
        files_for_name = [path for _, path in app.file_data[name]]
        has_deleted = any(path in app.deleted_files for path in files_for_name)
        if has_deleted:
            app.file_listbox.itemconfig(i, fg="red")
    
    if app.file_listbox.size() > 0:
        if current_selection >= app.file_listbox.size():
            current_selection = app.file_listbox.size() - 1
        app.file_listbox.selection_set(current_selection)
        app.current_index = current_selection
        show_comparison(app)

def select_file(app, event):
    selection = app.file_listbox.curselection()
    if selection:
        app.current_index = selection[0]
        show_comparison(app)

def show_comparison(app):
    for widget in app.canvas_frame.winfo_children():
        widget.destroy()
    if not app.file_data:  # Sprawdza, czy są dane do porównania
        app.info_label.config(text="No more files to compare.")
        return
    name, files = list(app.file_data.items())[app.current_index]  # Pobiera nazwę i pliki do porównania na podstawie bieżącego indeksu
    num_files = len(files)
    thumbnail_size = max(100, min(400, int(1200 / num_files) - 20))  # Oblicza rozmiar miniaturki na podstawie liczby plików

    create_info_frame(app)  # Tworzy ramkę informacyjną
    create_comparison_title(app, name)  # Tworzy tytuł porównania
    create_paths_frame(app, files, thumbnail_size)  # Tworzy ramkę z podglądami plików
    create_actions_frame(app, files, thumbnail_size, name)  # Tworzy ramkę z akcjami dla plików

def create_info_frame(app):
    info_frame = tk.Frame(app.canvas_frame)  # Tworzy ramkę informacyjną w canvas_frame
    info_frame.pack(fill=tk.X, pady=(0, 10))  # Pakuje ramkę informacyjną z odstępem pionowym 10 pikseli poniżej
    
    app.info_label = tk.Label(info_frame, text="", font=("TkDefaultFont", app.default_font.cget("size")))  # Tworzy etykietę informacyjną
    app.info_label.pack(fill=tk.X)  # Pakuje etykietę, aby wypełniała przestrzeń w poziomie

def create_comparison_title(app, name):
    comparison_title = tk.Frame(app.canvas_frame, height=int(0.2 * app.canvas_frame.winfo_toplevel().winfo_height()))
    comparison_title.pack(fill=tk.X, expand=False)

    title_label = tk.Label(comparison_title, text=f"Comparing: {name}", font=("Arial", 14, "bold"))
    title_label.pack(fill=tk.X, pady=5)

def create_paths_frame(app, files, thumbnail_size):
    paths_frame = tk.Frame(app.canvas_frame)
    paths_frame.pack(fill=tk.BOTH, expand=False)

    for i, (size, path) in enumerate(files):
        path_frame = tk.Frame(paths_frame, width=thumbnail_size, height=(0.3 * thumbnail_size))  # Ustawia stałą szerokość i wysokość na thumbnail_size
        path_frame.pack_propagate(False)  # Ustawia extendable na false
        path_frame.pack(side=tk.LEFT, padx=10, pady=10)
        formatted_size = format_size(size)
        info_label = tk.Label(path_frame, text=f"Found_{i+1}\nSize: {formatted_size}", wraplength=thumbnail_size)
        info_label.pack(fill=tk.X)
        path_label = tk.Label(path_frame, text=f"Path: {path}", wraplength=thumbnail_size, justify=tk.LEFT, anchor="w")  # Ustawia maksymalnie do lewej
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
        os.remove(file_path)  # Usuwa plik z systemu plików
        app.deleted_files.add(file_path)  # Dodaje ścieżkę pliku do zestawu usuniętych plików
        frame.destroy()  # Usuwa ramkę z interfejsu użytkownika
        app.info_label.config(text=f"Deleted: {file_path}", fg="green")  # Aktualizuje etykietę informacyjną, aby wskazać, że plik został usunięty
        
        names = list(app.file_data.keys())  # Pobiera listę nazw plików z danych aplikacji
        if file_name in names:
            idx = names.index(file_name)  # Znajduje indeks nazwy pliku
            app.file_listbox.itemconfig(idx, fg="red")  # Ustawia kolor tekstu na czerwony w liście plików, aby wskazać, że plik został usunięty
        
        # Filtruje pozostałe pliki, aby usunąć usunięty plik z danych aplikacji
        remaining_files = [(size, path) for size, path in app.file_data[file_name] if path != file_path]
        if remaining_files:
            app.file_data[file_name] = remaining_files  # Aktualizuje dane aplikacji, jeśli są jeszcze pozostałe pliki
        else:
            del app.file_data[file_name]  # Usuwa nazwę pliku z danych aplikacji, jeśli nie ma już pozostałych plików
            
        app.root.after(2000, lambda: show_comparison(app))  # Wywołuje show_comparison po 2000 milisekundach
    except Exception as e:
        app.info_label.config(text=f"Failed to delete: {file_path} - {str(e)}", fg="red")  # Aktualizuje etykietę informacyjną, aby wskazać, że usunięcie pliku nie powiodło się

def setup_control_frame(app):
    for widget in app.root.winfo_children():
        widget.destroy()

    app.canvas_frame = tk.Frame(root)  # Tworzy ramkę canvas w głównym oknie
    app.canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)  # Pakuje ramkę canvas po prawej stronie okna

    create_info_frame(app)  # Tworzy ramkę informacyjną
    
    app.control_frame = tk.Frame(app.root)  # Tworzy ramkę kontrolną w głównym oknie
    app.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)  # Pakuje ramkę kontrolną po lewej stronie okna

    app.load_button = tk.Button(app.control_frame, text="Scan Directory", command=lambda: scan_directory(app))  # Tworzy przycisk do skanowania katalogu
    app.load_button.pack(pady=5)  # Pakuje przycisk z odstępem 5 pikseli

    app.compare_name_check = tk.Checkbutton(app.control_frame, text="Compare by Name", variable=app.compare_by_name)  # Tworzy pole wyboru do porównywania po nazwie
    app.compare_name_check.pack(pady=2)  # Pakuje pole wyboru z odstępem 2 pikseli
    app.compare_size_check = tk.Checkbutton(app.control_frame, text="Compare by Size", variable=app.compare_by_size)  # Tworzy pole wyboru do porównywania po rozmiarze
    app.compare_size_check.pack(pady=2)  # Pakuje pole wyboru z odstępem 2 pikseli

    app.refresh_button = tk.Button(app.control_frame, text="Refresh", command=lambda: refresh_app(app))  # Tworzy przycisk do odświeżania
    app.refresh_button.pack(pady=5)  # Pakuje przycisk z odstępem 5 pikseli

    app.file_listbox = tk.Listbox(app.control_frame, height=40, width=30, font=("TkDefaultFont", app.default_font.cget("size")))  # Tworzy listę plików
    app.file_listbox.pack(fill=tk.Y, expand=True)  # Pakuje listę plików, aby wypełniała przestrzeń w pionie
    app.file_listbox.bind("<<ListboxSelect>>", lambda event: select_file(app, event))  # Wiąże zdarzenie wyboru z listy plików z funkcją select_file

class FileComparator:
    def __init__(self, root):
        self.root = root  # Przypisuje główne okno aplikacji do atrybutu root
        self.root.title("File Comparator")  # Ustawia tytuł okna aplikacji
        self.root.geometry("1200x800")  # Ustawia wymiary okna aplikacji
        
        self.default_font = tkfont.nametofont("TkDefaultFont")  # Pobiera domyślną czcionkę Tkinter
        self.default_font.configure(size=self.default_font.cget("size") + 2)  # Zwiększa rozmiar domyślnej czcionki o 2
        self.text_font = tkfont.nametofont("TkTextFont")  # Pobiera czcionkę tekstu Tkinter
        self.text_font.configure(size=self.text_font.cget("size") + 2)  # Zwiększa rozmiar czcionki tekstu o 2
        
        self.file_data = []  # Inicjalizuje listę danych plików jako pustą listę
        self.current_index = 0  # Ustawia bieżący indeks na 0
        self.compare_by_name = tk.BooleanVar(value=True)  # Inicjalizuje zmienną logiczną do porównywania po nazwie
        self.compare_by_size = tk.BooleanVar(value=False)  # Inicjalizuje zmienną logiczną do porównywania po rozmiarze
        self.deleted_files = set()  # Inicjalizuje zestaw usuniętych plików jako pusty zestaw
        self.current_directory = ""  # Inicjalizuje bieżący katalog jako pusty ciąg znaków
        
        setup_control_frame(self)  # Wywołuje funkcję setup_control_frame, aby ustawić ramkę kontrolną




if __name__ == "__main__":
    root = tk.Tk()
    app = FileComparator(root)
    root.mainloop()