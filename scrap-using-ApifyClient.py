# %% 1. Constants
apiKey = "apify_api_a46mgbdUMWrHuZjmycf4xdH6Yyvi4H1v4GpA"
keywordsInfo = [
    {"position": "police officer lateral", "datasetId": "NpGqlIv2EeCHg0yiA"},  # KBTeiDsOxsrgNqHCt, C2TuLsBaxOfngY7Mj
    {"position": "police officer basic", "datasetId": "mrtHKK5vUpb8C49FZ"},  # EnfyAq6CXSdyj3NP2
    {"position": "sheriffs deputy", "datasetId": "p3AL7UGssS7z9IrqG"},  # kJ067cxgFfbkwIfAm
    {"position": "police recruit", "datasetId": "jYwM1hIUZFKUt1Boe"},
    {"position": "police officer recruit", "datasetId": "4ZZt3UiikgqJ0EUux"},
    {"position": "sheriff", "datasetId": "YH4chT8K3yoF8Mo5A"},
    {"position": "deputy sheriff", "datasetId": "vhgHiayWW3tTae8M1"},
    {"position": "border patrol", "datasetId": "7trltRmc9yFf2TiMc"},
    {"position": "police lateral", "datasetId": "gEfe5SYg4xgfMp4ag"},
    {"position": "customs agent", "datasetId": "lLHEtwvDo0xhRRtsP"},
    {"position": "police officer", "datasetId": "1BZQ04ufy33ivhh1q"},
    {"position": "patrol officer", "datasetId": "7SGgDg2fjLdtIawMw"},
]

# %% 1 => 2. Functions
import threading

threadLock = threading.Lock()


def scrapData(infoIndex):
    threadLock.acquire()
    position = keywordsInfo[infoIndex]['position']
    print(infoIndex, position, 'will be started')
    threadLock.release()

    from apify_client import ApifyClient
    client = ApifyClient(apiKey)
    run_input = {
        "position": position,
        "country": "US",
        # "maxItems": 19000,
        "maxConcurrency": 15,
        "parseCompanyDetails": True,
        "saveOnlyUniqueItems": True,
        "followApplyRedirects": True,
    }
    run = client.actor("misceres/indeed-scraper").call(run_input=run_input)

    threadLock.acquire()
    keywordsInfo[infoIndex]['datasetId'] = run["defaultDatasetId"]
    print(keywordsInfo[infoIndex])
    threadLock.release()


def getFileNameOfOriginal(infoIndex):
    return str(infoIndex) + "_" + keywordsInfo[infoIndex]['position'] + '.csv'


def getFileNameOfModified(infoIndex):
    return str(infoIndex) + "_" + keywordsInfo[infoIndex]['position'] + ' - modified.csv'


def exportData(infoIndex):
    threadLock.acquire()
    position = keywordsInfo[infoIndex]["position"]
    datasetId = keywordsInfo[infoIndex]["datasetId"]
    print(infoIndex, position, datasetId, 'will be started')
    threadLock.release()

    from apify_client import ApifyClient
    client = ApifyClient("apify_api_a46mgbdUMWrHuZjmycf4xdH6Yyvi4H1v4GpA")
    ret = client.dataset(datasetId).get_items_as_bytes(item_format='csv')
    # Opening a file
    fileName = getFileNameOfOriginal(infoIndex)
    file = open(fileName, 'wb')
    file.write(ret)
    file.close()

    threadLock.acquire()
    print(fileName + ' is created')
    threadLock.release()


