import re

# Sample input data
data = [
    {
        "name": "Joshua Nishanth , Also known as Josh, born on 19 july",
        "aka": "",
        "date of birth": "",
        "part": "",
        "other information": "",
        "name_ner": "Joshua Nishanth['NAME'] Also known as Josh ['Also Known As'] born on 19 july['Date of Birth']"
    },
    {
        "name": "Joshua Nishanth , Also known as Josh, born on 19 july",
        "aka": "",
        "date of birth": "",
        "part": "",
        "other information": "",
        "name_ner": "Joshua Nishanth['NAME'] Also known as Josh ['Also Known As'] born on 19 july['Date of Birth']"
    },
    {
        "name": "Joshua Nishanth , Also known as Josh, born on 19 july",
        "aka": "",
        "date of birth": "",
        "part": "",
        "other information": "",
        "name_ner": "Joshua Nishanth['NAME'] Also known as Josh ['Also Known As'] born on 19 july['Date of Birth']"
    },
    {
        "name": "Joshua Nishanth , Also known as Josh, born on 19 july",
        "aka": "",
        "date of birth": "",
        "part": "",
        "other information": "",
        "name_ner": "Joshua Nishanth['NAME'] Josh ['Also Known As'] 19 july['Date of Birth']"
    }
]

# Function to map the NER tags to their respective fields
def map_ner_to_fields(record):
    name_ner = record['name_ner']
    
    # Extract Name
    name_match = re.search(r"(.+?)\['NAME'\]", name_ner)
    if name_match:
        record['name'] = name_match.group(1).strip()

    # Extract Also Known As (AKA)
    aka_match = re.search(r"(.+?)\['Also Known As'\]", name_ner)
    if aka_match:
        record['aka'] = aka_match.group(1).strip()

    # Extract Date of Birth
    dob_match = re.search(r"(.+?)\['Date of Birth'\]", name_ner)
    if dob_match:
        record['date of birth'] = dob_match.group(1).strip()

    return record

# Apply the function to all records
updated_data = [map_ner_to_fields(record) for record in data]

# Output the updated data
for record in updated_data:
    print(record)
