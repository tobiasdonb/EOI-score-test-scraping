import time
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
            bot._log(f"\n--- PROCESSING: {month} | SCORE: {score} ---")

            
            # A. GANTI BULAN
            if current_active_month is None:
                bot.switch_to_main_page()
                auto_month = bot.get_current_selection_text(
                    config.XPATH_CURRENT_SELECTION_MONTH
                )
                bot.click_element(
                    config.XPATH_CURRENT_SELECTION_MONTH, "Buka Filter Bulan"
                )
                time.sleep(1.5)

                # 1. Simpan status keberhasilan memilih bulan
                select_success = bot.search_and_select_item(month, f"Select {month}")

                # 2. Hanya hapus default jika bulan target berhasil dicentang
                if select_success and auto_month and auto_month != month:
                    bot.search_and_unselect_item(
                        auto_month, f"Uncheck default {auto_month}"
                    )
                elif not select_success:
                    bot._log(
                        f"⚠️ Gagal memilih {month} di awal! (Beresiko filter kosong)"
                    )

                bot.click_element(config.XPATH_ACTION_CONFIRM, "Confirm Month Init")
                time.sleep(2)

            elif month != current_active_month:
                bot.switch_to_main_page()

                # Beri jeda ekstra jika bot baru saja ngebut melakukan skip
                time.sleep(2)
                bot.click_element(config.XPATH_CURRENT_SELECTION_MONTH, "Ganti Bulan")
                time.sleep(2.5)

                try:
                    # 1. WAJIB: Pastikan bulan baru berhasil dicentang DULU
                    select_success = bot.search_and_select_item(month, f"Pilih {month}")

                    if select_success:
                        # 2. SAPU BERSIH: Hapus SEMUA bulan yang tercentang (kecuali bulan baru)
                        bot._log("🧹 Sapu bersih semua bulan yang nyangkut...")
                        bot.uncheck_selected_rows(exclude=month)
                    else:
                        # Jika gagal pilih bulan baru, JANGAN hapus apapun agar tidak kosong!
                        raise Exception(
                            f"Gagal ketik/centang {month}, membatalkan uncheck..."
                        )

                except Exception as search_err:
                    bot._log(
                        f"⚠️ Dropdown lag/nyangkut! Melakukan Retry... ({search_err})"
                    )
                    try:
                        bot.click_element(config.XPATH_ACTION_CONFIRM, "Tutup Darurat")
                    except:
                        pass

                    # Beri waktu Qlik bernapas dari freeze
                    time.sleep(3)
                    bot.click_element(
                        config.XPATH_CURRENT_SELECTION_MONTH, "Buka Ulang Bulan"
                    )
                    time.sleep(2)

                    # Percobaan kedua
                    retry_success = bot.search_and_select_item(month, f"Pilih {month}")
                    if retry_success:
                        bot._log("🧹 Sapu bersih semua bulan yang nyangkut (Retry)...")
                        bot.uncheck_selected_rows(exclude=month)

                bot.click_element(config.XPATH_ACTION_CONFIRM, "Confirm Transisi Bulan")
                time.sleep(3.5)
            # elif month != current_active_month:
            #     # --- PERGANTIAN BULAN BERIKUTNYA ---
            #     bot.switch_to_main_page()
            #     time.sleep(1)
            #     bot.click_element(config.XPATH_CURRENT_SELECTION_MONTH, "Ganti Bulan")
            #     time.sleep(1.5)  # Pastikan dropdown terbuka sempurna

            #     try:
            #         bot.search_and_select_item(month, f"Pilih {month}")
            #         bot.search_and_unselect_item(current_active_month, f"Hapus {current_active_month}")
                    
            #         # 🛡️ LAPIS PENGAMAN EXTRA: Jika bot kelelahan dan ada bulan siluman tersisa
            #         bot.uncheck_selected_rows(exclude=month)
                    
            #     except Exception as search_err:
            #         bot._log(f"⚠️ Dropdown lag/nyangkut! Melakukan Retry... ({search_err})")
            #         try:
            #             bot.click_element(config.XPATH_ACTION_CONFIRM, "Tutup Darurat")
            #         except:
            #             pass
            #         time.sleep(2)
            #         bot.click_element(
            #             config.XPATH_CURRENT_SELECTION_MONTH, "Buka Ulang Bulan"
            #         )
            #         time.sleep(2)
            #         bot.search_and_select_item(month, f"Pilih {month}")
            #         bot.search_and_unselect_item(
            #             current_active_month, f"Hapus {current_active_month}"
            #         )

            #     # 3. Confirm SEKALI saja untuk kedua aksi di atas!
            #     bot.click_element(config.XPATH_ACTION_CONFIRM, "Confirm Transisi Bulan")
            #     time.sleep(2)  # Jeda agar tabel final selesai dimuat

            # B. GANTI SCORE
            # (Kode B Anda tetap sama, biarkan tidak berubah)

            # C. ITERASI STATE & DOWNLOAD (STRUKTUR BARU)
            # 2. HAPUS first_state_flag karena sudah tidak diperlukan!
            for state in config.STATES:
                safe_name = f"EOI_{state}_SCORE_{score}_{month.replace('/', '_')}"
                
                if bot.check_file_exists(safe_name, month_folder=month):
                    bot._log(f"[SKIP] {state} skip - File exist.")
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
                # 3. Transisi state yang alami dan aman
                # if state != active_state:
                    # bot.switch_to_main_page()
                    
                    # # Pengecekan krusial: Apakah pill filter State ada?
                    # pill_elements = bot.driver.find_elements(By.XPATH, config.XPATH_CURRENT_SELECTION_STATE)
                    # if not pill_elements:
                    #     bot._log(f"[RESCUE] Pill State hilang! Memaksa inisialisasi '{state}' via Smart Search...")
                    #     bot.use_smart_search(state)
                    #     time.sleep(2)
                        
                    #     # Verifikasi apakah rescue berhasil
                    #     if not bot.driver.find_elements(By.XPATH, config.XPATH_CURRENT_SELECTION_STATE):
                    #         bot._log(f"[SKIP] State '{state}' benar-benar kosong, Smart Search gagal.")
                    #         continue # Lewati state ini
                            
                    #     active_state = state
                    #     # Lanjut langsung ke download karena Smart Search sudah menanam state ini
                    # else:
                    #     # Alur normal via Dropdown Pill
                    #     bot.click_element(config.XPATH_CURRENT_SELECTION_STATE, "Switch State")
                    #     time.sleep(2.0)
                        
                    #     # Coba cari dan check state yang baru DULU
                    #     select_success = bot.search_and_select_item(state, f"Check {state}")
                        
                    #     if select_success:
                    #         # METODE SAPU BERSIH (CLEAN SWEEP)
                    #         for other_state in config.STATES:
                    #             if other_state != state:
                    #                 bot.search_and_unselect_item(other_state, f"Uncheck {other_state}")
                            
                    #         bot.click_element(config.XPATH_ACTION_CONFIRM, "Confirm Switch State")
                    #         time.sleep(1.2)
                            
                    #         active_state = state
                    #     else:
                    #         bot._log(f"[SKIP] State '{state}' tidak tersedia di dropdown, melewati...")
                    #         bot.click_element(config.XPATH_ACTION_CONFIRM, "Tutup Menu State")
                    #         time.sleep(1)
                    #         continue # Langsung lanjut ke state berikutnya tanpa mendownload

                # Download
                bot.switch_to_dashboard_iframe()
                bot.export_table_data()
                bot.wait_and_rename_file(safe_name, state_name=state, english_score=score, month_folder=month)
                bot.close_export_dialog()
                time.sleep(0.5)

            current_active_month = month
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
            # Jika ingin load barengan, biarkan di-comment (pakai #)
            # Jika internet lag, hapus tanda # di bawah ini dan beri waktu 10-15 detik

            # if i < num_workers - 1:
            #     stagger_delay = 10
            #     print(f"  [WAIT] Menunggu {stagger_delay} detik...\n")
            #     time.sleep(stagger_delay)

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