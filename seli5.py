import os
import json
from datetime import datetime
from tools.imod_scraper import scrape_last_updated_date, is_date_new, log_last_updated_date, download_and_rename_excel_file
from tools.imod_delta import serializer, process_differences, compare_files, read_excel_as_dataframe
import sys

# Constants
ACTION_NAME = "PROCESS_DELTA_FILE"
PARAM_TABLE_URL = "table_url"
PARAM_EXCEL_URL = "excel_url"
PARAM_LAST_UPDATED_LOG_FILE = "lastUpdatedLogFile"
PARAM_ARTIFACTS_FOLDER = "artifactsFolder"
DEFAULT_LAST_UPDATED_LOG = 'last_updated_log.txt'
DEFAULT_ARTIFACTS_FOLDER = 'artifacts'

class DeltaFileProcessor:
    def __init__(self):
        self.table_url = None
        self.excel_url = None
        self.last_updated_log_file = None
        self.artifacts_folder = None

    @staticmethod
    def name() -> str:
        return ACTION_NAME

    def setup(self):
        self.table_url = self.get_param(PARAM_TABLE_URL)
        self.excel_url = self.get_param(PARAM_EXCEL_URL)
        self.last_updated_log_file = self.get_param(PARAM_LAST_UPDATED_LOG_FILE, DEFAULT_LAST_UPDATED_LOG)
        self.artifacts_folder = self.get_param(PARAM_ARTIFACTS_FOLDER, DEFAULT_ARTIFACTS_FOLDER)

    def validation_schema(self):
        return {
            'table_url': fields.Str(required=True, validate=validate.URL(error="Invalid table URL")),
            'excel_url': fields.Str(required=True, validate=validate.URL(error="Invalid excel URL")),
            'lastUpdatedLogFile': fields.Str(required=False, default=DEFAULT_LAST_UPDATED_LOG),
            'artifactsFolder': fields.Str(required=False, default=DEFAULT_ARTIFACTS_FOLDER)
        }

    def script(self):
        # Scraper setup
        last_updated_date = scrape_last_updated_date(self.table_url, self.last_updated_log_file)
        if last_updated_date and is_date_new(last_updated_date, self.last_updated_log_file, self.last_updated_log_file):
            file_path = download_and_rename_excel_file(self.excel_url, self.artifacts_folder, self.last_updated_log_file)
            if file_path:
                log_last_updated_date(last_updated_date, self.last_updated_log_file)
                files = sorted([f for f in os.listdir(self.artifacts_folder) if f.startswith("IMOD_LIST")], reverse=True)
                if len(files) >= 2:
                    file1 = os.path.join(self.artifacts_folder, files[0])
                    file2 = os.path.join(self.artifacts_folder, files[1])
                    delta_file_path = os.path.join(self.artifacts_folder, 'delta.json')
                    compare_files(file1, file2, delta_file_path, self.last_updated_log_file)
                    try:
                        os.remove(file1)
                        self.log_message(f"Deleted the previous file: {file1}")
                    except Exception as e:
                        self.log_message(f"Error deleting the previous file: {file1}: {e}")
                    return delta_file_path
                else:
                    self.log_message("Not enough files for comparison.")
                    return None
            else:
                self.log_message("No new updates. The file is up to date.")
                return None
        else:
            self.log_message("Could not find the last updated date.")
            return None

    def log_message(self, message):
        with open(self.last_updated_log_file, 'a') as log_file:
            log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

# Example usage:
processor = DeltaFileProcessor()
processor.setup()  # You can populate the params here.
delta_file_path = processor.script()

# The `delta_file_path` will be returned if the delta comparison is successful, else None.
