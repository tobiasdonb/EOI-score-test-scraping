import time
import threading
from concurrent.futures import ThreadPoolExecutor
from scraper import SkillSelectScraper
import config
from selenium.webdriver.common.by import By

# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def generate_month_range(start_str, end_str):
    """Generate list bulan dari end ke start (terbaru ke terlama)."""
    sm, sy = int(start_str.split('/')[0]), int(start_str.split('/')[1])
    em, ey = int(end_str.split('/')[0]), int(end_str.split('/')[1])
    months = []
    y, m = ey, em
    while (y, m) >= (sy, sm):
        months.append(f"{m:02d}/{y}")
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    return months

def setup_bot_environment(bot,initial_score):
    """Navigasi awal, bypass loader, set parameter YES/NO, dan filter global."""
    bot._log("[SETUP] Menyiapkan lingkungan browser...")
    bot.driver.get(config.URL)

    # 1. JEDA EKSTRA UNTUK QLIK SENSE (Sangat Penting!)
    bot._log("Menunggu Qlik Sense merender dashboard secara penuh...")
    time.sleep(14)  # Tambahkan jeda di sini

    try:
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By

        wait_for_loader = WebDriverWait(bot.driver, 30)
        wait_for_loader.until(
            EC.invisibility_of_element_located((By.ID, "page-loader"))
        )
    except:
        bot._log("[WARN] Loader lambat hilang, tetap lanjut...")
        pass
    time.sleep(3)  # Jeda transisi setelah loader hilang

    # 2. Navigasi ke parameter
    bot.switch_to_main_page()
    bot.click_element(config.XPATH_BTN_NEXT, "Next (Halaman Parameter)")
    time.sleep(5)  # Jeda ekstra setelah klik Next agar halaman parameter stabil

    # 3. Set YES/NO (Occupation & Points)
    bot.switch_to_dashboard_iframe()
    bot.click_element(config.XPATH_BTN_YES_OCCUPATION, "Occupation = YES")
    try:
        if getattr(config, 'INCLUDE_POINTS', True):
            bot.click_element(config.XPATH_BTN_YES_POINTS, "Points = YES")
        else:
            bot.click_element(config.XPATH_BTN_NO_POINTS, "Points = NO")
    except:
        bot._log("[WARN] Tombol 'Points' tidak ditemukan/sudah default.")

    # 4. Filter Global (Visa & Status)
    bot._log("--- Menyeting Filter Global (Visa & Status) ---")

    # Visa Filter
    bot.click_element(config.XPATH_DROPDOWN_SELECT, "Open Filter Pane")
    time.sleep(1)
    bot.click_element(config.XPATH_HEADER_VISA_TYPE, "Menu Visa")
    time.sleep(1)
    for xpath in [
        config.XPATH_VISA_189,
        config.XPATH_VISA_190,
        config.XPATH_VISA_491_SR,
        config.XPATH_VISA_491_ST,
    ]:
        bot.click_element(xpath, "Visa Type")
    bot.click_element(config.XPATH_ACTION_CONFIRM, "Confirm Visa")
    time.sleep(2)

    # Status Filter
    bot.click_element(config.XPATH_DROPDOWN_SELECT, "Open Filter Pane")
    time.sleep(1)
    bot.click_element(config.XPATH_HEADER_EOI_STATUS, "Menu Status")
    time.sleep(1)
    for xpath in [
        config.XPATH_EOI_SUBMITTED,
        config.XPATH_EOI_INVITED,
        config.XPATH_EOI_LODGED,
        config.XPATH_EOI_CLOSED,
        config.XPATH_EOI_HOLD,
    ]:
        bot.click_element(xpath, "EOI Status")
    bot.click_element(config.XPATH_ACTION_CONFIRM, "Confirm Status")
    time.sleep(2)

    # 5. Smart Search Inisialisasi
    bot.switch_to_main_page()
    bot.use_smart_search(config.STATES[0])
    bot.use_smart_search(initial_score)

    # 6. Ke Tabel Final
    bot.click_element(config.XPATH_BTN_NEXT, "Tombol Next Ke Tabel")
    bot._log("Menunggu render tabel final...")
    time.sleep(8)  # Tabel final Qlik biasanya sangat berat, beri waktu lebih lama


