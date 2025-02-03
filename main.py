from utils import Helper
import re
import importlib
import json

def process():
    '''
    This function scrapes the data from the websites and writes it to a Google Sheet.
    '''
    _helper = Helper()
    
    existing_items = _helper.read_from_json('output.json')
    items = get_items()
    existing_items.extend(items)
    items = existing_items

    items = _helper.sanitize(items) # clean/filter data

    sheet_name = 'List of Coaches (scraped)'
    _helper.to_google_sheet(items, sheet_name)
    print('done')
    
def get_items():
    items = []
    with open("config.json", "r") as f:
        config = json.load(f)
        
    skip = True
    for config_item in config:
        module_name = config_item["module"]
        class_name = config_item["class"]
        school = config_item["college/university"]
        base_url = f'https://{config_item["website"]}'
        urls = config_item["urls"]
        
        if school == "Gustavus Adolphus College":
            skip = False
        if skip:
            continue
        print(f'Processing {school}')
        
        module = importlib.import_module(module_name)
        ATTR = getattr(module, class_name)
        for url in urls:
            category = url["category"]
            location = url["location"]
            conference = url["conference"]
            _url = url["url"]
            parser = ATTR(school, base_url, category, location, conference)
            items.extend(parser.process(_url))
        print(f'{school} completed')
        
    return items

def get_single_school():
    items = []
    config_item = {
        "college/university": "Lawrence University",
        "school name": "Lawrence Vikings",
        "website": "vikings.lawrence.edu",
        "urls": [
            {
                "url": "https://vikings.lawrence.edu/sports/womens-ice-hockey/roster#sidearm-roster-coaches",
                "category": "Women's College Hockey DIII Coaches",
                "location": "Wisconsin",
                "conference": "WNCHA"
            }
        ],
        "module": "parser.vikings",
        "class": "Parser"
    }
    
    module_name = config_item["module"]
    class_name = config_item["class"]
    school = config_item["college/university"]
    base_url = f'https://{config_item["website"]}'
    urls = config_item["urls"]
    
    module = importlib.import_module(module_name)
    ATTR = getattr(module, class_name)
    for url in urls:
        category = url["category"]
        location = url["location"]
        conference = url["conference"]
        _url = url["url"]
        parser = ATTR(school, base_url, category, location, conference)
        items.extend(parser.process(_url))
    print(items)

if __name__ == '__main__':
    process()
    # extra()
    # get_single_school()