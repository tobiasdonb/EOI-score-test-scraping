<<<<<<< HEAD
# Core Scraper Engine Documentation (`scraper.py`)

This file contains the `SkillSelectScraper` class, which handles all low-level Selenium browser interactions, waits, DOM manipulations, and file conversions.

## 🛠️ Class Methods Overview

### Initialization & Setup
* **`__init__()`**: Ensures the download directory exists and initializes the Chrome WebDriver.
* **`_setup_driver()`**: Configures Chrome options. It enables eager loading, sets up automated download preferences to bypass popups, and applies the `HEADLESS` setting. It also includes anti-bot evasions using CDP commands.

### Navigation & Interaction
* **`switch_to_main_page()` & `switch_to_dashboard_iframe()`**: Qlik dashboards are heavily nested in iframes. These functions safely switch the driver context back and forth.
* **`click_element(xpath, action_name)`**: A robust custom clicking mechanism. It first attempts to use Selenium's `ActionChains` to perform a natural click. If the element is obscured or stubborn, it gracefully falls back to injecting raw JavaScript `MouseEvent` events directly into the DOM.
* **`search_and_select_item(item_text)`**: Automates typing into Qlik's internal dropdown search boxes and selecting the matching result.

### Data Extraction & File Management
* **`get_available_months()`**: Dynamically scrolls inside the "As At Month" listbox to scrape all available historical months, parses them, and sorts them chronologically.
* **`export_table_data()`**: Automates the complex right-click (`context_click`) export process unique to Qlik Sense. It waits for the server to generate the file and clicks the final download link.
* **`check_file_exists(filename_prefix, month_folder)`**: A utility for the auto-resume feature. Checks if a CSV file already exists in the target directory to prevent duplicate downloads.
* **`wait_and_rename_file(filename_prefix, state_name, month_folder)`**: 
  1. Polls the download directory until the Chrome `.crdownload` temp file disappears.
  2. Grabs the newly downloaded `.xlsx` file.
  3. Uses **Pandas** to read the Excel file, injects missing data columns (`Nominated State` and `As At Month`), and exports it as a clean, lightweight `.csv`.
  4. Deletes the raw `.xlsx` file to save space.
=======
# 🕸️ Core Scraper Engine Documentation (`scraper.py`)

This file contains the `SkillSelectScraper` class, managing all Selenium WebDriver interactions, waits, and file conversions.

## 🛠️ Key Methods

* **`_setup_driver()`**: Configures Chrome to auto-download files to our specific directory without prompting. It also applies anti-bot evasions.
* **`use_smart_search(keyword)`**: A clever workaround to seed the first filters. It clicks the magnifying glass, types the parameter (e.g., 'ACT' or '10'), and selects the first result.
* **`click_element(xpath)`**: A robust clicker that tries Selenium's `ActionChains` first. If the UI is stubborn or overlapping, it forces a click via JavaScript injection.
* **`export_table_data()`**: Automates the right-click (`context_click`) process on the Qlik table, navigates the export dialogs, and waits for the server to generate the Excel file.
* **`wait_and_rename_file()`**: 
    1. Polls the directory until the Chrome `.crdownload` file is finished.
    2. Reads the raw `.xlsx` file using Pandas.
    3. Injects the current loop's `State` and `English Test Score` into the dataframe.
    4. Saves it as a `.csv` inside the corresponding `Score_X` sub-folder and deletes the raw Excel file.
>>>>>>> c58cbca8ac340f98f03ed63994eb5b3ea4597a74
