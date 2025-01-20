# Job Scraping and Data Conversion Script

## Overview

This Python script automates the process of scraping job listings from the Indeed platform, converting the raw data into a more usable format, and performing various data cleaning and restructuring tasks. The script utilizes the Apify platform for scraping job data based on predefined keywords and positions, and then processes the scraped data for further analysis or storage.

## Features

- **Job Scraping:** Scrapes job listings from Indeed based on specific job positions (e.g., police officer, deputy sheriff, etc.).
- **Data Cleaning and Transformation:** Performs data cleaning by removing rows with missing data and unwanted entries, renaming columns, extracting and reformatting salary data, and converting job posting dates.
- **Multi-threading:** Uses threading to handle multiple tasks concurrently for faster processing and scraping of multiple job positions.
- **Export and Conversion:** Exports the raw data into CSV files and then processes the data into a more structured and cleaned format.
- **Merged Data:** Combines all modified data into one single CSV file for easier analysis or further processing.

## Prerequisites

- Python 3.x
- Required Python packages:
    - `apify-client`
    - `pandas`
    - `re`
    - `datetime`

Install the required packages using pip:

bash

CopyEdit

`pip install apify-client pandas`

## Setup

1. **API Key:** Make sure to replace the `apiKey` with your own Apify API key. This is necessary for interacting with the Apify platform to scrape job data.
    
2. **Keywords and Dataset Information:** The `keywordsInfo` list contains job positions and their corresponding dataset IDs, which will be used during the scraping process. You can modify or add more positions as required.
    

## Script Breakdown

### 1. Constants

Defines the `apiKey` and a list of job positions with associated dataset IDs.

### 2. Functions

- `scrapData(infoIndex)`: Scrapes job data for a specific job position.
- `getFileNameOfOriginal(infoIndex)`: Returns the original CSV filename for the scraped data.
- `getFileNameOfModified(infoIndex)`: Returns the modified CSV filename after the data has been processed.
- `exportData(infoIndex)`: Exports scraped data to a CSV file.
- `convertData(infoIndex)`: Processes and cleans the scraped data, including salary extraction, date formatting, and text sanitization.

### 3. Main Workflow

- **Scraping and Conversion:** The script runs the scraping and conversion process concurrently using threads. Each job position is processed in parallel for efficiency.
- **Data Merging:** After all positions have been processed, the individual CSV files are merged into a single file called `all-in-one.csv`.

## Running the Script

To run the script, simply execute the Python file:

bash

CopyEdit

`python scrap-using-ApifyClient.py`

The script will:

1. Scrape job data for each position in `keywordsInfo`.
2. Export the raw data to CSV files.
3. Convert and clean the data.
4. Merge all modified data into a single CSV file.

## Output Files

- **Individual CSV files:** Each job position will generate a CSV file named `<index>_<position>.csv`, containing the raw job data.
- **Modified CSV files:** After processing, the script creates modified CSV files with the name `<index>_<position> - modified.csv`.
- **Merged CSV:** After processing all positions, a single CSV file `all-in-one.csv` is created, containing all the cleaned and processed data.

## Notes

- Ensure you have a valid Apify API key for the script to work.
- Modify `keywordsInfo` for different positions or to use other datasets.
- The script uses multi-threading for parallel processing, improving efficiency for scraping multiple job positions.