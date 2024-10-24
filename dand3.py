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