def convertData(infoIndex):
    import pandas as pd
    import re
    from datetime import datetime

    threadLock.acquire()
    position = keywordsInfo[infoIndex]["position"]
    originalFileName = getFileNameOfOriginal(infoIndex)
    modifiedFileName = getFileNameOfModified(infoIndex)
    threadLock.release()

    df = pd.read_csv(originalFileName)
    # Rename columns
    df.rename(columns={'externalApplyLink': 'Apply URL', 'location': 'Office location', 'company': 'Company name'
        , 'description': 'Description', 'descriptionHTML': 'DescriptionHTML', 'jobType/0': 'Job type',
                       'postingDateParsed': 'Date posted'
        , 'positionName': 'Job title', 'companyInfo/companyLogo': 'Company logo', 'companyInfo/url': 'Company URL'},
              inplace=True)

    # Remove all rows that has empty blanks
    df = df.dropna(subset=['Company URL', 'Company logo', 'Apply URL', 'salary'], how='any')

    # Update(Reformat) some values
    def extract_salary_data(salary_string):
        # Define regex patterns for different salary schedules
        patterns = {
            'yearly': [
                r'\$([\d,.]+) - \$([\d,.]+) a year',
                r'Up to \$([\d,.]+) a year',
                r'\$([\d,.]+) a year',
            ],
            'monthly': [
                r'\$([\d,.]+) - \$([\d,.]+) a month',
                r'Up to \$([\d,.]+) a month',
                r'\$([\d,.]+) a month',
            ],
            'hourly': [
                r'\$([\d,.]+) - \$([\d,.]+) an hour',
                r'Up to \$([\d,.]+) an hour',
                r'\$([\d,.]+) an hour',
            ],
        }

        for schedule, patterns_list in patterns.items():
            for pattern in patterns_list:
                match = re.search(pattern, salary_string)
                if match:
                    if "Up to" in salary_string or len(match.groups()) == 1:
                        salary_min = 0.0
                        salary_max = float(match.group(1).replace(',', ''))
                    else:
                        salary_min = float(match.group(1).replace(',', ''))
                        salary_max = float(match.group(2).replace(',', ''))
                    return salary_min, salary_max, schedule

        # Return None if no match is found
        return None, None, None

    def convert_date_format(date_string):
        # Parse the input date string
        date_obj = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%fZ')
        # Format the date as "2024-07-09"
        formatted_date = date_obj.strftime('%Y-%m-%d')
        return formatted_date

    def removeSpecialChars(text):
        return (text.encode('utf-8')
                .replace(b'\xe2\x80\x9c', b'"')
                .replace(b'\xe2\x80\x9d', b'"')
                .replace(b'\xe2\x80\x98', b"'")
                .replace(b'\xe2\x80\x99', b"'")
                .replace(b'\xe2\x80\x93', b"-")
                .replace(b'\xe2\x80\x94', b"-")
                .decode('utf-8').replace("\n", "")
                .replace("\r", ""))

    shouldRemoveIndexes = []
    for x in df.index:
        if ('https://www.indeed.com/' in df.loc[x, "Apply URL"] or
                re.search('security', df.loc[x, "Job title"], re.IGNORECASE)):
            shouldRemoveIndexes.append(x)
        else:
            if df.loc[x, "Job type"] == 'Full-time':
                df.loc[x, "Job type"] = 'fulltime'
            elif df.loc[x, "Job type"] == 'Part-time':
                df.loc[x, "Job type"] = 'parttime'
            else:
                shouldRemoveIndexes.append(x)
            (df.loc[x, "Salary min"], df.loc[x, "Salary maximum"], df.loc[x, "Salary schedule"]) = extract_salary_data(
                df.loc[x, "salary"])
            df.loc[x, "Date posted"] = convert_date_format(df.loc[x, "Date posted"])
            df.loc[x, "Description"] = removeSpecialChars(df.loc[x, "Description"])
            df.loc[x, "DescriptionHTML"] = removeSpecialChars(df.loc[x, "DescriptionHTML"])
            df.loc[x, "Job title"] = removeSpecialChars(df.loc[x, "Job title"])

    df = df.drop(shouldRemoveIndexes)

    # Add a new column with fixed data
    df['Salary currency'] = 'USD'
    # df['Sticky'] = 'TRUE'
    df['Apply email'] = None
    df['Location limits'] = 'United States'
    # df['Highlighted'] = 'FALSE'
    df['Post state'] = 'draft'
    df['Post length'] = 45
    df['Job location'] = 'onsite'

    # Filter and order columns
    df = df[["Salary currency", "Apply URL", "Office location", "Apply email", "Company name", "Location limits",
             "Salary min", "Description", "DescriptionHTML", "Job type", "Post state", "Date posted", "Post length",
             "Salary maximum",
             "Job location", "Job title", "Company logo", "Salary schedule", "Company URL"]]

    # Save the modified DataFrame to a new Excel file
    df.to_csv(modifiedFileName, index=False)

    threadLock.acquire()
    print(modifiedFileName + ' is created')
    threadLock.release()


if __name__ == '__main__':
    # %% 2 => 3-1. Scrap(Or export, convert) data using multi-threads
    threads = []
    for index in range(0, len(keywordsInfo)):  # len(keywordsInfo)
        # threads.append(threading.Thread(target=scrapData, args=(index,)))
        # threads.append(threading.Thread(target=exportData, args=(index,)))
        threads.append(threading.Thread(target=convertData, args=(index,)))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    # %% 3-1 => 3-2. Merge all modified data to one file
    import pandas as pd

    dfArray = []
    for index in range(len(keywordsInfo)):
        dfArray.append(pd.read_csv(getFileNameOfModified(index)))
    df = pd.concat(dfArray)
    df.to_csv('all-in-one.csv', index=False)
    print('completed')
