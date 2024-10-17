import logging
from bs4 import BeautifulSoup
import re
import json

log = logging.getLogger(__name__)

def amendment_soup_handler(soup, source_type, country):
    consolidated_records = load_consolidated_records(source_type=source_type, country=country)
    sor_content = soup.find('h1', id='wb-cont')
    log.info(f"SOR Content: {sor_content}")
    latest_sor = extract_sor(sor_content.get_text())

    try:
        # Attempt to find and parse the list container
        list_container = soup.find('ol', class_='lst-spcd')
        numeration = int(list_container.attrs.get('start', 1))

        # Extract part and schedule information
        part_and_schedule_content = BeautifulSoup(str(list_container.previous_sibling), 'html.parser')
        part_and_schedule_text = part_and_schedule_content.find('em').previous_sibling
        part_and_schedule = extract_part_and_schedule(str(part_and_schedule_text))
        log.info(f"Part and Schedule: {part_and_schedule}")

        amended_records = []

        # Check if part and schedule are available
        if part_and_schedule and part_and_schedule.get('schedule'):
            log.info(f"Found schedule: {part_and_schedule}")

            # Parse and extract records using a regular expression
            pattern = re.compile(r"(\d+)\s([^\)]+)\s\(born on\s([^\)]+)\)")
            ul_tags = soup.find_all('ul', class_='lst-spcd mrgn-lft-lg list-unstyled')
            
            for ul in ul_tags:
                for li in ul.find_all('li'):
                    text = li.get_text()
                    match = pattern.search(text)
                    if match:
                        # Create the amended record
                        amended_record = detail_extract(text)
                        amended_record['id'] = match.group(1)
                        amended_record['name'] = match.group(2).strip()
                        amended_record['dob'] = match.group(3).strip()
                        amended_record['part'] = part_and_schedule['part']
                        amended_record['schedule'] = part_and_schedule['schedule']
                        amended_records.append(amended_record)
            log.info(f"Amended Records: {amended_records}")

            # If successful, return the updated records and meta information
            return {
                'data': {'records': amended_records},
                'meta': {'latest_sor': latest_sor, 'is_amendment_relevant': True}
            }

        else:
            log.warning("No available updates for individuals or entities")
            return {
                'data': consolidated_records,
                'meta': {'latest_sor': latest_sor, 'is_amendment_relevant': False}
            }

    except Exception as e:
        log.error(f"An error occurred while processing: {e}")
        
        # Handle the fallback - update consolidated records using the template logic
        updated_consolidated_records = []
        update_history = []

        # Update existing records with amended records (if any) in the same way as the template
        for record in consolidated_records['records']:
            updated_record = record
            for amended_record in amended_records:
                if (record['id'] == amended_record['id'] and 
                    record['part'] == amended_record['part'] and 
                    record['schedule'] == amended_record['schedule']):
                    updated_record = amended_record
                    amended_records.remove(amended_record)
                    break
            updated_consolidated_records.append(updated_record)

        # Add any new amended records that were not part of existing consolidated records
        if amended_records:
            for new_record in amended_records:
                updated_consolidated_records.append(new_record)
            log.info(f"Amended Records: {amended_records}")

        # Update history notes
        for note in consolidated_records['historyNotes']:
            update_history.append(note)
        update_history.append(latest_sor)

        # Create a consolidated delta with the updated records
        updated_consolidated_delta = {
            'records': updated_consolidated_records,
            'historyNotes': update_history
        }

        # Save the updated consolidated delta to a file
        updated_delta_file = get_delta_file_name(source_type, country)
        with open(updated_delta_file, "w") as output_file:
            json.dump(updated_consolidated_delta, output_file)
        log.info(f"Consolidated file: {updated_delta_file} was successfully saved.")
        log.info("END")

        # Return the output as per the template
        return {
            'data': updated_consolidated_delta,
            'meta': {'latest_sor': latest_sor, 'is_amendment_relevant': False}
        }
