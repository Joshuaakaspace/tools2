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
        
        name_ner = item['name_ner']
        
        # Extract information dynamically based on tags
        tags = re.findall(r'\[\'([^\']+)\'\]', name_ner)
        for i, tag in enumerate(tags):
            if i == 0:  # First tag is always NAME
                extracted['name'] = name_ner[:name_ner.index(f"['{tag}']")].strip()
            else:
                start = name_ner.index(f"['{tags[i-1]}']") + len(f"['{tags[i-1]}']")
                end = name_ner.index(f"['{tag}']")
                value = name_ner[start:end].strip()
                
                if tag == 'ALSO_KNOWN_AS':
                    extracted['aka'] = value
                elif tag == 'DATE_OF_BIRTH':
                    extracted['date of birth'] = value
        
        output.append(extracted)
    
    return output

# Test the function
input_data = [
    {
        "name": "Joshua Nishanth , Also known as Josh, born on 19 july",
        "aka": "",
        "date of birth:": "",
        "part": "",
        "other information": "",
        "name_ner": "Joshua Nishanth['NAME'] Also known as Josh ['ALSO_KNOWN_AS'] born on 19 july['DATE_OF_BIRTH']"
    },
    {
        "name": "Joshua Nishanth , Also known as Josh, born on 19 july",
        "aka": "",
        "date of birth:": "",
        "part": "",
        "other information": "",
        "name_ner": "Joshua Nishanth['NAME'] born on 19 july['DATE_OF_BIRTH']"
    },
]

result = extract_data(input_data)
for item in result:
    print(item)
    
  https://drive.google.com/drive/folders/1Q7U-pL9g1-QacuEWKl6VZiKepawREZzu?usp=drive_link