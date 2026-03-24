# 📖 Australian SkillSelect EOI Scraper (English Score & State Edition)

An automated web scraping tool built with Python and Selenium to extract Expression of Interest (EOI) data from the official Australian Department of Employment's Qlik Sense dashboard. 

This specific version is engineered to loop through different **English Test Scores** (0, 10, 20) and **Australian States**, automating the complex process of filtering, rendering, and downloading the data directly from the dynamic Qlik iframe.

## ✨ Features

* **Smart Search Initialization**: Utilizes the Qlik Smart Search feature to smoothly initialize the first State and Score filters without breaking the DOM structure.
* **Double Looping Extraction**: Systematically iterates through an outer loop of English Test Scores and an inner loop of States to gather highly granular data.
* **Auto-Resume Capability**: Checks if a file for a specific State and Score already exists in the destination folder. If the bot crashes, it will resume right where it left off!
* **Automated Data Transformation**: Uses Pandas to read the raw exported `.xlsx` files, automatically injects the `English Test Score` and `State` columns for context, and converts them to lightweight `.csv` files.
* **Structured Output**: Automatically categorizes downloaded datasets into specific sub-folders based on their English Score category.

## 📂 Output Structure

The script automatically generates a `DATASET_SCORE_TEST_EOI` folder. Inside, it categorizes the data by the English Score:

```text
📁 DATASET_SCORE_TEST_EOI/
├── 📁 Score_0/
│   ├── EOI_ACT_SCORE_0_03_2026_1710000000.csv
│   ├── EOI_NSW_SCORE_0_03_2026_1710000010.csv
├── 📁 Score_10/
│   ├── EOI_ACT_SCORE_10_03_2026_1710000090.csv
│   └── ...
```

# 🚀 Installation & Setup Guide

Follow these steps to set up the environment and run the scraper on your local machine.

## 📋 Prerequisites

To run this scraper successfully, you need:
* **Python 3.8+** installed on your machine.
* **Google Chrome** browser installed.

## 🛠️ Step-by-Step Installation

### 1. Clone the Repository
Clone this repository [https://github.com/babiguling12/EOI-score-test-scraping.git](https://github.com/babiguling12/EOI-score-test-scraping.git) to your local machine using Git:

```bash
git clone https://github.com/babiguling12/EOI-score-test-scraping.git
cd EOI-score-test-scraping
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