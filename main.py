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

        # 3. SET PARAMETER (OCCUPATION & POINTS)
        print("\n--- TAHAP 1: SET PARAMETER UTAMA ---")
        bot.switch_to_dashboard_iframe()
        bot.click_element(config.XPATH_BTN_YES_OCCUPATION, "Occupation = YES")
        try:
            bot.click_element(config.XPATH_BTN_YES_POINTS, "Points = YES")
        except:
            print("⚠️ Tombol 'Points' tidak ditemukan, melanjutkan dengan default.")

        # 4. FILTER GLOBAL (VISA & STATUS SUBMITTED)
        print("\n--- SETTING FILTER GLOBAL ---")
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
        bot.click_element(config.XPATH_EOI_SUBMITTED, "SUBMITTED done")
        bot.click_element(config.XPATH_EOI_INVITED, "INVITED done")
        bot.click_element(config.XPATH_EOI_LODGED, "LODGED done")
        bot.click_element(config.XPATH_ACTION_CONFIRM, "Confirm Status")
        time.sleep(1)

        # 5. SMART SEARCH UNTUK STATE & ENGLISH SCORE
        print("\n--- MENANAM STATE & SCORE PERTAMA VIA SMART SEARCH ---")
        bot.switch_to_main_page()
        
        first_state = config.STATES[0]
        bot.use_smart_search(first_state) 
        
        first_score = config.SCORES[0]
        bot.use_smart_search(first_score) 

        # 6. MAJU KE TABEL FINAL
        print("\n--- MAJU KE TABEL FINAL ---")
        bot.click_element(config.XPATH_BTN_NEXT, "Tombol Next Ke Tabel")
        print("Menunggu tabel final dirender...")
        time.sleep(4) 

        # 7. CARI & KUNCI BULAN TERBARU
        bot.switch_to_main_page()
        bot.click_element(config.XPATH_CURRENT_SELECTION_MONTH, "Buka Memori Bulan")
        time.sleep(1.5)

        dynamic_months = bot.get_available_months()
        latest_month = dynamic_months[0] if dynamic_months else config.MONTHS[0]
        
        print(f"\n🌟 MENGUNCI EKSTRAKSI UNTUK BULAN TERBARU: {latest_month}")
        bot.search_and_select_item(latest_month, "Pilih Bulan Terbaru")
        bot.click_element(config.XPATH_ACTION_CONFIRM, "Confirm Menu Bulan")
        time.sleep(1.5)

        # ==========================================================
        # 8. LOOPING GANDA (ENGLISH SCORE -> STATE)
        # ==========================================================
        print("\n--- MEMULAI PROSES EKSTRAKSI DATA ---")
        
        previous_state = first_state 
        previous_score = first_score

        for score in config.SCORES:
            print(f"\n======================================")
            print(f"🎯 MEMULAI EKSTRAKSI UNTUK SKOR: {score}")
            print(f"======================================")

            if score != previous_score:
                bot.switch_to_main_page()
                time.sleep(0.5)
                bot.click_element(config.XPATH_CURRENT_SELECTION_ENGLISH, "Buka Memori English Score")
                time.sleep(1)
                
                bot.click_element(config.XPATH_DROPDOWN_ROW.format(score), f"Centang Skor {score}")
                time.sleep(0.5)
                bot.click_element(config.XPATH_DROPDOWN_ROW.format(previous_score), f"Uncheck Skor {previous_score}")
                time.sleep(0.5)
                bot.click_element(config.XPATH_ACTION_CONFIRM, "Confirm Pergantian Skor")
                time.sleep(1.5)
                previous_score = score

            for state in config.STATES:
                print(f"\n  🚀 PROSES STATE: {state} (Skor: {score})")
                safe_prefix = f"EOI_{state}_SCORE_{score}_{latest_month.replace('/', '_')}"
                
                if bot.check_file_exists(safe_prefix, english_score=score):
                    print(f"  ⏭️ File sudah ada di folder Score_{score}. Skip...")
                    continue 

                if state != previous_state:
                    bot.switch_to_main_page()
                    time.sleep(0.5)
                    bot.click_element(config.XPATH_CURRENT_SELECTION_STATE, "Buka Memori State")
                    time.sleep(1) 
                    
                    bot.click_element(config.XPATH_DROPDOWN_ROW.format(state), f"Centang {state}")
                    time.sleep(0.5)
                    bot.click_element(config.XPATH_DROPDOWN_ROW.format(previous_state), f"Uncheck {previous_state}")
                    time.sleep(0.5)
                    bot.click_element(config.XPATH_ACTION_CONFIRM, "Confirm Pergantian State")
                    time.sleep(1.5)
                    previous_state = state 
                
                bot.switch_to_dashboard_iframe()
                print(f"  [{state} - Skor {score}] Mengunduh data...")
                bot.export_table_data()
                bot.wait_and_rename_file(safe_prefix, state_name=state, english_score=score) 
                bot.close_export_dialog()
                time.sleep(1)

        print("\n🎉 SELURUH DATA UNTUK BULAN TERBARU BERHASIL DIEKSPOR!")

    except Exception as e:
        print(f"❌ Terjadi kesalahan pada alur kerja: {e}")
        
    finally:
        bot.close_browser()

if __name__ == "__main__":
    main()