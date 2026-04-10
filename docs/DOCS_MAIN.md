# 🚀 Main Scraper Logic Documentation (`main.py`)

The `main.py` script serves as the orchestrator for the entire scraping process. It handles parallelization, task distribution, and the core worker routine.

## 🧵 Multi-Threaded Architecture

The scraper uses Python's `ThreadPoolExecutor` to run multiple browser instances simultaneously. 
- **Strategy**: One worker per English Test Score (0, 10, 20).
- **Task Distribution**: Months are divided among the workers.
- **Staggered Start**: To prevent overloading the target server or the local system, workers start with a slight delay between each other.

## 🛠️ Key Components

### 1. Helper Functions
- **`generate_month_range()`**: Converts the start/end month strings from `config.py` into a sorted list of month-year combinations.
- **`setup_bot_environment()`**: Performs the initial navigation, bypasses the page loader, sets up primary filters, and navigates to the final data table.

### 2. Worker Routine (`worker_routine`)
Each worker thread follows this cycle:
1. **Initialize Browser**: Creates a unique `SkillSelectScraper` instance with its own download directory.
2. **Environment Setup**: Runs the common setup routine.
3. **Task Loop**: Iterates through assigned `(month, score)` tasks:
    - **Switch Month/Score**: Efficiently updates the filters in the "Current Selections" bar.
    - **Resume Check**: Skips the task if the target file already exists in the `DATASET` folder.
    - **State Loop**: Iterates through all target States:
        - Switches the active state.
        - Triggers the Qlik "Export data" menu.
        - Waits for the download and converts the file to CSV.
4. **Cleanup**: Closes the browser after all tasks are completed.

### 3. Entry Point (`main`)
The main function calculates the tasks, chunks them for the available workers, and kicks off the multi-threaded execution.
