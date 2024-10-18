import xml.etree.ElementTree as ET
import requests
import pandas as pd

# URL for the XML data
url = 'https://api.websfm.kz/v1/sanctions/sanction-weapon-old/xml/?category=dprk&category=iran'

# Fetch XML data from URL
response = requests.get(url)
if response.status_code == 200:
    xml_data = response.text
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")
    xml_data = None

# Proceed if XML data is successfully fetched
if xml_data is not None:
    # Parse XML
    root = ET.fromstring(xml_data)

    # Initialize a list to store extracted data
    all_data = []

    # Loop over each <person> element in the XML
    for person in root.findall('.//person'):
        data = {}
        data['num'] = person.find('num').text if person.find('num') is not None else 'N/A'
        information = person.find('information').text if person.find('information') is not None else 'N/A'
        
        # Extracting name (first part of information text)
        data['name'] = information.split(',')[0] if information != 'N/A' else 'N/A'
        
        # Extracting Also Known As (if available in information)
        aka_split = 'Вымышленные названия:'
        data['also_known_as'] = 'N/A'
        if aka_split in information:
            data['also_known_as'] = information.split(aka_split)[1].split('Р.И.К.:')[0].strip()
        
        # Extracting address, date of listing, and other details
        address_split = 'Адрес:'
        date_list_split = 'Дата внесения в перечень:'
        data['address'] = 'N/A'
        data['date_of_listing'] = 'N/A'
        
        if address_split in information:
            data['address'] = information.split(address_split)[1].split(date_list_split)[0].strip()
        
        if date_list_split in information:
            data['date_of_listing'] = information.split(date_list_split)[1].split('Прочая информация:')[0].strip()
        
        # Extracting decision
        data['decision'] = person.find('decision').text if person.find('decision') is not None else 'N/A'
        
        # Extracting date
        data['date'] = person.find('date').text if person.find('date') is not None else 'N/A'
        
        # Placeholders for fields that are not clearly available in the XML
        data['designation'] = 'N/A'
        data['date_of_birth'] = 'N/A'
        data['place_of_birth'] = 'N/A'
        data['citizenship'] = 'N/A'
        data['passport_no'] = 'N/A'
        data['national_identification_no'] = 'N/A'

        # Checking for fields within 'Прочая информация'
        if 'Прочая информация:' in information:
            extra_info = information.split('Прочая информация:')[1]

            # Dummy logic for extraction from extra info (adjust based on actual XML content):
            if 'designation' in extra_info:
                data['designation'] = extra_info.split('designation:')[1].split('.')[0].strip()
            if 'date_of_birth' in extra_info:
                data['date_of_birth'] = extra_info.split('date_of_birth:')[1].split('.')[0].strip()
            if 'place_of_birth' in extra_info:
                data['place_of_birth'] = extra_info.split('place_of_birth:')[1].split('.')[0].strip()
            if 'citizenship' in extra_info:
                data['citizenship'] = extra_info.split('citizenship:')[1].split('.')[0].strip()
            if 'passport_no' in extra_info:
                data['passport_no'] = extra_info.split('passport_no:')[1].split('.')[0].strip()
            if 'national_identification_no' in extra_info:
                data['national_identification_no'] = extra_info.split('national_identification_no:')[1].split('.')[0].strip()

        # Append the extracted data to the list
        all_data.append(data)

    # Create a DataFrame from the extracted data
    df = pd.DataFrame(all_data)

    # Save DataFrame to CSV or Excel
    df.to_csv('extracted_data.csv', index=False)  # Save as CSV
    # df.to_excel('extracted_data.xlsx', index=False)  # Save as Excel (uncomment if you prefer Excel)

    print("Data extracted and saved successfully!")

# Display the DataFrame (optional)
if df is not None:
    print(df)
