import json
import re

# Your list with potential multiple JSON objects in a single string
data_list = [
    ['{\n "name":"jack", \n "DOB":"1990-01-01", \n "POB":"City", "position":"Manager", "rank":"Senior", "nationality":"Country", "gender":"Male", "passport_number":"123456789", "reasons":"Employment", "date_of_listing":"2023-01-01", "other_details":"None" },{\n "name":"jack", \n "DOB":"1990-01-01", \n "POB":"City", "position":"Manager", "rank":"Senior", "nationality":"Country", "gender":"Male", "passport_number":"123456789", "reasons":"Employment", "date_of_listing":"2023-01-01", "other_details":"None" }'],
    ['{\n "name":"mack", \n "DOB":"1991-02-02", \n "POB":"City" }'],
    ['{\n "name":"track", \n "DOB":"1992-03-03", \n "POB":"City" }'],
    ['{\n "name":"hag", \n "DOB":"1993-04-04", \n "POB":"City" }'],
    ['{\n "name":"Sag", \n "DOB":"1994-05-05", \n "POB":"City" }']
]

# Function to extract JSON objects from strings
def extract_json_objects(json_string):
    # Updated pattern to include all fields
    pattern = r'\{\s*"\s*name"\s*:\s*"[^"]*"\s*,\s*"\s*DOB"\s*:\s*"[^"]*"\s*,\s*"\s*POB"\s*:\s*"[^"]*"\s*,\s*"\s*position"\s*:\s*"[^"]*"\s*,\s*"\s*rank"\s*:\s*"[^"]*"\s*,\s*"\s*nationality"\s*:\s*"[^"]*"\s*,\s*"\s*gender"\s*:\s*"[^"]*"\s*,\s*"\s*passport_number"\s*:\s*"[^"]*"\s*,\s*"\s*reasons"\s*:\s*"[^"]*"\s*,\s*"\s*date_of_listing"\s*:\s*"[^"]*"\s*,\s*"\s*other_details"\s*:\s*"[^"]*"\s*\}'
    matches = re.findall(pattern, json_string)
    return matches

# Function to parse and extract data
def extract_data(data_list):
    cleaned_data = []
    for item in data_list:
        json_strings = extract_json_objects(item[0])
        for json_string in json_strings:
            try:
                # Load the JSON string
                data = json.loads(json_string)
                # Extract the dictionary
                cleaned_data.append(data)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                print(f"Problematic data: {json_string}")
    return cleaned_data

# Get the cleaned data
cleaned_data = extract_data(data_list)
print(cleaned_data)