# ==========================================================
# WORKER CORE LOGIC
# ==================
def worker_routine(worker_id, tasks):
    """Routine utama yang dijalankan oleh setiap worker thread."""
    bot = SkillSelectScraper(worker_id=worker_id)
    
    try:
        # 1. Ambil Score khusus untuk Worker ini dari tugas pertamanya
        assigned_score = tasks[0][1]

        # 2. Kirim assigned_score ke bot saat setup lingkungan
        setup_bot_environment(bot, assigned_score)

        current_active_month = None
        active_state = config.STATES[0]

        for month, score in tasks:
            # --- PRE-CHECK: Cek kelengkapan data state untuk bulan ini ---
            missing_states = []
            for check_state in config.STATES:
                safe_name = f"EOI_{check_state}_SCORE_{score}_{month.replace('/', '_')}"
                if not bot.check_file_exists(safe_name, english_score=score, month_folder=month):
                    missing_states.append(check_state)
            
            if not missing_states:
                bot._log(f"⏩ Data Bulan {month} (Score {score}) sudah LENGKAP 100%. Melewati aksi UI...")
                continue # Lanjut ke iterasi `for month` berikutnya
            
            # --- A. GANTI BULAN DI UI ---
            if current_active_month is None:
                bot.switch_to_main_page()
                time.sleep(1)

                auto_month = bot.get_current_selection_text(
                    config.XPATH_CURRENT_SELECTION_MONTH
                )

                if not auto_month:
                    bot._log(f"Pill As At Month tidak ditemukan, menanam bulan {month} dengan Smart Search...")
                    bot.use_smart_search(month)
                    time.sleep(2)
                elif auto_month == month:
                    bot._log(f"✅ Bulan {month} sudah terpilih sebagai default.")
                else:
                    bot._log(f"🧹 Mengganti pilihan bulan default dari ({auto_month}) ke {month}...")
                    bot.click_element(
                        config.XPATH_CURRENT_SELECTION_MONTH, "Buka Filter Bulan"
                    )
                    time.sleep(1.5)

                    # Pilih bulan target
                    bot.search_and_select_item(month, f"Pilih {month}")
                    time.sleep(1)
                    
                    # Hapus default lama
                    bot.search_and_unselect_item(auto_month, f"Uncheck {auto_month}")
                    time.sleep(1)
                    
                    bot.click_element(config.XPATH_ACTION_CONFIRM, "Confirm Month Init")
                    time.sleep(2)

            elif month != current_active_month:
                
                bot.switch_to_main_page()
                time.sleep(1.5)

                bot._log(f"🔄 Memulai proses penggantian: {current_active_month} -> {month}")
                
                # 1. Buka Filter (Pilih dulu yang baru agar pill tidak hilang)
                bot.click_element(config.XPATH_CURRENT_SELECTION_MONTH, "Buka Filter Bulan")
                time.sleep(2)
                
                # 2. Cari dan seleksi bulan baru
                select_success = bot.search_and_select_item(month, f"Pilih {month}")
                
                if not select_success:
                    bot._log(f"⚠️ Gagal menemukan {month}, mencoba menyegarkan pencarian...")
                    # Fallback jika pencarian macet
                    try:
                        bot.driver.execute_script("arguments[0].value = '';", bot.driver.find_element(By.XPATH, config.XPATH_SEARCH_LISTBOX))
                    except: pass
                    bot.search_and_select_item(month, f"Retry Pilih {month}")

                time.sleep(1)
                
                # 3. Unselect bulan lama
                bot.search_and_unselect_item(current_active_month, f"Uncheck {current_active_month}")
                time.sleep(1)

                # 4. Approve / Confirm perubahan
                bot.click_element(config.XPATH_ACTION_CONFIRM, "Confirm Perubahan Bulan")
                bot._log(f"✅ Sekarang aktif pada bulan: {month}")
                time.sleep(3)
                
            current_active_month = month
            
            # --- B. PRIORITASKAN MISSING STATES ---
            for state in missing_states:
                safe_name = f"EOI_{state}_SCORE_{score}_{month.replace('/', '_')}"
                
                # Cek file exist sekali lagi sebagai lapis pengaman
                if bot.check_file_exists(safe_name, english_score=score, month_folder=month):
                    continue
                
                if state != active_state:
                    bot.switch_to_main_page()
                    pill_elements = bot.driver.find_elements(
                        By.XPATH, config.XPATH_CURRENT_SELECTION_STATE
                    )
                    if not pill_elements:
                        bot._log(
                            f"[RESCUE] Pill State hilang! Memaksa inisialisasi '{state}' via Smart Search..."
                        )
                        bot.use_smart_search(state)
                        time.sleep(2)

                        if not bot.driver.find_elements(
                            By.XPATH, config.XPATH_CURRENT_SELECTION_STATE
                        ):
                            bot._log(
                                f"[SKIP] State '{state}' benar-benar kosong, Smart Search gagal."
                            )
                            continue

                        active_state = state
                    else:
                        bot.click_element(
                            config.XPATH_CURRENT_SELECTION_STATE, "Switch State"
                        )
                        time.sleep(2.0)

                        select_success = bot.search_and_select_item(
                            state, f"Check {state}"
                        )
                        
                        if select_success:
                            # METODE SAPU BERSIH (CLEAN SWEEP)
                            for other_state in config.STATES:
                                if other_state != state:
                                    search_box_elements = bot.driver.find_elements(
                                        By.XPATH, config.XPATH_SEARCH_LISTBOX
                                    )
                                    if not search_box_elements:
                                        bot._log(
                                            "⚠️ Menu State tertutup otomatis! Membuka kembali..."
                                        )
                                        try:
                                            bot.click_element(
                                                config.XPATH_CURRENT_SELECTION_STATE,
                                                "Re-open State Menu",
                                            )
                                        except:
                                            pass
                                        time.sleep(1.5)
                                    bot.search_and_unselect_item(
                                        other_state, f"Uncheck {other_state}"
                                    )
                                    
                            bot.click_element(
                                config.XPATH_ACTION_CONFIRM, "Confirm Switch State"
                            )
                            time.sleep(1.2)
                            active_state = state
                        else:
                            bot._log(
                                f"[SKIP] State '{state}' tidak tersedia di dropdown, melewati..."
                            )
                            bot.click_element(config.XPATH_ACTION_CONFIRM, "Tutup Menu State")
                            time.sleep(1)
                            continue

                # Download
                bot.switch_to_dashboard_iframe()
                bot.export_table_data()
                bot.wait_and_rename_file(safe_name, state_name=state, english_score=score, month_folder=month)
                bot.close_export_dialog()
                time.sleep(0.5)
        
            # current_active_score diset per iterasi tasks utama
            current_active_score = score

        bot._log("✅ Pekerjaan Selesai.")

    except Exception as e:
        bot._log(f"❌ Terjadi kesalahan fatal: {e}")
        import traceback
        traceback.print_exc()
    finally:
        bot.close_browser()

