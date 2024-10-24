
# Reloading necessary modules and running the entire block of code

import pandas as pd
import re

# Function to extract details from the text in the 'record_data' column
def extract_details_from_record_data(text):
    extracted_details = {}

    # Adjust regex to capture Name 1 (Latin script) and Name 2 (Cyrillic script)
    name_pattern = re.compile(r'([A-Za-z\s\-]+),\s+([А-Яа-я\s\-]+)', re.IGNORECASE)
    name_match = name_pattern.findall(text)
    if name_match and len(name_match) >= 1:
        extracted_details['Name 1'] = name_match[0][0].strip()  # First name in Latin script
        extracted_details['Name 2'] = name_match[0][1].strip()  # Second name in Cyrillic script
    else:
        extracted_details['Name 1'] = 'N/A'
        extracted_details['Name 2'] = 'N/A'

    # Extract other key-value pairs
    keys = [
        'Вымышленные названия', 'Адрес', 'Дата внесения в перечень', 'Прочая информация',
        'Обращение', 'Должность', 'Дата рождения', 'Место рождения',
        'На основании достоверных источников также известен как',
        'На основании менее достоверных источников также известен как',
        'Гражданство', 'Паспорт №', 'Национальный идентификационный номер', 'Р.И.К.'
    ]
    
    for key in keys:
        pattern = re.compile(f'{key}\s*:\s*(.*)')
        match = pattern.search(text)
        if match:
            extracted_details[key] = match.group(1).strip()
        else:
            extracted_details[key] = 'N/A'
    
    return extracted_details

# Function to process the dataframe and apply extraction on the 'record_data' column
def process_dataframe_column(df):
    # Apply the extraction function to each row in the 'record_data' column
    extracted_data = df['record_data'].apply(extract_details_from_record_data)
    
    # Convert the list of dictionaries into a DataFrame
    extracted_df = pd.DataFrame(extracted_data.tolist())

    # Concatenate the extracted details back to the original dataframe
    df = pd.concat([df, extracted_df], axis=1)
    
    return df

# Load the provided file with encoding handling
df = pd.read_csv('/mnt/data/file-Y6uygD7pmP8iAC09zscjXLPO', encoding='ISO-8859-1')  # Using a different encoding

# Process the DataFrame by applying the extraction to the 'record_data' column
df = process_dataframe_column(df)

# Display the updated DataFrame with extracted columns
# Function to remove everything starting from any of the keywords in the list
def clean_up_extra_information(text, keywords):
    # Track the earliest occurrence of any keyword
    earliest_position = len(text)  # Start with the length of the text (i.e., nothing removed yet)
    for keyword in keywords:
        keyword_position = text.find(keyword)
        if keyword_position != -1:  # If the keyword is found in the text
            earliest_position = min(earliest_position, keyword_position)
    
    # Trim the text from the earliest occurrence of any keyword
    return text[:earliest_position].strip() if earliest_position < len(text) else text

# Function to apply the complete cleanup across the specified columns
def post_process_dataframe(df, columns, keywords):
    for column in columns:
        df[column] = df[column].apply(lambda x: clean_up_extra_information(str(x), keywords))
    return df

# Keywords that, when found, will result in trimming the text from that point onward
keywords = [
    'Должность', 'Обращение', 'Адрес', 'Дата внесения', 'Дата рождения', 
    'Прочая информация', 'Место рождения', 'На основании достоверных источников', 
    'На основании менее достоверных источников', 'Паспорт №', 'Национальный идентификационный номер'
]

# Relevant columns where the cleanup is needed
columns_to_clean = [
    'Обращение', 'Адрес', 'Дата внесения в перечень', 'Дата рождения', 
    'Место рождения', 'Прочая информация', 'Гражданство', 'Паспорт №', 
    'Национальный идентификационный номер'
]

# Process the DataFrame by applying the enhanced cleanup logic
df = post_process_dataframe(df, columns_to_clean, keywords)

# Display the updated DataFrame with completely cleaned-up fields
tools.display_dataframe_to_user(name="Post-Processed DataFrame with Full Cleanup", dataframe=df)
