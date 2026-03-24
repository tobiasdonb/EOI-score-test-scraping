# ⚙️ Configuration File Documentation (`config.py`)

This file acts as the central brain for all static variables, settings, target lists, and XPath locators.

## 🎯 Target Variables
* **`MONTHS`, `STATES`, `SCORES`**: The primary lists the bot will iterate through. *Note: Score '5' is intentionally excluded per initial requirements.*
* **`DOWNLOAD_DIR`**: Set to create a specific folder named `DATASET_SCORE_TEST_EOI`.

## 🔍 XPath Selectors
Categorized into logical groups:
1. **Iframe & Navigation**: For moving between dashboard pages.
2. **Parameter Settings**: To click 'YES' for Occupations and Points.
3. **Global Filters**: Checkboxes for specific Visa Types (189, 190, 491) and Statuses (Submitted, Invited, Lodged).
4. **Smart Search**: Locators to type and select initial parameters globally.
5. **Current Selections**: Targets the top active bar to quickly swap States and Scores during the loop.
6. **Export Data**: The precise locators to trigger Qlik's native context menu (Right-Click -> Export data -> Export -> Click Download Link).