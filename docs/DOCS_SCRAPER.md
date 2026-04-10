# 🕷️ Scraper Class Documentation (`scraper.py`)

The `SkillSelectScraper` class is a high-level wrapper around Selenium, specifically designed to handle the complexities of the Qlik Sense UI.

## 🏗️ Initialization & Setup

- **`__init__(worker_id)`**: Initializes the WebDriver and creates a unique temporary download directory for the worker to avoid file collisions during parallel downloads.
- **`_setup_driver()`**: Configures Chrome with optimized settings (headless support, image blocking, eager page load strategy, and anti-bot bypass).

## 🖱️ Browser Interactions

- **`click_element()`**: A robust clicking method that uses `ActionChains` with a fallback to `JS MouseEvent` injection if standard clicks are intercepted by Qlik's dynamic overlays.
- **`search_and_select_item()`**: Inputs text into a dropdown's search box and selects the matching result.
- **`uncheck_selected_rows()`**: A specialized utility that scrolls through a listbox and unchecks all items except an optional excluded one. This is critical for maintaining clean filters in Qlik.
- **`get_available_months()`**: Scans the "As At Month" listbox using automatic scrolling to extract all available data points dynamically.

## 📊 Data Export & Handling

- **`export_table_data()`**: Automates the right-click context menu on the main data table, selects "Export data," and triggers the generation of the Excel file.
- **`wait_and_rename_file()`**: 
    1. Polls the worker's download directory until the Chrome `.crdownload` file is finished.
    2. Identifies the most recent `.xlsx` file.
    3. Reads the file into a Pandas DataFrame.
    4. **Data Injection**: Dynamically adds `Nominated State`, `English Test Score`, and `As At Month` columns to ensure context is preserved.
    5. Saves the final result as a `.csv` in the primary `DATASET` folder with a structured name.
    6. Deletes the original Excel file to maintain a clean workspace.

## 🛡️ Anti-Bot & Reliability
- Uses **CDP (Chrome DevTools Protocol)** commands to hide the `navigator.webdriver` flag.
- Implements various wait strategies (`WebDriverWait`) and fallback JS execution to handle the high latency and dynamic nature of Qlik dashboards.
