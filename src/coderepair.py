import os
import tkinter as tk
from tkinter import filedialog

def remove_duplicate_translations(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    prev_line = None
    skip_line = False

    for line in lines:
        stripped_line = line.strip()
        
        # Eğer satır "old" ile başlıyorsa, yeni çevirileri takip et
        if stripped_line.startswith('old'):
            skip_line = False
            new_lines.append(line)  # "old" satırını ekle
            continue
        elif stripped_line.startswith('new'):
            if skip_line:  # Eğer daha önce aynı "new" satırı eklenmişse, bu satırı atla
                continue
            new_lines.append(line)
            skip_line = True
            continue

        # Çift yazılan metinleri teke indir
        if stripped_line and stripped_line == prev_line:
            continue
        
        new_lines.append(line)
        prev_line = stripped_line  # Bir önceki satırı kaydet

    # Dosyayı temizlenmiş versiyonuyla güncelle
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

def remove_escaped_quotes(file_path):
    """
    Dosya içindeki tüm \" ifadelerini kaldırır.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Ters bölü ve çift tırnak karakterlerini kaldır
    content = content.replace('\\"', '')

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

def process_rpy_files():
    root = tk.Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory(title="Klasör Seç")

    if not folder_selected:
        print("Klasör seçilmedi. Çıkılıyor...")
        return

    for root_dir, _, files in os.walk(folder_selected):
        for file in files:
            if file.endswith(".rpy"):
                file_path = os.path.join(root_dir, file)
                print(f"İşleniyor: {file_path}")
                remove_duplicate_translations(file_path)
                remove_escaped_quotes(file_path)

    print("Tüm .rpy dosyalarındaki çift çeviriler temizlendi ve \" ifadesi kaldırıldı.")

if __name__ == "__main__":
    process_rpy_files()
