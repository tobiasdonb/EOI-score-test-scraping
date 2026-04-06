<<<<<<< HEAD
# Main Execution Flow Documentation (`main.py`)

This is the entry point of the application. It imports the `SkillSelectScraper` and the `config`, orchestrating the step-by-step logic required to extract the data systematically.

## 🔄 Workflow Sequence

1. **Dashboard Initialization**: Opens the target URL and waits for the initial page loader to disappear.
2. **Parameter Configuration**: Navigates into the dashboard iframe and sets the required base parameters (Occupation = Yes, State = Yes, Points = No).
3. **Applying Global Filters**: Expands the Qlik filter panes to select specific Visa Types and EOI Statuses, locking these parameters globally for the session.
4. **Table Preparation**: Moves to the final data table view and locks in the first state (e.g., ACT) to prepare the UI for looping.
5. **Dynamic Month Extraction**: Reads the top "Current Selections" bar to scrape all available months. Falls back to `config.MONTHS` if extraction fails.
6. **Nested Extraction Loop (Months x States)**:
   * **Outer Loop (Months)**: Iterates through each extracted month, switching the global timeline parameter.
   * **Inner Loop (States)**: Iterates through the list of Australian states.
   * **Auto-Resume Check**: Before switching UI elements, it checks if the state/month CSV already exists. If yes, it skips to the next iteration, saving massive amounts of time.
   * **Download Execution**: If the data is missing, it updates the state filter, triggers the right-click export, and waits for the CSV conversion.
7. **Master Data Generation**: At the end of each month's loop, it selects *ALL* states simultaneously and downloads a compiled "Master Data" file for that specific month.
8. **UI Reset**: Carefully resets the Qlik active filters back to the first state before moving on to the next month to prevent selection overlapping.
9. **Cleanup**: Closes the browser cleanly once all loops are complete.
=======
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
>>>>>>> c58cbca8ac340f98f03ed63994eb5b3ea4597a74
