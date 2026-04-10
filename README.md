# 📖 Australian SkillSelect EOI Scraper (Asynchronous Edition)

An automated web scraping tool built with Python and Selenium to extract Expression of Interest (EOI) data from the official Australian Department of Employment's Qlik Sense dashboard. 

This version is engineered for **High-Performance Asynchronous Scraping**, utilizing multiple browser instances to loop through different **English Test Scores** (0, 10, 20), **Australian States**, and **Months** simultaneously.

## ✨ Features

* **Multi-Threaded Performance**: Leverages `ThreadPoolExecutor` to run multiple browser workers in parallel, significantly reducing total scraping time.
* **Smart Search Initialization**: Utilizes the Qlik Smart Search feature to smoothly initialize the first State and Score filters without breaking the DOM structure.
* **Dynamic Data Extraction**: Automatically scrolls and extracts available months directly from the dashboard UI.
* **Auto-Resume Capability**: Checks if a file for a specific State, Score, and Month already exists. If the bot crashes, it will resume right where it left off!
* **Automated Data Transformation**: Uses Pandas to read raw exported `.xlsx` files, injects `English Test Score`, `Nominated State`, and `As At Month` columns, and converts them to lightweight `.csv`.
* **Organized Storage**: Automatically categorizes downloaded datasets into structured directories (`DATASET/YYYY/MM_YYYY/`).
* **Headless Support**: Can run quietly in the background (Headless Chrome) or visually for debugging.

## 📂 Output Structure

The scraper automatically organizes the exported data by year and month. The output will look like this:

```text
📁 DATASET/
├── 📁 2025/
│   ├── 📁 01_2025/
│   │   ├── EOI_ACT_SCORE_0_01_2025_1710000000.csv
│   │   ├── EOI_NSW_SCORE_10_01_2025_1710000010.csv
│   │   ├── ...
```

# 🚀 Installation & Setup Guide

Follow these steps to set up the environment and run the scraper on your local machine.

## 📋 Prerequisites

To run this scraper successfully, you need:
* **Python 3.8+** installed on your machine.
* **Google Chrome** browser installed. *(Note: Selenium Manager handles the ChromeDriver automatically).*

## 🛠️ Step-by-Step Installation

### 1. Clone the Repository
Clone this repository to your local machine:

```bash
git clone https://github.com/babiguling12/EOI-score-test-scraping.git
cd EOI-score-test-scraping
```

### 2. Create a Virtual Environment (Recommended)
**For Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Scraper
```bash
python main.py
```

Sit back and let the bot navigate the dashboard. If you set `HEADLESS = False` in `config.py`, you will see the Chrome browsers opening and performing actions in parallel.