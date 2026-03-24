import time
from scraper import SkillSelectScraper
import config

def main():
    bot = SkillSelectScraper()
    
    try:
        # 1. BUKA URL DASHBOARD
        print("Membuka URL Dashboard...")
        bot.driver.get(config.URL)
        
        try:
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.common.by import By
            wait_for_loader = WebDriverWait(bot.driver, 60)
            wait_for_loader.until(EC.invisibility_of_element_located((By.ID, "page-loader")))
        except: pass
        time.sleep(1)

        # 2. PINDAH KE HALAMAN PARAMETER
        print("\n--- PINDAH KE HALAMAN PARAMETER ---")
        bot.switch_to_main_page()
        bot.click_element(config.XPATH_BTN_NEXT, "Tombol Next Pertama")
        time.sleep(2)

        # 3. SET OCCUPATION & STATE AWAL
        print("\n--- TAHAP 1: SET OCCUPATION & STATE ---")
        bot.switch_to_dashboard_iframe()
        bot.click_element(config.XPATH_BTN_YES_OCCUPATION, "Occupation = YES")
        bot.click_element(config.XPATH_BTN_YES_STATE, "State = YES")
        bot.click_element(config.XPATH_BTN_NO_POINTS, "Points = NO")
        time.sleep(1)

        # 4. FILTER VISA & STATUS GLOBAL 
        print("\n--- SETTING FILTER GLOBAL (VISA & STATUS) ---")
        bot.click_element(config.XPATH_DROPDOWN_SELECT, "Expand Filter Pane")
        time.sleep(0.5)
        
        bot.click_element(config.XPATH_HEADER_VISA_TYPE, "Buka Menu Visa")
        time.sleep(0.5)
        bot.click_element(config.XPATH_VISA_189, "Visa 189")
        bot.click_element(config.XPATH_VISA_190, "Visa 190")
        bot.click_element(config.XPATH_VISA_491_SR, "Visa 491 SR")
        bot.click_element(config.XPATH_VISA_491_ST, "Visa 491 ST")
        bot.click_element(config.XPATH_ACTION_CONFIRM, "Confirm Visa")
        time.sleep(1)

        bot.click_element(config.XPATH_DROPDOWN_SELECT, "Expand Filter Pane")
        time.sleep(0.5)
        bot.click_element(config.XPATH_HEADER_EOI_STATUS, "Buka Menu Status")
        time.sleep(0.5)
        bot.click_element(config.XPATH_EOI_SUBMITTED, "SUBMITTED")
        bot.click_element(config.XPATH_EOI_INVITED, "INVITED")
        bot.click_element(config.XPATH_EOI_LODGED, "LODGED")
        bot.click_element(config.XPATH_EOI_HOLD, "HOLD")
        bot.click_element(config.XPATH_EOI_CLOSED, "CLOSED")
        bot.click_element(config.XPATH_ACTION_CONFIRM, "Confirm Status")
        time.sleep(1)

        # 5. MAJU KE TABEL UNTUK MENANAM STATE PERTAMA
        print("\n--- MAJU KE TABEL UNTUK MENGUNCI STATE PERTAMA ---")
        bot.switch_to_main_page()
        bot.click_element(config.XPATH_BTN_NEXT, "Tombol Next (Ke Halaman Tabel)")
        time.sleep(4) 

        bot.switch_to_dashboard_iframe()
        bot.click_element(config.XPATH_TABLE_HEADER_STATE_SEARCH, "Icon Search Header State")
        time.sleep(1) 
        
        first_state = config.STATES[0] 
        bot.click_element(config.XPATH_DROPDOWN_ROW.format(first_state), f"Pilih Awal {first_state}")
        bot.click_element(config.XPATH_ACTION_CONFIRM, "Confirm Filter State Awal")
        time.sleep(1.5)

        # 6. MUNDUR & TUKAR KOLOM
        print("\n--- KEMBALI KE PARAMETER UNTUK TUKAR KOLOM ---")
        bot.switch_to_main_page()
        bot.click_element(config.XPATH_BTN_BACK, "Tombol Back")
        time.sleep(2.5)

        bot.switch_to_dashboard_iframe()
        bot.click_element(config.XPATH_BTN_NO_STATE, "State = NO")
        time.sleep(0.5)
        bot.click_element(config.XPATH_BTN_YES_POINTS, "Points = YES")
        time.sleep(1)

        # 7. MAJU KE TABEL FINAL UNTUK LOOPING
        bot.switch_to_main_page()
        bot.click_element(config.XPATH_BTN_NEXT, "Tombol Next Final")
        print("Menunggu tabel final dirender...")
        time.sleep(4) 

        # 8. BACA BULAN DI TABEL AKHIR
        print("\n--- MENGAMBIL DAFTAR BULAN (DI TABEL AKHIR) ---")
        bot.switch_to_main_page()
        time.sleep(0.5)
        
        bot.click_element(config.XPATH_CURRENT_SELECTION_MONTH, "Buka <li> Memori Bulan")
        time.sleep(1.5)

        dynamic_months = bot.get_available_months()
        if not dynamic_months:
            print("⚠️ Ekstraksi bulan gagal, menggunakan list fallback")
            dynamic_months = config.MONTHS 

        first_month = dynamic_months[0]
        
        bot.click_element(config.XPATH_ACTION_CONFIRM, "Tutup Menu Bulan")
        print("Mempersiapkan ekspor data pertama...")
        time.sleep(1.5)

        # ==========================================================
        # 9. NESTED LOOPING (DENGAN AUTO-SKIP RESUME)
        # ==========================================================
        print("\n--- MEMULAI PROSES EKSTRAKSI DATA MASSAL ---")
        
        previous_month = first_month
        previous_state = first_state 

        for month in dynamic_months:
            print(f"\n{'='*50}")
            print(f"📅 MEMASUKI BULAN: {month}")
            print(f"{'='*50}")

            if month != previous_month:
                bot.switch_to_main_page()
                time.sleep(0.5)
                bot.click_element(config.XPATH_CURRENT_SELECTION_MONTH, "Buka <li> Memori Bulan")
                time.sleep(1) 
                
                bot.search_and_select_item(previous_month, "Uncheck Bulan Lama")
                bot.search_and_select_item(month, "Centang Bulan Baru")
                
                bot.click_element(config.XPATH_ACTION_CONFIRM, "Confirm Pergantian Bulan")
                print("Menunggu tabel merender ulang data bulan...")
                time.sleep(1.5)
                previous_month = month
            
            for state in config.STATES:
                print(f"\n  🚀 PROSES STATE: {state}")
                
                # --- FITUR RESUME (SKIP JIKA FILE SUDAH ADA) ---
                safe_prefix = f"Data_EOI_{state}_{month}"
                if bot.check_file_exists(safe_prefix, month):
                    print(f"  ⏭️ File {state} untuk {month} sudah ada. Melewati...")
                    continue # Langsung lompat ke State berikutnya tanpa menyentuh UI!

                if state != previous_state:
                    bot.switch_to_main_page()
                    time.sleep(0.5)
                    bot.click_element(config.XPATH_CURRENT_SELECTION_STATE, "Buka <li> Memori State")
                    time.sleep(1) 
                    
                    bot.click_element(config.XPATH_DROPDOWN_ROW.format(state), f"Centang {state}")
                    time.sleep(0.5)
                    bot.click_element(config.XPATH_DROPDOWN_ROW.format(previous_state), f"Uncheck {previous_state}")
                    time.sleep(0.5)
                    
                    bot.click_element(config.XPATH_ACTION_CONFIRM, "Confirm Pergantian State")
                    print("  Menunggu tabel merender ulang data state...")
                    time.sleep(1)
                    previous_state = state 
                
                bot.switch_to_dashboard_iframe()
                print(f"  [{state}] Mengunduh data...")
                bot.export_table_data()
                bot.wait_and_rename_file(safe_prefix, state_name=state, month_folder=month)
                bot.close_export_dialog()
                time.sleep(1) 

            # PROSES MASTER DATA (MENCENTANG SEMUA STATE)
            safe_prefix_master = f"MASTER_DATA_EOI_{month}"
            if bot.check_file_exists(safe_prefix_master, month):
                print(f"\n  🌟 ⏭️ MASTER DATA untuk {month} sudah ada. Melewati...")
                ui_state_tracker = "SINGLE" # Tandai bahwa UI Qlik masih di posisi Single State
            else:
                print(f"\n  🌟 MENGUNDUH MASTER DATA UNTUK BULAN {month} (ALL STATES)...")
                bot.switch_to_main_page()
                time.sleep(0.5)
                
                bot.click_element(config.XPATH_CURRENT_SELECTION_STATE, "Buka <li> Memori State (Master Data)")
                time.sleep(1.5) 
                
                for st in config.STATES:
                    if st != previous_state:
                        bot.click_element(config.XPATH_DROPDOWN_ROW.format(st), f"Centang {st}")
                        time.sleep(0.3)
                        
                bot.click_element(config.XPATH_ACTION_CONFIRM, "Confirm Master Data")
                print("  Menunggu tabel merender ulang Master Data...")
                time.sleep(1) 
                
                bot.switch_to_dashboard_iframe()
                bot.export_table_data()
                bot.wait_and_rename_file(safe_prefix_master, state_name="ALL STATES", month_folder=month)
                bot.close_export_dialog()
                time.sleep(1.5)
                ui_state_tracker = "ALL" # Tandai bahwa UI Qlik sekarang mencentang SEMUA State

            # PERSIAPAN BULAN BERIKUTNYA (RESET KE STATE PERTAMA)
            if month != dynamic_months[-1]: 
                # Bot hanya perlu mereset jika UI Qlik sedang berantakan (semua tercentang) 
                # atau berada di state yang salah (bukan ACT)
                if ui_state_tracker == "ALL" or (ui_state_tracker == "SINGLE" and previous_state != first_state):
                    print("\n  🌱 Mereset ke State pertama untuk persiapan bulan berikutnya...")
                    bot.switch_to_main_page()
                    time.sleep(0.5)
                    
                    bot.click_element(config.XPATH_CURRENT_SELECTION_STATE, "Buka <li> Memori State (Reset)")
                    time.sleep(1.5)
                    
                    if ui_state_tracker == "ALL":
                        # Kalau tadi Master diekspor, maka uncheck semua kecuali ACT
                        for st in config.STATES:
                            if st != first_state:
                                bot.click_element(config.XPATH_DROPDOWN_ROW.format(st), f"Uncheck {st}")
                                time.sleep(0.3)
                    elif ui_state_tracker == "SINGLE":
                        # Kalau Master ter-skip, maka cukup centang ACT dan uncheck posisi terakhirnya
                        bot.click_element(config.XPATH_DROPDOWN_ROW.format(first_state), f"Centang {first_state}")
                        time.sleep(0.3)
                        bot.click_element(config.XPATH_DROPDOWN_ROW.format(previous_state), f"Uncheck {previous_state}")
                        time.sleep(0.3)
                            
                    bot.click_element(config.XPATH_ACTION_CONFIRM, "Confirm Reset State")
                    time.sleep(1)
                    
                    previous_state = first_state 

        print("\n🎉 SELURUH DATA DARI SEMUA BULAN DAN STATE BERHASIL DIEKSPOR!")

    except Exception as e:
        print(f"❌ Terjadi kesalahan pada alur kerja: {e}")
        
    finally:
        bot.close_browser()

if __name__ == "__main__":
    main()