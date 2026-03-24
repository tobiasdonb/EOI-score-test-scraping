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