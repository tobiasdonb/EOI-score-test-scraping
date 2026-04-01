import os

# ==========================================
# KONFIGURASI DIREKTORI & TARGET
# ==========================================
BASE_DIR = os.getcwd()
DOWNLOAD_DIR = os.path.join(BASE_DIR, "DATASET_SCORE_TEST_EOI")
URL = "https://api.dynamic.reports.employment.gov.au/anonap/extensions/hSKLS02_SkillSelect_EOI_Data/hSKLS02_SkillSelect_EOI_Data.html"

HEADLESS = False

# Range bulan yang ingin di-scrape (format: 'MM/YYYY')
# Scraper akan memproses dari END_MONTH (terbaru) mundur ke START_MONTH (terlama)
START_MONTH = '01/2025'  # Bulan terlama
END_MONTH   = '10/2025'  # Bulan terbaru

STATES = ['ACT', 'NSW', 'NT', 'QLD', 'SA', 'TAS', 'VIC', 'WA']
SCORES = ['0', '10', '20'] # 5 tidak dimasukkan sesuai permintaan

# ==========================================
# XPATH SELECTORS
# ==========================================

XPATH_IFRAME = "//iframe[@id='f1']"
XPATH_BTN_NEXT = "//a[@data-qcmd='navNext']"

# --- SETTING PARAMETER (YES/NO) ---
XPATH_BTN_YES_OCCUPATION = "//div[contains(@class, 'qsc-root') and .//span[@title='Occupations']]//button[@data-value='Y']"
XPATH_BTN_YES_POINTS = "//div[contains(@class, 'qsc-root') and .//span[contains(@title, 'Point')]]//button[@data-value='Y']"

# --- FILTER GLOBAL ---
XPATH_DROPDOWN_SELECT = "//button[@data-testid='filterpane-expand-button']"
XPATH_HEADER_VISA_TYPE = "//div[@data-testid='collapsed-title-Visa Type']"
XPATH_HEADER_EOI_STATUS = "//div[@data-testid='collapsed-title-EOI Status']"

XPATH_VISA_189 = "//div[@role='row' and .//div[@title='189PTS Points-Tested Stream']]"
XPATH_VISA_190 = "//div[@role='row' and .//div[@title='190SAS Skilled Australian Sponsored']]"
XPATH_VISA_491_SR = "//div[@role='row' and .//div[@title='491FSR Family Sponsored - Regional']]"
XPATH_VISA_491_ST = "//div[@role='row' and .//div[@title='491SNR State or Territory Nominated - Regional']]"    
XPATH_EOI_SUBMITTED = "//div[@role='row' and .//div[@title='SUBMITTED']]"
XPATH_EOI_INVITED = "//div[@role='row' and .//div[@title='INVITED']]"
XPATH_EOI_LODGED = "//div[@role='row' and .//div[@title='LODGED']]"

XPATH_ACTION_CONFIRM = "//button[@data-testid='actions-toolbar-confirm']"

# --- SMART SEARCH ---
XPATH_SMART_SEARCH_BTN = "//button[@tid='toggleGlobalSearchButton']"
XPATH_SMART_SEARCH_INPUT = "//input[contains(@class, 'lui-search__input')]"
XPATH_SMART_SEARCH_FIRST_RESULT = "(//div[@tid='globalSearch.resultField']//div[contains(@class, 'group-hits')])[1]"

# --- CURRENT SELECTIONS & DROPDOWN ---
XPATH_CURRENT_SELECTION_STATE = "//li[@data-csid='Nominated State']//div[contains(@class, 'current-selection-item-text') and @role='button']"
XPATH_CURRENT_SELECTION_MONTH = "//li[@data-csid='As At Month']//div[contains(@class, 'current-selection-item-text') and @role='button']"
XPATH_CURRENT_SELECTION_ENGLISH = "//li[@data-csid='English Test Score']//div[contains(@class, 'current-selection-item-text') and @role='button']"

XPATH_DROPDOWN_ROW = "//div[@role='row' and .//div[@title='{}']]"
XPATH_SEARCH_LISTBOX = "//input[@data-testid='search-input-field']"

# --- EXPORT DATA ---
XPATH_TABLE_CELL = "(//td[@data-tid='qv-st-cell'])[1]" 
XPATH_EXPORT_DATA = "//*[contains(text(), 'Export data') or contains(text(), 'Export Data')]"
XPATH_DIALOG_EXPORT_BTN = "//button[@tid='table-export']"
XPATH_DOWNLOAD_LINK = "//a[contains(@class, 'export-url')]"
XPATH_DIALOG_CLOSE_BTN = "//button[@q-translation='Common.Close' or @ng-click='close()']"