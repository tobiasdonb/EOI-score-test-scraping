import os
import time
import glob
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import config

class SkillSelectScraper:
    def __init__(self, worker_id=0):
        self.worker_id = worker_id
        self.log_prefix = f"[W{worker_id}]"
        
        # Setiap worker punya folder download sendiri agar file tidak bertabrakan
        self.worker_download_dir = os.path.join(config.DOWNLOAD_DIR, f"_worker_{worker_id}_tmp")
        if not os.path.exists(self.worker_download_dir):
            os.makedirs(self.worker_download_dir)
        if not os.path.exists(config.DOWNLOAD_DIR):
            os.makedirs(config.DOWNLOAD_DIR)
            
        self.driver = self._setup_driver()
        self.wait = WebDriverWait(self.driver, 20)

    def _log(self, msg):
        """Print dengan prefix worker ID."""
        print(f"{self.log_prefix} {msg}")

    def _setup_driver(self):
        options = webdriver.ChromeOptions()
        if config.HEADLESS:
            self._log("🚀 Menjalankan Chrome dalam mode HEADLESS...")
            options.add_argument('--headless=new')
            options.add_argument('--window-size=1920,1080')
        else:
            self._log("🖥️ Menjalankan Chrome dalam mode VISUAL...")
        
        options.add_argument('--start-maximized')
        options.page_load_strategy = 'eager' 
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        prefs = {
            "download.default_directory": self.worker_download_dir,
            "download.prompt_for_download": False,
            "directory_upgrade": True,
            "safebrowsing.enabled": True,
            "profile.managed_default_content_settings.images": 2 
        }
        options.add_experimental_option("prefs", prefs)
        
        driver = webdriver.Chrome(options=options)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })
        return driver

    def switch_to_main_page(self):
        self.driver.switch_to.default_content()
        time.sleep(1)

    def switch_to_dashboard_iframe(self):
        self.driver.switch_to.default_content()
        try:
            iframe = self.wait.until(EC.presence_of_element_located((By.XPATH, config.XPATH_IFRAME)))
            self.driver.switch_to.frame(iframe)
            time.sleep(4) 
        except Exception as e:
            print(f"❌ Gagal masuk ke Iframe: {e}")

    def click_element(self, xpath, action_name="elemen"):
        element = None
        try:
            element = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'nearest'});", element)
            time.sleep(0.5) 
            
            actions = ActionChains(self.driver)
            actions.move_to_element(element).click().perform()
            print(f"✅ Klik: {action_name}")
            time.sleep(0.5) 
        except Exception as e:
            if element:
                self.driver.execute_script("arguments[0].click();", element)
                print(f"✅ Klik (JS): {action_name}")
                time.sleep(0.5)

    def use_smart_search(self, keyword):
        print(f"🔍 Menggunakan Smart Search untuk: {keyword}")
        try:
            self.click_element(config.XPATH_SMART_SEARCH_BTN, "Tombol Smart Search")
            time.sleep(0.5)

            search_input = self.wait.until(EC.presence_of_element_located((By.XPATH, config.XPATH_SMART_SEARCH_INPUT)))
            search_input.clear()
            search_input.send_keys(keyword)
            time.sleep(1) 

            self.click_element(config.XPATH_SMART_SEARCH_FIRST_RESULT, "Hasil Pencarian Pertama (Smart Search)")
            time.sleep(1)

            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            print(f"✅ Berhasil menanam State '{keyword}' dari Smart Search.")
        except Exception as e:
            print(f"❌ Gagal menggunakan Smart Search: {e}")

    def get_current_selection_text(self, xpath):
        """
        Baca teks/title yang sedang aktif pada pill 'Current Selections' (misalnya 'As At Month')
        TANPA harus membuka listbox terlebih dahulu.
        Mengembalikan string nilai yang terpilih, atau None jika tidak ada.
        """
        try:
            # Coba ambil dari atribut 'title' pada elemen pill
            el = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            title = el.get_attribute("title")
            if title and title.strip():
                clean_val = title.strip().split('\n')[-1].strip()
                print(f"📖 Terbaca dari pill (title): '{clean_val}'")
                return clean_val
            # Fallback: ambil dari teks inner span
            text = el.text.strip()
            if text:
                clean_val = text.strip().split('\n')[-1].strip()
                print(f"📖 Terbaca dari pill (text): '{clean_val}'")
                return clean_val
            return None

        except Exception as e:
            print(f"⚠️ Tidak dapat membaca current selection: {e}")
            return None

    def get_available_months(self):

        print("Membaca daftar bulan untuk mencari data terbaru...")
        try:
            scroll_container = self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'ListBox-styledScrollbars')]")))
            months_set = set() 
            last_scroll_position = -1

            while True:
                elements = self.driver.find_elements(By.XPATH, "//div[@role='row']//div[contains(@class, 'RowColumn-cell') and @title]")
                for el in elements:
                    title = el.get_attribute("title")
                    if title and "/" in title:
                        months_set.add(title.strip())

                self.driver.execute_script("arguments[0].scrollTop += 200;", scroll_container)
                time.sleep(0.5) 
                current_scroll_position = self.driver.execute_script("return arguments[0].scrollTop;", scroll_container)
                if current_scroll_position == last_scroll_position:
                    break 
                last_scroll_position = current_scroll_position

            months = list(months_set)
            months.sort(key=lambda x: (int(x.split('/')[1]), int(x.split('/')[0])), reverse=True)
            return months
        except Exception as e:
            return []

    def uncheck_selected_rows(self, exclude=None):
        """Uncheck semua row yang sedang tercentang, kecuali yang ada di 'exclude'."""
        try:
            print(f"🔄 Memulai uncheck mendalam (Target Tetap: '{exclude}')...")
            
            # --- 1. Paksa Kosongkan Search Box ---
            try:
                search_boxes = self.driver.find_elements(By.XPATH, config.XPATH_SEARCH_LISTBOX)
                if search_boxes:
                    sb = search_boxes[0]
                    self.driver.execute_script("arguments[0].value = '';", sb)
                    sb.send_keys(Keys.ENTER) # Trigger refresh
                    print("✅ Search box dikosongkan.")
                    time.sleep(1.5)
            except: pass

            # --- 2. Inisialisasi Scroll ---
            try:
                scroll_container = self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'ListBox-styledScrollbars')]")))
            except:
                scroll_container = None

            last_scroll_pos = -1
            processed_titles = set()
            uncheck_count = 0
            
            # --- 3. Looping Scroll & Uncheck ---
            for _ in range(12): # Max 12 scrolls
                xpath_selected = "//div[@role='row' and (@aria-selected='true' or .//i[contains(@class, 'lui-icon--tick')])]"
                current_selected = self.driver.find_elements(By.XPATH, xpath_selected)
                
                for row in current_selected:
                    try:
                        title_el = row.find_element(By.XPATH, ".//div[contains(@class, 'RowColumn-cell') and @title]")
                        title = title_el.get_attribute("title").strip()
                        
                        if title in processed_titles: continue
                        processed_titles.add(title)

                        if exclude and title == exclude.strip():
                            print(f"  ⏭️ Skip (ingin tetap tercentang): '{title}'")
                            continue
                        
                        print(f"  ✅ Melakukan UNCHECK pada: '{title}'")
                        # Klik spesifik pada element title agar lebih akurat di Qlik
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", title_el)
                        time.sleep(0.3)
                        self.driver.execute_script("arguments[0].click();", title_el)
                        uncheck_count += 1
                        time.sleep(0.5)
                    except: continue

                if not scroll_container: break
                
                self.driver.execute_script("arguments[0].scrollTop += 350;", scroll_container)
                time.sleep(0.8)
                curr_pos = self.driver.execute_script("return arguments[0].scrollTop;", scroll_container)
                if curr_pos == last_scroll_pos: break
                last_scroll_pos = curr_pos

            print(f"🎉 Selesai. Total item di-uncheck: {uncheck_count}")
            time.sleep(1.2)
                
        except Exception as e:
            print(f"❌ Gagal uncheck: {e}")

    def search_and_select_item(self, item_text, action_name="Item"):
        try:
            search_box = self.wait.until(EC.element_to_be_clickable((By.XPATH, config.XPATH_SEARCH_LISTBOX)))
            search_box.send_keys(Keys.CONTROL + "a")
            time.sleep(0.2)
            search_box.send_keys(Keys.BACKSPACE)
            time.sleep(0.5)
            search_box.send_keys(item_text)
            time.sleep(1.0) 
            
            xpath_target = config.XPATH_DROPDOWN_ROW.format(item_text)
            row_element = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath_target)))
            
            ticks = row_element.find_elements(By.XPATH, ".//i[contains(@class, 'lui-icon--tick')]")
            is_selected = row_element.get_attribute("aria-selected") == "true"
            
            if ticks or is_selected:
                print(f"✅ {item_text} sudah dalam kondisi terpilih (tercentang).")
            else:
                self.click_element(xpath_target, action_name)
                
        except Exception as e:
            print(f"❌ Gagal mencari {item_text}: {e}")

    def search_and_unselect_item(self, item_text, action_name="Item"):
        if not item_text:
            return
        print(f"🔄 Menggunakan Search Explicit untuk UNCHECK: '{item_text}'")
        try:
            search_box = self.wait.until(EC.element_to_be_clickable((By.XPATH, config.XPATH_SEARCH_LISTBOX)))
            self.driver.execute_script("arguments[0].value = '';", search_box)
            search_box.send_keys(Keys.CONTROL + "a")
            search_box.send_keys(Keys.BACKSPACE)
            time.sleep(0.5)
            
            search_box.send_keys(item_text)
            time.sleep(1.5) 
            
            xpath_target = config.XPATH_DROPDOWN_ROW.format(item_text)
            row_element = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath_target)))
            
            ticks = row_element.find_elements(By.XPATH, ".//i[contains(@class, 'lui-icon--tick')]")
            is_selected = row_element.get_attribute("aria-selected") == "true"
            
            if ticks or is_selected:
                print(f"  🔍 Ditemukan {item_text} dalam keadaan tercentang, mengeklik untuk uncheck...")
                self.click_element(xpath_target, action_name)
                time.sleep(0.5)
            else:
                print(f"  ℹ️ {item_text} sudah TIDAK tercentang.")
                
        except Exception as e:
            print(f"❌ Gagal mencari & unselect {item_text}: {e}")

    def export_table_data(self):
        try:
            print("Mencari sel tabel untuk di-klik kanan...")
            table_cell = self.wait.until(EC.visibility_of_element_located((By.XPATH, config.XPATH_TABLE_CELL)))
            
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", table_cell)
            time.sleep(1)
            
            # Mencoba klik kanan sampai menu muncul (max 3 kali)
            menu_opened = False
            for attempt in range(3):
                print(f"Melakukan klik kanan pada tabel (Percobaan {attempt+1})...")
                actions = ActionChains(self.driver)
                actions.context_click(table_cell).perform()
                time.sleep(2)
                
                if self.driver.find_elements(By.XPATH, config.XPATH_EXPORT_DATA):
                    menu_opened = True
                    break
                else:
                    print("⚠️ Menu belum terbuka, mencoba klik kanan dengan JS...")
                    self.driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('contextmenu', {bubbles: true, cancelable: true, view: window}));", table_cell)
                    time.sleep(2)
                    if self.driver.find_elements(By.XPATH, config.XPATH_EXPORT_DATA):
                        menu_opened = True
                        break

            if not menu_opened:
                raise Exception("Gagal membuka menu konteks (Export data) setelah 3 percobaan.")

            print("Mengeklik pilihan 'Export data'...")
            export_menu = self.wait.until(EC.element_to_be_clickable((By.XPATH, config.XPATH_EXPORT_DATA)))
            try:
                export_menu.click() 
            except:
                self.driver.execute_script("arguments[0].click();", export_menu)
            
            time.sleep(2) 
            print("Mengeklik tombol 'Export' di dalam dialog...")
            self.click_element(config.XPATH_DIALOG_EXPORT_BTN, "Tombol Export (Dialog)")
            
            print("Menunggu server Qlik men-generate file (bisa memakan waktu)...")
            wait_long = WebDriverWait(self.driver, 120) 
            download_link = wait_long.until(EC.element_to_be_clickable((By.XPATH, config.XPATH_DOWNLOAD_LINK)))
            
            self.driver.execute_script("arguments[0].click();", download_link)
            print("✅ Link download berhasil diklik! Proses pengunduhan di background berjalan...")
            time.sleep(1.5) 
            
        except Exception as e:
            print(f"❌ Gagal melakukan proses ekspor tabel: {e}")

    def close_export_dialog(self):
        print("Menutup dialog ekspor...")
        try:
            self.click_element(config.XPATH_DIALOG_CLOSE_BTN, "Tombol Close Dialog")
            time.sleep(0.5)
        except:
            print("⚠️ Tombol close terhalang, mencoba menekan tombol ESCAPE...")
            try:
                ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                time.sleep(0.5)
            except Exception as e:
                print(f"❌ Gagal menutup dialog: {e}")

    def check_file_exists(self, filename_prefix, english_score):
        target_dir = os.path.join(config.DOWNLOAD_DIR, f"Score_{english_score}")
        
        if not os.path.exists(target_dir):
            return False
            
        search_pattern = os.path.join(target_dir, f"{filename_prefix}_*.csv")
        return len(glob.glob(search_pattern)) > 0

    def wait_and_rename_file(self, filename_prefix, state_name=None, english_score=None): 
        self._log("Menunggu file selesai diunduh...")
        timeout = 180 
        start_time = time.time()
        
        target_dir = os.path.join(config.DOWNLOAD_DIR, f"Score_{english_score}") if english_score else config.DOWNLOAD_DIR
        
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        while True:
            # Cari di folder worker sendiri
            files = os.listdir(self.worker_download_dir)
            if any(f.endswith('.crdownload') or f.endswith('.tmp') for f in files):
                time.sleep(1)
            else:
                time.sleep(2)
                break
            if time.time() - start_time > timeout:
                return

        list_of_files = glob.glob(os.path.join(self.worker_download_dir, '*.xlsx'))
        if not list_of_files: 
            self._log("⚠️ Tidak ada file .xlsx ditemukan di folder download worker!")
            return
            
        latest_file = max(list_of_files, key=os.path.getctime)
        new_name = f"{filename_prefix}_{int(time.time())}.csv"
        new_path = os.path.join(target_dir, new_name)
        
        try:
            df = pd.read_excel(latest_file)
            
            if english_score is not None:
                df['English Test Score'] = english_score
            if state_name is not None:
                df['State'] = state_name
                
            df.to_csv(new_path, index=False)
            self._log(f"✅ Berhasil di-convert dan simpan ke: {new_name}")
            os.remove(latest_file)
        except Exception as e:
            self._log(f"❌ Gagal memanipulasi file Pandas: {e}")

    def close_browser(self):
        self.driver.quit()