def amendment_soup_handler(soup, source_type, country, site_url, has_single_record_type, default_record_type, meta):
    consolidated_records = load_consolidated_records(source_type=source_type, country=country)
    
    log.info(f'Meta: {meta}')
    latest_sor = meta['amendment_tracking_value']
    log.info(f'latest sor: {latest_sor}')
    
    try:
        # Attempt to find amendments with <ol> tag
        list_container = soup.find('ol', class_='lst-spcd')
        numeration = int(list_container.attrs.get('start'))
        
        # Extract part and schedule information
        part_and_schedule_content = BeautifulSoup(str(list_container.previous_sibling), 'html.parser')
        part_and_schedule_text = part_and_schedule_content.find('em').previous_sibling
        part_and_schedule = extract_part_and_schedule(str(part_and_schedule_text))
        log.info(part_and_schedule)

        amended_records = []
        for child in list_container.children:
            part = part_and_schedule['part'] if part_and_schedule is not None else ''
            schedule = part_and_schedule['schedule'] if part_and_schedule is not None else ''
            
            amended_record = create_record(str(numeration), child.get_text(), part, schedule)
            amended_records.append(amended_record)
            numeration = numeration + 1

    except Exception as e:
        # Fallback to <ul> tag if <ol> is not found
        log.error(f"An error occurred: {e}, trying with <ul> tag")
        list_container = soup.find('ul', class_='lst-spcd')
        
        previous_sibling = list_container.previous_sibling
        while previous_sibling and previous_sibling.name != 'p':
            previous_sibling = previous_sibling.previous_sibling
        
        if previous_sibling:
            part_and_schedule_content = BeautifulSoup(str(previous_sibling), 'html.parser')
            part_and_schedule_text = part_and_schedule_content.find('em').previous_sibling
            part_and_schedule = extract_part_and_schedule(str(part_and_schedule_text))
            log.info(f"Found schedule: {part_and_schedule}")
        else:
            log.info("No previous paragraph tag found.")

        amended_records = []
        if part_and_schedule and part_and_schedule.get('schedule'):
            log.info(f"Found schedule: {part_and_schedule}")

        # New pattern-based matching logic for <ul> elements from second version
        pattern = re.compile(r'(\d{4})\s(\(+\d+)\s*(also known as\s([^)]+))?\)')
        for ul_tag in soup.find_all('ul', class_='list-spcd mrgn-tp-md list-unstyled'):
            for li in ul_tag.find_all('li'):
                text = li.get_text()
                match = pattern.search(text)
                if match:
                    amended_record = create_record(str(numeration), text, part_and_schedule.get('part', ''), part_and_schedule.get('schedule', ''))
                    amended_record['name'] = match.group(2).strip() if match.group(2) else ''
                    amended_record['dob'] = match.group(4) if match.group(4) else ''
                    amended_records.append(amended_record)
                    numeration += 1
                else:
                    log.info("No available updates for individuals or entities")
    
    updated_consolidated_records = []
    update_history = []

    # Update the consolidated records with amended records
    for record in consolidated_records['records']:
        updated_record = record
        for amended_record in amended_records:
            amended_record['type'] = get_record_type_for_amended_record(record, amended_record)
            to_update = record['id'] == amended_record['id'] and \
                        record['part'] == amended_record['part'] and \
                        record['schedule'] == amended_record['schedule']
            if to_update:
                updated_record = amended_record
                amended_records.remove(amended_record)
        updated_consolidated_records.append(updated_record)

    # Check for new records
    if len(amended_records) > 0:
        for new_record in amended_records:
            updated_consolidated_records.append(new_record)

    # Update history notes
    for note in consolidated_records['historyNotes']:
        update_history.append(note)
    update_history.append(latest_sor)

    # Prepare updated delta
    updated_consolidated_delta = {'records': updated_consolidated_records, 'historyNotes': update_history}
    log.info(f'Scraping Amendment Site Ended')

    # Return the updated consolidated data
    return {
        'data': updated_consolidated_delta,
        'meta': meta
    }

    # If no amendments were found, return existing records
    return {
        'data': consolidated_records,
        'meta': meta
    }
