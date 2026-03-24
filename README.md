# Australian SkillSelect EOI Data Scraper

An automated web scraping tool built with Python and Selenium to extract Expression of Interest (EOI) data from the official Australian Department of Employment's Qlik Sense dashboard. 

Because Qlik Sense dashboards are highly dynamic and notoriously difficult to scrape via traditional HTTP requests, this bot automates the browser interactions—navigating iframes, applying complex filters, extracting dynamic dropdowns, and utilizing the native "Right-Click -> Export" functionality to download the data.

## ✨ Features

* **Dynamic Data Extraction**: Automatically scrolls and extracts available months directly from the dashboard UI, with a fallback list just in case.
* **Smart Export & Conversion**: Triggers the Qlik Sense right-click context menu to export data as `.xlsx`, waits for the download, and automatically converts it to `.csv` using Pandas for lighter storage and easier data analysis.
* **Auto-Resume Capability**: Checks if a specific file for a state and month already exists. If the script stops or fails, it will resume exactly where it left off without re-downloading existing data.
* **Data Enrichment**: Automatically injects `Nominated State` and `As At Month` columns into the final CSV files since the raw exported table sometimes lacks this context.
* **Organized Storage**: Automatically categorizes downloaded datasets into structured directories (`DATASET/YYYY/MM_YYYY/`).
* **Headless Support**: Can run quietly in the background (Headless Chrome) or visually for debugging purposes.

## 📂 Output Structure

The scraper automatically organizes the exported data by year and month. The output will look like this:

```text
📁 DATASET/
├── 📁 2026/
│   ├── 📁 01_2026/
│   │   ├── Data_EOI_ACT_01_2026_1710000000.csv
│   │   ├── Data_EOI_NSW_01_2026_1710000010.csv
│   │   ├── ...
│   │   └── MASTER_DATA_EOI_01_2026_1710000080.csv
│   ├── 📁 02_2026/
│   │   ├── Data_EOI_ACT_02_2026_1710000090.csv
│   │   └── ...
```

# 🚀 Installation & Setup Guide

Follow these steps to set up the environment and run the scraper on your local machine.

## 📋 Prerequisites

To run this scraper successfully, you need:
* **Python 3.8+** installed on your machine.
* **Google Chrome** browser installed. *(Note: Selenium Manager handles the ChromeDriver automatically in modern Selenium versions).*

## 🛠️ Step-by-Step Installation

### 1. Clone the Repository
First, clone this repository to your local machine using Git:

```bash
git clone [https://github.com/babiguling12/EOI-SkillSelect-Scraping.git](https://github.com/babiguling12/EOI-SkillSelect-Scraping.git)
cd EOI-SkillSelect-Scraping
```

### 2. Create a Virtual Environment (Recommended)
It is highly recommended to use a virtual environment to isolate the project dependencies and avoid conflicts with other Python projects.

**For Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**For macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Once your virtual environment is activated, install all the required libraries using `pip`. 

Ensure you have a `requirements.txt` file with the following content:
```text
selenium>=4.10.0
pandas>=2.0.0
openpyxl>=3.1.2
```

Run this command to install them:
```bash
pip install -r requirements.txt
```

### 4. Run the Scraper
With your virtual environment activated, start the scraping process by running:

```bash
python main.py
```

Sit back and let the bot navigate the dashboard. If you set `HEADLESS = False` in `config.py`, you will see the Chrome browser opening and performing the actions automatically.