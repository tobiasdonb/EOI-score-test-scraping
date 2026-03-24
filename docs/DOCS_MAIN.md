# 🚦 Main Execution Flow (`main.py`)

This orchestrator script ties the configuration and scraper engine together into a logical sequence.

## 🔄 The Pipeline

1. **Initialization**: Opens the dashboard and waits for the initial loader to disappear.
2. **Parameter Injection**: Sets Occupation and Points to YES.
3. **Global Filtering**: Locks in Visa Types and EOI Statuses.
4. **Smart Seeding**: Uses the Smart Search bar to apply the very first State and English Score to the dashboard before moving to the final table.
5. **Month Lock**: Scrapes available months, picks the latest one, and locks it in.
6. **The Double Loop**:
    * **Outer Loop (Scores)**: Iterates through 0, 10, and 20. Uses the "Current Selections" top bar to swap scores.
    * **Inner Loop (States)**: Iterates through all Australian states.
    * **Auto-Skip**: Before downloading, it checks if `EOI_[State]_SCORE_[Score]...csv` exists. If yes, it skips to save time.
    * **Extraction**: Triggers the export, waits for the file, cleans it, and loops again.
7. **Cleanup**: Gracefully closes the browser after completing the matrix.