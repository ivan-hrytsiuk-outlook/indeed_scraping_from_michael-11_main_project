# %%
import pandas as pd

# Load the Excel file
file_path = 'police officer lateral_2024-07-11_15-28-28-271.xlsx'
df = pd.read_excel(file_path)
# Rename columns
df.rename(columns={'externalApplyLink': 'Apply URL', 'location': 'Office location', 'company': 'Company name'
    , 'description': 'Description', 'jobType/0': 'Job type', 'postingDateParsed': 'Date posted'
    , 'positionName': 'Job title', 'companyInfo/companyLogo': 'Company logo', 'companyInfo/url': 'Company URL'}, inplace=True)

# Remove all rows that has empty blanks
df = df.dropna(subset=['Company URL', 'Company logo', 'Apply URL', 'salary'], how='any')
# %%
import re
from datetime import datetime
def extract_salary_data(salary_string):
    # Define regex patterns for different salary schedules
    patterns = {
        'Yearly': [
            r'\$([\d,.]+) - \$([\d,.]+) a year',
            r'Up to \$([\d,.]+) a year',
            r'\$([\d,.]+) a year',
        ],
        'Monthly': [
            r'\$([\d,.]+) - \$([\d,.]+) a month',
            r'Up to \$([\d,.]+) a month',
            r'\$([\d,.]+) a month',
        ],
        'Hourly': [
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
    # Format the date as "7/9/2024"
    formatted_date = date_obj.strftime('%m/%d/%Y').replace('/0', '/')
    return formatted_date

# %%
for x in df.index:
    (df.loc[x, "Salary min"], df.loc[x, "Salary maximum"], df.loc[x, "Salary schedule"]) = extract_salary_data(df.loc[x, "salary"])
    df.loc[x, "Date posted"] = convert_date_format(df.loc[x, "Date posted"])

# %%
# Add a new column with fixed data
df['Salary currency'] = 'USD'
# df['Sticky'] = 'TRUE'
df['Apply email'] = None
df['Location limits'] = 'United States'
# df['Highlighted'] = 'FALSE'
df['Post state'] = 'draft'
df['Post length'] = 45
df['Job location'] = 'onsite'

# Remove columns
# df.drop(columns=['isExpired', 'jobType'], inplace=True)

# Filter and order columns
df = df[["Salary currency", "Apply URL", "Office location", "Apply email", "Company name", "Location limits",
        "Salary min", "Description", "Job type", "Post state", "Date posted", "Post length", "Salary maximum",
         "Job location", "Job title", "Company logo", "Salary schedule", "Company URL"]]


# Save the modified DataFrame to a new Excel file
output_file_path = 'police officer lateral_modified.csv'
df.to_csv(output_file_path, index=False)

print("Converted successfully.")