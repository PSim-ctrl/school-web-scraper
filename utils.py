from oauth2client.service_account import ServiceAccountCredentials
import gspread
import json
import re

class Helper():
    def __init__(self):
        pass
    
    def to_google_sheet(self, data, sheet_name=None):
        try:
            creds_file = "cred.json"  # Replace with your credentials file
            shared_sheet_url = "https://docs.google.com/spreadsheets/d/1CvBlfX2YNMpgqK4_JQOLmtP-35VIIxz1UIhB8V4sut0/edit?gid=1038148581#gid=1038148581"  # Replace with your shared sheet URL

            sheet = self.setup_google_sheet(creds_file, shared_sheet_url, sheet_name)
        
            self.write_to_google_sheet(sheet, data)
            self.write_to_json(data, "output.json")
        except Exception as e:
            print(f"Error: {e}")
    
    @staticmethod
    def setup_google_sheet(creds_file, shared_sheet_url, sheet_name):
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
        client = gspread.authorize(creds)
        # Open the sheet by URL
        spreadsheet = client.open_by_url(shared_sheet_url)
        if sheet_name:
            sheet = spreadsheet.worksheet(sheet_name)
        else:
            sheet = spreadsheet.sheet1
        return sheet

    # Write data to Google Sheets
    @staticmethod
    def write_to_google_sheet(sheet, data):
        sheet.clear()  # Clear existing data
        if data:
            # Write headers
            headers = list(data[0].keys())
            sheet.insert_row(headers, 1)
            # Prepare data rows
            rows = [list(row.values()) for row in data]
            # Batch update rows
            sheet.insert_rows(rows, 2)
        print("Data written to Google Sheet")

    def write_to_json(self, data, filename):
        '''
        write output data to a json file.
        '''
        with open(filename, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        print(f"Data written to {filename}")
        
    def read_from_json(self, filename):
        '''
        read data from a json file.
        this could also use to transform data without scraping website all over again.
        '''
        with open(filename, 'r') as json_file:
            data = json.load(json_file)
        print(f"Data read from {filename}")
        return data
    
    def transform_data(self, filename):
        '''
        Transform data by removing the last two digits from the 'Last Name' field.
        '''
        data = self.read_from_json(filename)
        
        for item in data:
            item['Last Name'] = re.sub(r"'\d{2}", "", item['Last Name'])
        return data

    @staticmethod
    def sanitize(items):
        exclude = ['trainer', 'operation', 'operations', 'equipment', 'strength', 'conditioning', 'student', 'students', 'performance', 'volunteer', 'volunteers']
        _temp = []
        for item in items:
            item['Last Name'] = re.sub(r"'\d{2}", "", item['Last Name'])
            if not any(exc_item in item['Title'].lower() for exc_item in exclude):
                _temp.append(item)

        return _temp

    def reprocess(self):
        '''
        This function reads the data from the output.json file and reprocesses 
        it to remove the last two digits from the Last Name field.
        We can clean data without having to scrape the websites again.
        This could also be updated to transform the data in any other way.
        '''
        data = self.transform_data('output.json')
        sheet_name = 'List of Coaches (scraped)'
        self.to_google_sheet(data, sheet_name)