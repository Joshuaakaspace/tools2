import pandas as pd
import re

# Function to extract Name 1 and Name 2 with improved handling for spaces and formatting
def extract_names(text):
    # Use regex to capture Name 1 and Name 2, allowing for irregular spacing and missing punctuation
    name_pattern = re.compile(r'([A-Z\s\-]+)[,\s]*["«](.+?)["»]', re.IGNORECASE)
    name_match = name_pattern.findall(text.strip())  # Strip leading/trailing spaces
    
    if name_match and len(name_match) >= 1:
        # Return Name 1 and Name 2, stripped of any extra spaces
        return name_match[0][0].strip(), name_match[0][1].strip()
    else:
        # If names are not found, return 'N/A'
        return 'N/A', 'N/A'

# Function to apply name extraction to the 'record_data' column
def extract_names_from_column(df):
    # Ensure the 'record_data' column exists
    if 'record_data' in df.columns:
        df['Name 1'], df['Name 2'] = zip(*df['record_data'].apply(lambda x: extract_names(str(x))))
    return df

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

# Sample DataFrame for demonstration (replace this with your actual DataFrame)
# This DataFrame assumes you have the relevant columns to apply the cleanup
data = {
    'record_data': ['TORGOVO-TEKHNOLOGICHESKAYA, «ТХОСОН»', 'GENERALNAYA EKONOMICHESKAYA I TORGOVAYA KORPORATSIYA, «СИНВАН»'],
    'Обращение': ['д/о Должность: пример текста', 'д/о'],
    'Адрес': ['улица пример Адрес', 'д/о'],
    'Дата внесения в перечень': ['д/о', 'д/о'],
    'Дата рождения': ['1970-01-01', '1990-05-05 Прочая информация: дополнительная информация'],
    'Место рождения': ['д/о', 'место Прочая информация: пример'],
    'Прочая информация': ['д/о Прочая информация: пример', 'Прочая информация: удалить это'],
    'Гражданство': ['д/о', 'д/о'],
    'Паспорт №': ['1234567890 Прочая информация: дополнительное описание', 'д/о'],
    'Национальный идентификационный номер': ['д/о', 'номер Прочая информация: информация']
}

# Create DataFrame
df = pd.DataFrame(data)

# First, extract names using the improved regex
df = extract_names_from_column(df)

# Then, process the DataFrame by applying the enhanced cleanup logic
df = post_process_dataframe(df, columns_to_clean, keywords)

# Display the cleaned DataFrame
print("Post-Processed DataFrame with Name 1 and Name 2 Extraction:")
print(df)
