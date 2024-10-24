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
    keys = ['Вымышленные названия', 'Адрес', 'Дата внесения', 'Прочая информация']
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

# Sample DataFrame with 'record_data' column
data = {
    'record_data': [
        """Departament oruzheynoy promyshlennosti, Департамент оружейной промышленности
        Вымышленные названия: Military Supplies Industry Department, MID
        Р.И.К.: д/о
        Адрес: д/о
        Дата внесения в перечень: д/о
        Прочая информация: Департамент оружейной промышленности занимается основными аспектами ракетной программы КНДР. 
        ДОП обеспечивает контроль за разработкой баллистических ракет КНДР, включая ракеты типа «Таеподонг-2». 
        ДОП осуществляет надзор за программами КНДР по производству оружия и НИОКР в области вооружений, включая программу КНДР, 
        связанную с баллистическими ракетами. В подчинении ДОП находятся Второй экономический комитет и Вторая академия естественных наук 
        (также в перечне с августа 2010 года). В последние годы Департамент занимался разработкой МБР «КН-08» на мобильных пусковых установках. 
        ДОП курирует ядерную программу КНДР. Институт ядерного оружия подчинен ДОП."""
    ]
}

# Create DataFrame
df = pd.DataFrame(data)

# Process the DataFrame by applying the extraction to the 'record_data' column
df = process_dataframe_column(df)

# Display the updated DataFrame with extracted columns
import ace_tools as tools; tools.display_dataframe_to_user(name="Processed DataFrame with record_data", dataframe=df)
