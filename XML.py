import requests
import xml.etree.ElementTree as ET

def fetch_data_from_url(url):
    # Get the XML content from the URL
    response = requests.get(url)
    response.raise_for_status()  # Check if the request was successful
    return response.text

def extract_data_updated(xml_string):
    # Parse the XML data
    root = ET.fromstring(xml_string)
    
    # Find the 'persons' element under the root
    persons_element = root.find('persons')
    if persons_element is None:
        return []  # Return empty list if 'persons' element is not found
    
    # List to hold extracted information
    extracted_data = []

    # Loop through each 'person' entry
    for person in persons_element.findall('person'):
        # Dictionary to hold each person's data
        person_data = {}
        
        # Extract the 'num' field
        num = person.find('num').text if person.find('num') is not None else None
        person_data['num'] = num
        
        # Extract the 'information' field and process its contents
        info = person.find('information').text if person.find('information') is not None else None
        if info:
            # Split the information into logical sections
            fields = {
                'name': info.split('Вымышленные названия:')[0].strip(),
                'aliases': None,
                'additional_info': None
            }
            if 'Вымышленные названия:' in info:
                aliases_section = info.split('Вымышленные названия:')[1]
                fields['aliases'] = aliases_section.split('Р.И.К.:')[0].strip()
            if 'Прочая информация:' in info:
                additional_info_section = info.split('Прочая информация:')[1]
                fields['additional_info'] = additional_info_section.strip()

            # Add the processed fields to person_data
            person_data.update(fields)
        
        # Extract the 'decision' field
        decision = person.find('decision').text if person.find('decision') is not None else None
        person_data['decision'] = decision
        
        # Extract the 'date' field
        date = person.find('date').text if person.find('date') is not None else None
        person_data['date'] = date
        
        # Append the person's data to the extracted_data list
        extracted_data.append(person_data)
    
    return extracted_data

# URL containing the XML data
url = "https://example.com/data.xml"  # Replace with the actual URL

try:
    # Fetch and extract data from the provided URL
    xml_data = fetch_data_from_url(url)
    result = extract_data_updated(xml_data)
    
    # Display the result
    for entry in result:
        print(entry)
except requests.RequestException as e:
    print(f"Error fetching data: {e}")
except ET.ParseError as e:
    print(f"Error parsing XML: {e}")
