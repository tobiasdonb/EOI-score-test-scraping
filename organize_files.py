import os
import glob
import shutil
import re

dataset_dir = "DATASET"
if not os.path.exists(dataset_dir):
    print("Folder DATASET tidak ditemukan.")
    exit()

# Ambil semua file CSV di dalam DATASET dan subfoldernya
csv_files = glob.glob(os.path.join(dataset_dir, "**", "*.csv"), recursive=True)
moved_count = 0

print(f"Ditemukan {len(csv_files)} file CSV. Memulai pengorganisasian otomatis...\n")

for file_path in csv_files:
    filename = os.path.basename(file_path)
    
    # Cek pola file: EOI_ACT_SCORE_10_03_2026_1234567.csv
    # Menangkap Score (grup 1), Bulan/MM (grup 2), dan Tahun/YYYY (grup 3)
    match = re.search(r'_SCORE_(\d+)_(\d{2})_(\d{4})_', filename)
    if match:
        score = match.group(1)
        month = match.group(2)
        year = match.group(3)
        
        # Susun hierarki folder secara dinamis: DATASET / 2026 / 01_2026 / Score_10
        safe_month_folder = f"{month}_{year}"
        target_dir = os.path.join(dataset_dir, year, safe_month_folder, f"Score_{score}")
        
        # Cek apakah file sudah di posisi folder yang benar
        # (menggunakan os.path.normpath agar cross-platform support di Windows/Mac akurat)
        if os.path.normpath(os.path.dirname(file_path)) == os.path.normpath(target_dir):
            continue
            
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            
        target_path = os.path.join(target_dir, filename)
        
        try:
            shutil.move(file_path, target_path)
            print(f"✅ Moved: {filename} \n   -> {target_dir}")
            moved_count += 1
        except Exception as e:
            print(f"⚠️ Error memindah file {filename}: {e}")

print(f"\nSelesai! Berhasil merapikan {moved_count} file ke format (Tahun/Bulan/Score).")
