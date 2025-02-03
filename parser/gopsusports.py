from bs4 import BeautifulSoup
from requester import Requester

class Parser():
    def __init__(self, school, base_url, category, location, conference):
        self.school = school
        self.base_url = base_url
        self.category = category
        self.location = location
        self.conference = conference
    
    def process(self, _url):
        try:
            items = []
            raw_data = Requester.get(_url)
            urls = self.get_coaches_url(raw_data)
            for url in urls:
                raw_html = Requester.get(url)
                item = self.get_item(self.school, raw_html, url)
                items.append(item)
            return items
        except:
            return []
        
    def raw_html_to_soup(self, raw_html):
        return BeautifulSoup(raw_html, 'html.parser')
        
    def get_item(self, school, raw_html, url):
        _soup = self.raw_html_to_soup(raw_html)
        item = {}
        item['First Name'], item['Last Name']  = self.get_name(_soup)
        item['Title'] = self.get_title(_soup)
        item['School'] = school
        item['Email'] = self.get_email(_soup)
        item['Phone'] = self.get_number(_soup)
        item['Profile URL'] = url
        item['Category'] = self.category
        item['Location'] = self.location
        item['Conference'] = self.conference
        
        return item
    
    def get_coaches_url(self, raw_data):
        try:
            soup = self.raw_html_to_soup(raw_data)
            urls = []
            h3_tag = soup.find('h2', text="Women's Ice Hockey Coaching Staff")
            if h3_tag:
                next_tag = h3_tag.find_next_sibling()
                tags = next_tag.select('.staff-list-item__title-link')
                if tags:
                    urls = [f"{self.base_url}{tag.get('href')}" for tag in tags]
            return urls
        except:
            return None
    
    def get_name(self, soup):
        try:
            f_name = None
            l_name = None
            tag = soup.select_one('h1')
            if tag:
                name =  tag.get_text().strip().split(' ')
                name = [item for item in name if item] # Cleanse or remove empty strings
                f_name = name[0]
                l_name = name[1]
            return f_name, l_name
        except:
            return None, None
        
    def get_title(self, soup):
        try:
            title = None
            tag = soup.find(lambda tag: tag.name == "small" and "Title" in tag.text)
            if tag:
                title = tag.find_next_sibling().get_text()
            return title
        except:
            return None
        
    def get_email(self, soup):
        try:
            email = None
            tag = soup.find(lambda tag: tag.name == "small" and "Email" in tag.text)
            if tag:
                email = tag.find_next_sibling().get_text()
            return email
        except:
            return None
    
    def get_number(self, soup):
        try:
            number = None
            tag = soup.find(lambda tag: tag.name == "small" and "Phone" in tag.text)
            if tag:
                number = tag.find_next_sibling().get_text()
            return number
        except:
            return None