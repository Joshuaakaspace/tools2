import logging
from bs4 import BeautifulSoup
import json

log = logging.getLogger(__name__)

def amendment_soup_handler(soup, source_type, country, site_url, has_single_record_type, default_record_type, meta):
    consolidated_records = load_consolidated_records(source_type=source_type, country=country)
    sor_content = soup.find('h1', id='wb-cont')
    latest_sor = extract_sor(sor_content.get_text()) if sor_content else None
    meta['latest_sor'] = latest_sor

    try:
        # Attempt to find and parse the list container
        list_container = soup.find('ol', class_='lst-spcd')
        if not list_container:
            log.warning("No list container found.")
            meta['is_amendment_relevant'] = False
            return {'data': consolidated_records, 'meta': meta}

        # Extract part and schedule information
        part_and_schedule_content = BeautifulSoup(str(list_container.previous_sibling), 'html.parser')
        part_and_schedule_text = part_and_schedule_content.find('em').previous_sibling if part_and_schedule_content.find('em') else None
        part_and_schedule = extract_part_and_schedule(str(part_and_schedule_text)) if part_and_schedule_text else None

        if not part_and_schedule or not part_and_schedule.get('schedule'):
            log.warning("No valid part and schedule found.")
            meta['is_amendment_relevant'] = False
            return {'data': consolidated_records, 'meta': meta}

        log.info(f"Found part and schedule: {part_and_schedule}")
        meta['is_amendment_relevant'] = True
        # If a valid schedule is found, retain the original consolidated records
        return {'data': consolidated_records, 'meta': meta}

    except Exception as e:
        log.error(f"An error occurred while processing: {e}")
        meta['is_amendment_relevant'] = False
        # In case of an exception, return the original consolidated records
        return {'data': consolidated_records, 'meta': meta}
