import pandas as pd
import re

# Define the keys to look for in the text (as seen in the screenshot)
keys = ['Выделенное название', 'Адрес', 'Дата внесения', 'Прочая информация']

# Function to extract key-value pairs dynamically from each record
def extract_details(text):
    extracted_details = {}

    # Extract key-value pairs for the keys
    for key in keys:
        pattern = re.compile(f'{key}\s*:\s*(.*)')
        match = pattern.search(text)
        if match:
            extracted_details[key] = match.group(1).strip()
        else:
            extracted_details[key] = 'N/A'  # If the key is not found, mark as N/A

    # Additional handling for splitting the name and corporation details
    if 'Выделенное название' in extracted_details:
        # Regex pattern to extract the two parts of the name
        name_pattern = re.compile(r"(.+?)\s+корпорация\s+['\"](.+?)['\"]", re.IGNORECASE)
        name_match = name_pattern.search(extracted_details['Выделенное название'])
        if name_match:
            extracted_details['Corporation Type'] = name_match.group(1).strip()
            extracted_details['Corporation Name'] = name_match.group(2).strip()
        else:
            extracted_details['Corporation Type'] = 'N/A'
            extracted_details['Corporation Name'] = 'N/A'
    
    return extracted_details

# Function to process each row of the dataframe and update columns
def process_dataframe(df):
    # Apply the extraction function to each row in the 'record_data' column
    extracted_data = df['record_data'].apply(extract_details)
    
    # Convert the list of dictionaries into a DataFrame
    extracted_df = pd.DataFrame(extracted_data.tolist())

    # Concatenate the extracted details back to the original dataframe
    df = pd.concat([df, extracted_df], axis=1)
    
    return df

# Sample DataFrame with a 'record_data' column
data = {
    'record_data': [
        """Выделенное название: Торгово-технологическая корпорация 'Тхосон' 
        Адрес: д/о 
        Дата внесения: д/о 
        Прочая информация: Корейская торгово-технологическая корпорация 'Тхосон' является дочерней компанией Корейской горнорудной торговой корпорации."""
    ]
}

# Create DataFrame
df = pd.DataFrame(data)

# Process the DataFrame
df = process_dataframe(df)

# Display the updated DataFrame with the extracted columns
print(df)
