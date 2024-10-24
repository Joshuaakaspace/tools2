import pandas as pd
import re

# Function to extract Name 1 and Name 2 with improved handling for spaces and formatting
def extract_names(text):
    # Use regex to capture Name 1 and Name 2, allowing for irregular spacing
    name_pattern = re.compile(r'([A-Z\s\-]+),?\s*["«](.+?)["»]', re.IGNORECASE)
    name_match = name_pattern.findall(text.strip())  # Strip leading/trailing spaces
    
    if name_match and len(name_match) >= 1:
        # Return Name 1 and Name 2, stripped of any extra spaces
        return name_match[0][0].strip(), name_match[0][1].strip()
    else:
        # If names are not found, return 'N/A'
        return 'N/A', 'N/A'

# Function to apply name extraction to the 'record_data' column
def extract_names_from_column(df):
    df['Name 1'], df['Name 2'] = zip(*df['record_data'].apply(lambda x: extract_names(str(x))))
    return df

# Post-processing function to remove everything starting from any of the keywords in the list
def clean_up_extra_information(text, keywords):
    # Find the earliest occurrence of any keyword and remove everything starting from that keyword
    earliest_position = len(text)  # Start with the length of the text (i.e., nothing removed yet)
    for keyword in keywords:
        keyword_position = text.find(keyword)
        if keyword_position != -1:  # If the keyword is found in the text
            earliest_position = min(earliest_position, keyword_position)
    
    # Trim the text from the earliest occurrence of any keyword
    return text[:earliest_position].strip() if earliest_position < len(text) else text

# Function to apply post-processing on relevant columns
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

# Load the provided file as a DataFrame
df = pd.read_csv('/mnt/data/file-vdgnzLKQRmFm8uGamBKJOIVb', encoding='ISO-8859-1')

# First, extract names using the improved regex
df = extract_names_from_column(df)

# Then, process the DataFrame by applying the cleanup logic
df = post_process_dataframe(df, columns_to_clean, keywords)

# Display the updated DataFrame with extracted Name 1, Name 2, and cleaned-up fields
import ace_tools as tools; tools.display_dataframe_to_user(name="Processed DataFrame with Fixed Name Extraction and Cleanup", dataframe=df)
