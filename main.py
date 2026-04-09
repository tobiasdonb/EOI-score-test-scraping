import time
from concurrent.futures import ThreadPoolExecutor
from scraper import SkillSelectScraper
import config

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

def setup_bot_environment(bot):
    """Navigasi awal, bypass loader, set parameter YES/NO, dan filter global."""
    bot._log("🚀 Menyiapkan lingkungan browser...")
    bot.driver.get(config.URL)
    
    try:
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By
        wait_for_loader = WebDriverWait(bot.driver, 60)
        wait_for_loader.until(EC.invisibility_of_element_located((By.ID, "page-loader")))
    except: pass
    time.sleep(1)

    # 1. Navigasi ke parameter
    bot.switch_to_main_page()
    bot.click_element(config.XPATH_BTN_NEXT, "Next (Halaman Parameter)")
    time.sleep(2)

    # 2. Set YES/NO (Occupation & Points)
    bot.switch_to_dashboard_iframe()
    bot.click_element(config.XPATH_BTN_YES_OCCUPATION, "Occupation = YES")
    try:
        bot.click_element(config.XPATH_BTN_NO_POINTS, "Points = NO")
    except:
        bot._log("⚠️ Tombol 'Points' tidak ditemukan/sudah default.")

    # 3. Filter Global (Visa & Status)
    bot._log("--- Menyeting Filter Global (Visa & Status) ---")
    
    # Visa Filter
    bot.click_element(config.XPATH_DROPDOWN_SELECT, "Open Filter Pane")
    time.sleep(0.5)
    bot.click_element(config.XPATH_HEADER_VISA_TYPE, "Menu Visa")
    time.sleep(0.5)
    for xpath in [config.XPATH_VISA_189, config.XPATH_VISA_190, config.XPATH_VISA_491_SR, config.XPATH_VISA_491_ST]:
        bot.click_element(xpath, "Visa Type")
    bot.click_element(config.XPATH_ACTION_CONFIRM, "Confirm Visa")
    time.sleep(1)

    # Status Filter
    bot.click_element(config.XPATH_DROPDOWN_SELECT, "Open Filter Pane")
    time.sleep(0.5)
    bot.click_element(config.XPATH_HEADER_EOI_STATUS, "Menu Status")
    time.sleep(0.5)
    for xpath in [config.XPATH_EOI_SUBMITTED, config.XPATH_EOI_INVITED, config.XPATH_EOI_LODGED, config.XPATH_EOI_CLOSED, config.XPATH_EOI_HOLD]:
        bot.click_element(xpath, "EOI Status")
    bot.click_element(config.XPATH_ACTION_CONFIRM, "Confirm Status")
    time.sleep(1)

    # 4. Smart Search Inisialisasi
    bot.switch_to_main_page()
    bot.use_smart_search(config.STATES[0]) 
    bot.use_smart_search(config.SCORES[0]) 

    # 5. Ke Tabel Final
    bot.click_element(config.XPATH_BTN_NEXT, "Tombol Next Ke Tabel")
    bot._log("Menunggu render tabel final...")
    time.sleep(5)

# ==========================================================
# WORKER CORE LOGIC
# ==========================================================

