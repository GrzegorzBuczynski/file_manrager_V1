import os
import datetime
import csv
from collections import defaultdict

def scan_directory(directory):
    file_info = []
    file_names = defaultdict(list)
    name_variants = defaultdict(list)
    
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                size = os.path.getsize(file_path)
                file_info.append((file, size, file_path))
                file_names[(file, size)].append(file_path)
                name_variants[file].append((size, file_path))
            except OSError:
                print(f'Błąd dostępu do pliku: {file_path}')
    
    return file_info, file_names, name_variants

def find_duplicates(file_names):
    return {key: paths for key, paths in file_names.items() if len(paths) > 1}

def find_name_variants(name_variants):
    return {name: files for name, files in name_variants.items() if len(files) > 1}

def main():
    folder = input("Podaj ścieżkę do folderu do analizy: ")
    if not os.path.exists(folder):
        print("Podana ścieżka nie istnieje.")
        return
    
    file_info, file_names, name_variants = scan_directory(folder)
    
    # Tworzenie nazwy pliku wynikowego
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    result_filename = f"file_manager_result_{timestamp}.csv"
    
    duplicates = find_duplicates(file_names)
    name_conflicts = find_name_variants(name_variants)
    
    sorted_files = []
    for name, size, path in file_info:
        if (name, size) in duplicates:
            status = "DUP"
            color = "#FF0000"  # Czerwony
            sorted_files.append((status, color, size, name, path))
        elif name in name_conflicts:
            status = "VAR"
            color = "#FFFF00"  # Żółty
            sorted_files.append((status, color, size, name, path))
        else:
            status = "OK"
            color = "#FFFFFF"  # Biały
            sorted_files.append((status, color, size, name, path))
    
    # Sortowanie: DUP -> VAR -> OK, każdy według rozmiaru malejąco
    sorted_files.sort(key=lambda x: (x[0] != "DUP", x[0] != "VAR", -x[2]))
    
    with open(result_filename, "w", encoding="utf-8", newline='') as result_file:
        csv_writer = csv.writer(result_file)
        csv_writer.writerow(["Status", "Kolor", "Rozmiar (B)", "Nazwa pliku", "Ścieżka"])
        
        for status, color, size, name, path in sorted_files:
            csv_writer.writerow([status, color, size, name, path])
    
    print(f"Wyniki zapisano w pliku: {result_filename}")
    
if __name__ == "__main__":
    main()
