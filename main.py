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

        # 5. SMART SEARCH UNTUK STATE & ENGLISH SCORE PERTAMA
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

        # 7. GENERATE DAFTAR BULAN DARI CONFIG (END_MONTH → START_MONTH)
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

        dynamic_months = generate_month_range(config.START_MONTH, config.END_MONTH)
        print(f"\n📅 Range bulan dari config: {config.END_MONTH} → {config.START_MONTH}")
        print(f"📋 Total {len(dynamic_months)} bulan akan diproses: {dynamic_months}")
        print("🔄 Akan diproses dari terbaru ke terlama\n")

        # 8. BACA BULAN AUTO-TERSELECT DARI PILL, LALU INISIALISASI BULAN PERTAMA
        current_month = dynamic_months[0]
        print(f"\n🌟 BULAN TARGET PERTAMA: {current_month}")

        # Baca bulan yang sudah otomatis ter-checklist dari text pill (SEBELUM buka listbox)
        bot.switch_to_main_page()
        auto_checked_month = bot.get_current_selection_text(config.XPATH_CURRENT_SELECTION_MONTH)
        if auto_checked_month:
            print(f"⚠️ Dashboard auto-checklist bulan: '{auto_checked_month}' — akan di-uncheck")
        else:
            print("ℹ️ Tidak ada bulan yang auto-terselect di pill, lanjut...")

        # Step 1: Buka listbox → pilih bulan target → confirm
        bot.click_element(config.XPATH_CURRENT_SELECTION_MONTH, "Buka Memori Bulan")
        time.sleep(1.5)
        bot.search_and_select_item(current_month, "Pilih Bulan Pertama")
        bot.click_element(config.XPATH_ACTION_CONFIRM, "Confirm Pilih Bulan Pertama")
        time.sleep(1.5)

        # Step 2: Buka listbox lagi → uncheck bulan yang auto-terselect (kecuali bulan target)
        if auto_checked_month and auto_checked_month != current_month:
            bot.switch_to_main_page()
            bot.click_element(config.XPATH_CURRENT_SELECTION_MONTH, "Buka Memori Bulan (Uncheck Auto)")
            time.sleep(1.5)
            bot.search_and_unselect_item(auto_checked_month, "Uncheck Auto-Checklist")
            time.sleep(0.5)
            bot.click_element(config.XPATH_ACTION_CONFIRM, "Confirm Uncheck Auto-Checklist")
            time.sleep(1.5)

        # ==========================================================
        # 9. LOOP UTAMA: BULAN -> SCORE -> STATE
        # ==========================================================
        for month_idx, month in enumerate(dynamic_months):
            print(f"\n{'='*60}")
            print(f"📅 BULAN [{month_idx+1}/{len(dynamic_months)}]: {month}")
            print(f"{'='*60}")

            # --- GANTI BULAN jika bukan bulan pertama ---
            if month_idx > 0:
                previous_month = dynamic_months[month_idx - 1]
                print(f"\n🔄 Mengganti bulan: {previous_month} → {month}")
                
                # Step 1: Buka menu → pilih bulan baru → confirm
                bot.switch_to_main_page()
                bot.click_element(config.XPATH_CURRENT_SELECTION_MONTH, "Buka Memori Bulan")
                time.sleep(1.3)
                bot.search_and_select_item(month, f"Pilih Bulan {month}")
                bot.click_element(config.XPATH_ACTION_CONFIRM, "Confirm Menu Bulan")
                time.sleep(1.3)
                
                # Step 2: Buka menu lagi → uncheck bulan lama → confirm
                bot.switch_to_main_page()
                bot.click_element(config.XPATH_CURRENT_SELECTION_MONTH, "Buka Memori Bulan (Uncheck)")
                time.sleep(1.3)
                bot.search_and_unselect_item(previous_month, f"Uncheck Bulan {previous_month}")
                time.sleep(0.5)
                bot.click_element(config.XPATH_ACTION_CONFIRM, "Confirm Uncheck Bulan Lama")
                time.sleep(1.3)

                # Reset state & score ke awal via Smart Search
                print(f"\n🔁 Reset State & Score ke awal untuk bulan {month}")
                bot.switch_to_main_page()

                # Reset state ke pertama
                bot.click_element(config.XPATH_CURRENT_SELECTION_STATE, "Buka Memori State")
                time.sleep(1)
                bot.search_and_select_item(first_state, f"Centang {first_state}")
                time.sleep(0.5)
                bot.uncheck_selected_rows(exclude=first_state)
                time.sleep(0.5)
                bot.click_element(config.XPATH_ACTION_CONFIRM, "Confirm Reset State")
                time.sleep(1.5)

                # Reset score ke pertama
                bot.switch_to_main_page()
                bot.click_element(config.XPATH_CURRENT_SELECTION_ENGLISH, "Buka Memori English Score")
                time.sleep(1)
                bot.search_and_select_item(first_score, f"Centang Skor {first_score}")
                time.sleep(0.5)
                bot.uncheck_selected_rows(exclude=first_score)
                time.sleep(0.5)
                bot.click_element(config.XPATH_ACTION_CONFIRM, "Confirm Reset Skor")
                time.sleep(1.5)

            # --- LOOPING SCORE -> STATE untuk bulan ini ---
            previous_state = first_state 
            previous_score = first_score

            for score in config.SCORES:
                print(f"\n  ======================================")
                print(f"  🎯 SKOR: {score} | BULAN: {month}")
                print(f"  ======================================")

                if score != previous_score:
                    bot.switch_to_main_page()
                    time.sleep(0.5)
                    bot.click_element(config.XPATH_CURRENT_SELECTION_ENGLISH, "Buka Memori English Score")
                    time.sleep(1)
                    
                    bot.click_element(config.XPATH_DROPDOWN_ROW.format(score), f"Centang Skor {score}")
                    time.sleep(0.5)
                    bot.click_element(config.XPATH_DROPDOWN_ROW.format(previous_score), f"Uncheck Skor {previous_score}")
                    time.sleep(0.8) # JEDA SEGERA SEBELUM CONFIRM HARUS CUKUP
                    bot.click_element(config.XPATH_ACTION_CONFIRM, "Confirm Pergantian Skor")
                    time.sleep(1.2)
                    previous_score = score

                for state in config.STATES:
                    print(f"\n    🚀 STATE: {state} | SKOR: {score} | BULAN: {month}")
                    safe_prefix = f"EOI_{state}_SCORE_{score}_{month.replace('/', '_')}"
                    
                    if bot.check_file_exists(safe_prefix, english_score=score):
                        print(f"    ⏭️ File sudah ada di folder Score_{score}. Skip...")
                        continue 

                    if state != previous_state:
                        bot.switch_to_main_page()
                        time.sleep(0.2)
                        bot.click_element(config.XPATH_CURRENT_SELECTION_STATE, "Buka Memori State")
                        time.sleep(0.7) 
                        bot.click_element(config.XPATH_DROPDOWN_ROW.format(state), f"Centang {state}")
                        time.sleep(0.4)
                        bot.click_element(config.XPATH_DROPDOWN_ROW.format(previous_state), f"Uncheck {previous_state}")
                        time.sleep(0.7) # JEDA SEGERA SEBELUM CONFIRM HARUS CUKUP LAMA UNTUK MENGHINDARI RACE CONDITION 
                        bot.click_element(config.XPATH_ACTION_CONFIRM, "Confirm Pergantian State")
                        time.sleep(1.0)
                        previous_state = state 
                    
                    bot.switch_to_dashboard_iframe()
                    print(f"    [{state} - Skor {score} - {month}] Mengunduh data...")
                    bot.export_table_data()
                    bot.wait_and_rename_file(safe_prefix, state_name=state, english_score=score) 
                    bot.close_export_dialog()
                    time.sleep(0.8)

            print(f"\n✅ Selesai untuk bulan {month}!")

        print(f"\n🎉 SELURUH DATA UNTUK {len(dynamic_months)} BULAN BERHASIL DIEKSPOR!")

    except Exception as e:
        print(f"❌ Terjadi kesalahan pada alur kerja: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        bot.close_browser()

if __name__ == "__main__":
    main()