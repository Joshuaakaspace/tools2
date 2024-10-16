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

# Extract the information using the updated function
result_test_updated = extract_data_updated(xml_data_test)

# Display the result for the new test
result_test_updated
