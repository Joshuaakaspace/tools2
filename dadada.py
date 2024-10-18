@staticmethod
def run_delta_updates_scraping(inner_instance):
    pass_down_meta = inner_instance.get_param('meta')

    logging.info("Type of meta: type({})".format(type(pass_down_meta)))
    logging.info("Should trigger amendment extraction: {}".format(pass_down_meta))

    # Fix: Check if pass_down_meta is not None and contains the required key
    if pass_down_meta and 'extract_amendment_site' in pass_down_meta:
        if pass_down_meta['extract_amendment_site']:
            amendment_extraction_result = CanadaSiteScraper.download_advance_data(inner_instance=inner_instance, meta=pass_down_meta)
            amendment_extraction_meta = amendment_extraction_result['meta']
        else:
            raise AirflowSkipException("Amendment not relevant, skipping.")
    else:
        logging.info("No amendment site or pass_down_meta is None")
        raise AirflowSkipException("No amendment site key in meta, skipping.")

    # Check if delta was downloaded on the first time
    if pass_down_meta['initial_run']:
        # Set the previous record as empty so that first time delta will be tagged as newly added record
        inner_instance.push_context_value('previous_records', [])
    else:
        inner_instance.push_context_value('previous_records', inner_instance.previous_records)

    # Skip if amendment is not relevant
    is_amendment_relevant = amendment_extraction_meta['is_amendment_relevant']
    logging.info(f"Meta: {amendment_extraction_meta}")
    if not is_amendment_relevant:
        raise AirflowSkipException("Amendment is not relevant, skipping.")

    inner_instance.push_context_value('amended_records', amendment_extraction_result['data']['records'])
    inner_instance.push_context_value('meta', amendment_extraction_result['meta'])

    logging.info(f"Result: {amendment_extraction_result}")
    data = amendment_extraction_result['data']
    records = data['records']
    meta = amendment_extraction_result['meta']
    logging.info(f"Extraction result meta: {meta}")

    return records
