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
    def __init__(self):
        if not os.path.exists(config.DOWNLOAD_DIR):
            os.makedirs(config.DOWNLOAD_DIR)
        self.driver = self._setup_driver()
        self.wait = WebDriverWait(self.driver, 20)

    def _setup_driver(self):
        options = webdriver.ChromeOptions()
 
        if config.HEADLESS:
            print("🚀 Menjalankan Chrome dalam mode HEADLESS (Latar Belakang)...")
            options.add_argument('--headless=new')
            options.add_argument('--window-size=1920,1080') # Tetap butuh ukuran layar agar UI tidak rusak
        else:
            print("🖥️ Menjalankan Chrome dalam mode VISUAL (Terlihat)...")
        
        options.add_argument('--start-maximized')
        
        # Mode Eager agar langsung jalan tanpa menunggu background loading Qlik
        options.page_load_strategy = 'eager' 
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        prefs = {
            "download.default_directory": config.DOWNLOAD_DIR,
            "download.prompt_for_download": False,
            "directory_upgrade": True,
            "safebrowsing.enabled": True,
            "profile.managed_default_content_settings.images": 2 # Mematikan gambar agar ngebut
        }
        options.add_experimental_option("prefs", prefs)
        
        driver = webdriver.Chrome(options=options)
        
        # Bypass Anti-Bot
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
            print(f"⚠️ ActionChains gagal pada {action_name}. Mencoba injeksi MouseEvent JS...")
            if element:
                try:
                    self.driver.execute_script("""
                        var evt = new MouseEvent('mousedown', {bubbles: true, cancelable: true, view: window});
                        arguments[0].dispatchEvent(evt);
                        var evt2 = new MouseEvent('mouseup', {bubbles: true, cancelable: true, view: window});
                        arguments[0].dispatchEvent(evt2);
                        var evt3 = new MouseEvent('click', {bubbles: true, cancelable: true, view: window});
                        arguments[0].dispatchEvent(evt3);
                    """, element)
                    print(f"✅ Klik (JS MouseEvent): {action_name}")
                    time.sleep(0.5)
                except Exception as js_e:
                    print(f"❌ Alternatif JS gagal: {js_e}")
            else:
                print(f"❌ {action_name} tidak ditemukan di layar! (Timeout)")

    def get_available_months(self):
        print("Mencari dan membaca seluruh daftar bulan (Scrolling otomatis)...")
        try:
            scroll_container = self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'ListBox-styledScrollbars')]")))
            time.sleep(1)

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

            print(f"✅ Berhasil mengekstrak {len(months)} bulan: {months}")
            
            self.driver.execute_script("arguments[0].scrollTop = 0;", scroll_container)
            time.sleep(1)
            
            return months
            
        except Exception as e:
            print(f"❌ Gagal mengekstrak daftar bulan secara dinamis: {e}")
            return []
    
    def search_and_select_item(self, item_text, action_name="Item"):
        print(f"Mengetik '{item_text}' di kolom pencarian...")
        try:
            search_box = self.wait.until(EC.element_to_be_clickable((By.XPATH, config.XPATH_SEARCH_LISTBOX)))
            
            search_box.send_keys(Keys.CONTROL + "a")
            time.sleep(0.2)
            search_box.send_keys(Keys.BACKSPACE)
            time.sleep(0.5)
            
            search_box.send_keys(item_text)
            time.sleep(1.5) 
            
            xpath_target = config.XPATH_DROPDOWN_ROW.format(item_text)
            self.click_element(xpath_target, action_name)
            
        except Exception as e:
            print(f"❌ Gagal mencari {item_text} via Search: {e}")

    def export_table_data(self):
        try:
            print("Mencari sel tabel untuk di-klik kanan...")
            table_cell = self.wait.until(EC.visibility_of_element_located((By.XPATH, config.XPATH_TABLE_CELL)))
            
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", table_cell)
            time.sleep(1)
            
            print("Melakukan klik kanan pada tabel...")
            actions = ActionChains(self.driver)
            actions.context_click(table_cell).perform()
            time.sleep(1.5)
            
            if not self.driver.find_elements(By.XPATH, config.XPATH_EXPORT_DATA):
                print("⚠️ Menu belum terbuka, mencoba klik kanan dengan JS...")
                self.driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('contextmenu', {bubbles: true, cancelable: true, view: window}));", table_cell)
                time.sleep(1.5)
            
            print("Mengeklik pilihan 'Export data'...")
            export_menu = self.wait.until(EC.element_to_be_clickable((By.XPATH, config.XPATH_EXPORT_DATA)))
            try:
                export_menu.click() 
                print("✅ Pilihan 'Export data' berhasil diklik!")
            except:
                self.driver.execute_script("arguments[0].click();", export_menu)
                print("✅ Pilihan 'Export data' berhasil diklik (via JS)!")
            
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

    # ==============================================================
    # --- FITUR BARU: CEK FILE CSV ---
    # ==============================================================
    def check_file_exists(self, filename_prefix, month_folder):
        """Mengecek apakah file .csv dengan prefix tertentu sudah ada di folder Tahun/Bulan"""
        year = month_folder.split('/')[1]
        safe_month = month_folder.replace('/', '_').replace('\\', '_')
        safe_prefix = filename_prefix.replace('/', '_').replace('\\', '_')
        
        target_dir = os.path.join(config.DOWNLOAD_DIR, year, safe_month)
        
        if not os.path.exists(target_dir):
            return False
            
        # Mencari file yang berekstensi .csv
        search_pattern = os.path.join(target_dir, f"{safe_prefix}_*.csv")
        existing_files = glob.glob(search_pattern)
        
        return len(existing_files) > 0

    def wait_and_rename_file(self, filename_prefix, state_name=None, month_folder=None):
        print("Menunggu file selesai diunduh...")
        timeout = 180 
        start_time = time.time()
        
        target_dir = config.DOWNLOAD_DIR
        if month_folder:
            year = month_folder.split('/')[1]
            safe_month = month_folder.replace('/', '_').replace('\\', '_')
            
            # Struktur folder sekarang: DATASET/2026/02_2026/
            target_dir = os.path.join(config.DOWNLOAD_DIR, year, safe_month)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)

        while True:
            files = os.listdir(config.DOWNLOAD_DIR)
            if any(f.endswith('.crdownload') or f.endswith('.tmp') for f in files):
                time.sleep(1)
            else:
                time.sleep(2)
                break
                
            if time.time() - start_time > timeout:
                print("❌ Timeout! File gagal diunduh atau jaringan lambat.")
                return

        # Tetap ambil file .xlsx karena default unduhan Qlik adalah Excel
        list_of_files = glob.glob(os.path.join(config.DOWNLOAD_DIR, '*.xlsx'))
        if not list_of_files: 
            print("❌ File excel tidak ditemukan setelah proses download.")
            return
            
        latest_file = max(list_of_files, key=os.path.getctime)
        
        safe_prefix = filename_prefix.replace('/', '_').replace('\\', '_')
        # GANTI EKSTENSI MENJADI .csv
        new_name = f"{safe_prefix}_{int(time.time())}.csv"
        new_path = os.path.join(target_dir, new_name)
        
        try:
            print(f"Mengonversi file ke CSV dan menyuntikkan identitas data...")
            # Membaca file Excel mentah yang baru didownload
            df = pd.read_excel(latest_file)
            
            if state_name:
                df['Nominated State'] = state_name
            if month_folder:
                df['As At Month'] = month_folder
                
            # Menyimpan data dalam format CSV
            df.to_csv(new_path, index=False)
            print(f"✅ Berhasil dikonversi dan disimpan ke: {new_path}")
            
            # Hapus file Excel asli dari folder downloads agar tidak menumpuk
            os.remove(latest_file)
            
        except Exception as e:
            print(f"❌ Gagal mengonversi atau memanipulasi file: {e}")

    def close_browser(self):
        self.driver.quit()