# ==========================================================
# MAIN ENTRY POINT
# ==========================================================
def main():
    print("==================================================")
    print("   SKILLSELECT MULTI-THREADED SCRAPER STARTING    ")
    print("   STRATEGY: ONE WORKER PER ENGLISH SCORE         ")
    print("==================================================")

    # 1. Persiapkan daftar bulan
    months = generate_month_range(config.START_MONTH, config.END_MONTH)

    # 2. Set jumlah worker agar otomatis menyesuaikan dengan jumlah Score di config
    num_workers = len(config.SCORES)

    print(f"Bulan Target : {config.START_MONTH} s/d {config.END_MONTH}")
    print(f"Total Worker : {num_workers} threads (Masing-masing 1 English Score)\n")

    # 3. Jalankan ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = []

        # Looping berdasarkan Index (i) dan Score
        for i, score in enumerate(config.SCORES):
            # KUNCI UTAMA: Buat list task KHUSUS untuk satu score saja
            # Worker ini akan mengerjakan semua bulan, tapi hanya untuk 'score' ini
            worker_tasks = [(month, score) for month in months]

            print(f"[START] Worker {i} ditugaskan khusus untuk English Score: {score}")

            # Kirim tugas ke worker
            futures.append(executor.submit(worker_routine, i, worker_tasks))

            # (Opsional) Pengaturan Start Barengan / Staggered
            # Jika internet lag dan beban menjadi sangat berat (karena fitur Points aktif), berikan delay lebih lama!
            if i < num_workers - 1:
                stagger_delay = 10
                print(f"  [WAIT] Menunggu {stagger_delay} detik agar beban awal web dan CPU stabil sebelum membuka browser berikutnya...\n")
                time.sleep(stagger_delay)

        # Tunggu sampai semua worker selesai
        for future in futures:
            try:
                future.result()
            except Exception as e:
                print(f"Worker Error: {e}")

    print("\n==================================================")
    print("   SELURUH DATA BERHASIL DIKUMPULKAN! FINISHED.   ")
    print("==================================================")


if __name__ == "__main__":
    main()
if __name__ == "__main__":
    main()