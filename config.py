import os

# ==========================================
# KONFIGURASI DIREKTORI & TARGET
# ==========================================
BASE_DIR = os.getcwd()
DOWNLOAD_DIR = os.path.join(BASE_DIR, "DATASET")
URL = "https://api.dynamic.reports.employment.gov.au/anonap/extensions/hSKLS02_SkillSelect_EOI_Data/hSKLS02_SkillSelect_EOI_Data.html"

HEADLESS = True  # Ubah ke False jika ingin melihat browser berjalan

# Fallback/Cadangan list bulan jika ekstraksi dinamis di web Qlik gagal
MONTHS = ['01/2026', '02/2026', '03/2026'] 
STATES = ['ACT', 'NSW', 'NT', 'QLD', 'SA', 'TAS', 'VIC', 'WA']

# ==========================================
# XPATH SELECTORS
# ==========================================

# --- IFRAME BUNGKUSAN UTAMA ---
XPATH_IFRAME = "//iframe[@id='f1']"

# --- TOP BAR NAVIGASI ---
XPATH_CLEAR_ALL = "//button[@id='clearselections']"
XPATH_BTN_NEXT = "//a[@data-qcmd='navNext']"
XPATH_BTN_BACK = "//a[@data-qcmd='navBack']"

# --- SETTING PARAMETER (YES/NO) SUPER AKURAT ---
XPATH_BTN_YES_OCCUPATION = "//div[contains(@class, 'qsc-root') and .//span[@title='Occupations']]//button[@data-value='Y']"
XPATH_BTN_YES_POINTS = "//div[contains(@class, 'qsc-root') and .//span[@title='Points']]//button[@data-value='Y']"
XPATH_BTN_NO_POINTS = "//div[contains(@class, 'qsc-root') and .//span[@title='Points']]//button[@data-value='N']"
XPATH_BTN_YES_STATE = "//div[contains(@class, 'qsc-root') and .//span[@title='Nominated State']]//button[@data-value='Y']"
XPATH_BTN_NO_STATE = "//div[contains(@class, 'qsc-root') and .//span[@title='Nominated State']]//button[@data-value='N']"

# --- FILTER GLOBAL (FOLDED LISTBOX) ---
# Tombol Expand untuk membuka Filter Pane
XPATH_DROPDOWN_SELECT = "//button[@data-testid='filterpane-expand-button']"

# Header untuk membuka menu dropdown yang terlipat
XPATH_HEADER_VISA_TYPE = "//div[@data-testid='collapsed-title-Visa Type']"
XPATH_HEADER_EOI_STATUS = "//div[@data-testid='collapsed-title-EOI Status']"
XPATH_HEADER_MONTH = "//div[@data-testid='collapsed-title-As At Month']"

# Opsi Visa
XPATH_VISA_189 = "//div[@role='row' and .//div[@title='189PTS Points-Tested Stream']]"
XPATH_VISA_190 = "//div[@role='row' and .//div[@title='190SAS Skilled Australian Sponsored']]"
XPATH_VISA_491_SR = "//div[@role='row' and .//div[@title='491FSR Family Sponsored - Regional']]"
XPATH_VISA_491_ST = "//div[@role='row' and .//div[@title='491SNR State or Territory Nominated - Regional']]"    

# Opsi EOI Status
XPATH_EOI_SUBMITTED = "//div[@role='row' and .//div[@title='SUBMITTED']]"
XPATH_EOI_INVITED = "//div[@role='row' and .//div[@title='INVITED']]"
XPATH_EOI_LODGED = "//div[@role='row' and .//div[@title='LODGED']]"
XPATH_EOI_HOLD = "//div[@role='row' and .//div[@title='HOLD']]"
XPATH_EOI_CLOSED = "//div[@role='row' and .//div[@title='CLOSED']]"

# Aksi Panel Filter
XPATH_ACTION_CONFIRM = "//button[@data-testid='actions-toolbar-confirm']"
XPATH_ACTION_CLEAR = "//button[@data-testid='actions-toolbar-clear']"

# --- FILTER TABEL & CURRENT SELECTIONS ---
XPATH_STATE_HEADER = "//h6[contains(@title, 'Nominated State') or contains(@title, 'Nominating State')]"
XPATH_TABLE_HEADER_STATE_SEARCH = "//th[contains(@aria-label, 'Nominated State')]//i[contains(@class, 'lui-icon--search')]"

# Membidik elemen <li> di luar iframe. Memastikan yang diklik adalah tombolnya, bukan tombol silang (remove)
XPATH_CURRENT_SELECTION_STATE = "//li[@data-csid='Nominated State']//div[contains(@class, 'current-selection-item-text') and @role='button']"
XPATH_CURRENT_SELECTION_MONTH = "//li[@data-csid='As At Month']//div[contains(@class, 'current-selection-item-text') and @role='button']"

# Opsi universal untuk Dropdown (Bisa digunakan format string untuk memilih State maupun Bulan)
XPATH_DROPDOWN_ROW = "//div[@role='row' and .//div[@title='{}']]"

# Tombol untuk menghapus (clear) State yang sedang terpilih di Current Selections Bar
XPATH_CLEAR_CURRENT_STATE = "//div[@title='Clear selection for field: Nominated State']"


# ==========================================
# EXPORT DATA
# ==========================================
# Sel data pertama (indeks [1]) dari tabel untuk diklik kanan
XPATH_TABLE_CELL = "(//td[@data-tid='qv-st-cell'])[1]" 

# Menu klik kanan Qlik Sense
XPATH_EXPORT_DATA = "//*[contains(text(), 'Export data') or contains(text(), 'Export Data')]"

# Elemen di dalam Dialog Export
XPATH_DIALOG_EXPORT_BTN = "//button[@tid='table-export']"
XPATH_DOWNLOAD_LINK = "//a[contains(@class, 'export-url')]"

# Tombol Close/Cancel untuk menutup dialog
XPATH_DIALOG_CLOSE_BTN = "//button[@q-translation='Common.Close' or @ng-click='close()']"

# --- XPATH UNTUK SEARCH BOX DI DALAM DROPDOWN ---
XPATH_SEARCH_LISTBOX = "//input[@data-testid='search-input-field']"