def worker_routine(worker_id, tasks):
    """Routine utama yang dijalankan oleh setiap worker thread."""
    bot = SkillSelectScraper(worker_id=worker_id)
    
    try:
        setup_bot_environment(bot)
        
        current_active_month = None
        current_active_score = config.SCORES[0] # Default dari setup_bot_environment

        for month, score in tasks:
            bot._log(f"\n--- PROCESSING: {month} | SCORE: {score} ---")

            # A. GANTI BULAN
            if current_active_month is None:
                # First time initialization for this worker
                bot.switch_to_main_page()
                auto_month = bot.get_current_selection_text(config.XPATH_CURRENT_SELECTION_MONTH)
                
                bot.click_element(config.XPATH_CURRENT_SELECTION_MONTH, "Buka Filter Bulan")
                time.sleep(1.5)
                bot.search_and_select_item(month, f"Select {month}")
                bot.click_element(config.XPATH_ACTION_CONFIRM, "Confirm Month")
                time.sleep(1.5)

                if auto_month and auto_month != month:
                    bot.switch_to_main_page()
                    bot.click_element(config.XPATH_CURRENT_SELECTION_MONTH, "Uncheck Auto Month")
                    time.sleep(1)
                    bot.search_and_unselect_item(auto_month, f"Uncheck {auto_month}")
                    bot.click_element(config.XPATH_ACTION_CONFIRM, "Confirm Uncheck")
                    time.sleep(1.5)
            
            elif month != current_active_month:
                bot.switch_to_main_page()
                bot.click_element(config.XPATH_CURRENT_SELECTION_MONTH, "Ganti Bulan")
                time.sleep(1.2)
                bot.search_and_select_item(month, f"Pilih {month}")
                bot.click_element(config.XPATH_ACTION_CONFIRM, "Confirm New Month")
                time.sleep(1.2)
                
                bot.switch_to_main_page()
                bot.click_element(config.XPATH_CURRENT_SELECTION_MONTH, "Uncheck Bulan Lama")
                time.sleep(1.2)
                bot.search_and_unselect_item(current_active_month, f"Hapus {current_active_month}")
                bot.click_element(config.XPATH_ACTION_CONFIRM, "Confirm Remove Old Month")
                time.sleep(1.5)

            # B. GANTI SCORE
            if score != current_active_score or current_active_month is None:
                bot.switch_to_main_page()
                bot.click_element(config.XPATH_CURRENT_SELECTION_ENGLISH, "Ganti Score")
                time.sleep(1)
                bot.search_and_select_item(score, f"Set Score {score}")
                bot.uncheck_selected_rows(exclude=score)
                bot.click_element(config.XPATH_ACTION_CONFIRM, "Confirm Score")
                time.sleep(1.5)
            
            # C. ITERASI STATE & DOWNLOAD
            first_state_flag = True
            active_state = config.STATES[0]

            for state in config.STATES:
                safe_name = f"EOI_{state}_SCORE_{score}_{month.replace('/', '_')}"
                
                if bot.check_file_exists(safe_name, english_score=score):
                    bot._log(f"⏭️ {state} skip - File exist.")
                    continue

                if first_state_flag:
                    # Pastikan state pertama benar-benar ter-checklist sendirian
                    bot.switch_to_main_page()
                    bot.click_element(config.XPATH_CURRENT_SELECTION_STATE, "Init State Loop")
                    time.sleep(1)
                    bot.search_and_select_item(active_state, f"Select {active_state}")
                    bot.uncheck_selected_rows(exclude=active_state)
                    bot.click_element(config.XPATH_ACTION_CONFIRM, "Confirm State Init")
                    time.sleep(1.5)
                    first_state_flag = False

                if state != active_state:
                    bot.switch_to_main_page()
                    bot.click_element(config.XPATH_CURRENT_SELECTION_STATE, "Switch State")
                    time.sleep(0.8)
                    bot.click_element(config.XPATH_DROPDOWN_ROW.format(state), f"Check {state}")
                    bot.click_element(config.XPATH_DROPDOWN_ROW.format(active_state), f"Uncheck {active_state}")
                    time.sleep(0.8)
                    bot.click_element(config.XPATH_ACTION_CONFIRM, "Confirm Switch State")
                    time.sleep(1.2)
                    active_state = state

                # Download
                bot.switch_to_dashboard_iframe()
                bot.export_table_data()
                bot.wait_and_rename_file(safe_name, state_name=state, english_score=score)
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
    
    # 1. Persiapkan daftar tugas berdasarkan Score
    months = generate_month_range(config.START_MONTH, config.END_MONTH)
    
    # Membagi tasks berdasarkan Score
    score_tasks = {}
    for score in config.SCORES:
        score_tasks[score] = [(m, score) for m in months]
            
    num_workers = min(config.MAX_WORKERS, len(config.SCORES))
    
    print(f"Bulan Target : {config.START_MONTH} s/d {config.END_MONTH}")
    print(f"Total Task   : {len(months) * len(config.SCORES)} kombinasi")
    print(f"Worker Aktif : {num_workers} threads (Capped to Score count)\n")
    
    # 2. Distribusikan tasks ke worker (setiap worker dapat 1 atau lebih score)
    worker_chunks = [[] for _ in range(num_workers)]
    for idx, score in enumerate(config.SCORES):
        worker_chunks[idx % num_workers].extend(score_tasks[score])
        
    # 3. Jalankan ThreadPoolExecutor dengan Staggered Start
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = []
        for i in range(num_workers):
            if worker_chunks[i]:
                # Ambil score pertama di chunk untuk deskripsi log
                score_desc = worker_chunks[i][0][1]
                print(f"Worker {i} mulai memproses Score: {score_desc} dan lainnya...")
                
                futures.append(executor.submit(worker_routine, i, worker_chunks[i]))
                
                # STAGGERED START: Tunggu sebentar sebelum membuka browser berikutnya
                if i < num_workers - 1:
                    stagger_delay = 10 
                    print(f"⏳ Menunggu {stagger_delay} detik sebelum memulai worker berikutnya...\n")
                    time.sleep(stagger_delay)
        
        # Tunggu sampai semua selesai
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