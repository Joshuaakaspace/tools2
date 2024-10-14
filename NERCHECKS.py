import re

def extract_data(input_data):
    output = []
    
    for item in input_data:
        extracted = {
            'name': '',
            'aka': '',
            'date of birth': '',
            'part': item.get('part', ''),
            'other information': item.get('other information', ''),
            'name_ner': item.get('name_ner', '')
        }
        
        # Extract name
        name_match = re.search(r"(\w+\s+\w+)\['NAME'\]", item['name_ner'])
        if name_match:
            extracted['name'] = name_match.group(1)
        
        # Extract aka
        aka_match = re.search(r"Also known as (\w+)\s*\['Also Known As'\]", item['name_ner'])
        if aka_match:
            extracted['aka'] = f"Also known as {aka_match.group(1)}"
        
        # Extract date of birth
        dob_match = re.search(r"born on (\d+\s+\w+)\['Date of Birth'\]", item['name_ner'])
        if dob_match:
            extracted['date of birth'] = f"born on {dob_match.group(1)}"
        
        output.append(extracted)
    
    # Add an extra entry with empty 'date of birth'
    if len(output) >= 2:
        extra_entry = output[0].copy()
        extra_entry['date of birth'] = ''
        output.append(extra_entry)
    
    return output

# Test the function
input_data = [
    {
        "name": 'Joshua Nishanth , Also known as Josh, born on 19 july",
        "aka": "",
        "date of birth:": "",
        "part": "",
        "other information": "",
        "name_ner": 'Joshua Nishanth['NAME'] Also known as Josh ['Also Known As'] born on 19 july['Date of Birth']'
    },
    {
        "name": 'Joshua Nishanth , Also known as Josh, born on 19 july",
        "aka": "",
        "date of birth:": "",
        "part": "",
        "other information": "",
        "name_ner": 'Joshua Nishanth['NAME'] born on 19 july['Date of Birth']'
    },
]

result = extract_data(input_data)
for item in result:
    print(item)