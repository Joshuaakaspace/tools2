import json

# Your original list
data_list = [
    ['{\n "name":"jack", \n "dob":"", \n "pob":"" }'],
    ['{\n "name":"mack", \n "dob":"", \n "pob":"" }'],
    ['{\n "name":"track", \n "dob":"", \n "pob":"" }'],
    ['{\n "name":"hag", \n "dob":"", \n "pob":"" }'],
    ['{\n "name":"Sag", \n "dob":"", \n "pob":"" }']
]

# Function to parse and extract data
def extract_data(data_list):
    cleaned_data = []
    for item in data_list:
        # Load the JSON string
        data = json.loads(item[0])
        # Extract the dictionary
        cleaned_data.append({
            "name": data["name"],
            "dob": data["dob"],
            "pob": data["pob"]
        })
    return cleaned_data

# Get the cleaned data
cleaned_data = extract_data(data_list)
print(cleaned_data)

