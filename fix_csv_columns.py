import os
import glob
import pandas as pd

dataset_dir = "DATASET"
if not os.path.exists(dataset_dir):
    print(f"Folder {dataset_dir} tidak ditemukan.")
    exit()

# Mengambil semua file CSV di dalam folder DATASET dan subfoldernya
csv_files = glob.glob(os.path.join(dataset_dir, "**", "*.csv"), recursive=True)
fixed_count = 0

print(f"Memeriksa {len(csv_files)} file CSV...\n")

for file_path in csv_files:
    try:
        # Membaca sebagai object/string supaya tidak ada error DtypeWarning pada Pandas
        df = pd.read_csv(file_path, dtype=str)
        needs_save = False
        
        for wrong_col in ['State', 'Nominating State']:
            if wrong_col in df.columns:
                if 'Nominated State' in df.columns:
                    # Jika keduanya terbaca ganda (karena sudah sempat tersuntik), 
                    # maka kita cukup buang (drop) kolom bawaan Qlik yang salah.
                    df.drop(columns=[wrong_col], inplace=True)
                else:
                    # Jika belum ganda, kita ganti nama kolom aslinya
                    df.rename(columns={wrong_col: 'Nominated State'}, inplace=True)
                
                needs_save = True
        
        # Jika file CSV bersinggungan dengan masalah di atas, simpan ulang (timpa)
        if needs_save:
            df.to_csv(file_path, index=False)
            print(f"✅ Diperbaiki: {os.path.basename(file_path)}")
            fixed_count += 1
            
    except Exception as e:
        print(f"⚠️ Error memanipulasi {os.path.basename(file_path)}: {e}")

print(f"\nSelesai! Berhasil merapikan dan memperbaiki kolom pada {fixed_count} file CSV.")
