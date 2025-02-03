from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from requester import Requester
import time

class Parser:
    def __init__(self, school, base_url, category, location, conference):
        self.school = school
        self.base_url = base_url
        self.category = category
        self.location = location
        self.conference = conference
    
    def process(self, _url):
        try:
            items = []
            urls = self.get_coaches_url(_url)
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
    
    def get_name(self, soup):
        try:
            f_name = None
            l_name = None
            tag = soup.select_one('.s-coaches-detail-page__coach__name')
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
            tag = soup.find(lambda tag: tag.name == "dl" and "Title" in tag.text)
            if tag:
                title = tag.select_one('dd').get_text().strip()
            return title
        except:
            return None
        
    def get_email(self, soup):
        try:
            email = None
            tag = soup.find(lambda tag: tag.name == "dl" and "Email" in tag.text)
            if tag:
                email = tag.select_one('dd').get_text().strip()
            return email
        except:
            return None
    
    def get_number(self, soup):
        try:
            number = None
            tag = soup.find(lambda tag: tag.name == "dl" and "Phone" in tag.text)
            if tag:
                number = tag.select_one('dd').get_text().strip()
            return number
        except:
            return None
    
    def get_driver(self):
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--enable-unsafe-swiftshader")
        
        # Set up the WebDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        return driver
        
    def get_coaches_url(self, url):
        urls = []
        driver = self.get_driver()
         
        driver.get(url)
        
         # Add explicit wait
        wait = WebDriverWait(driver, 60)
        section_tag = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#coaching-staff > :first-child")))
         
        if section_tag:
            time.sleep(2)
            links = section_tag.find_elements(By.CSS_SELECTOR, '[data-test-id="s-person-details__personal-single-line"] a')
            for link in links:
                urls.append(link.get_attribute('href'))
        
        driver.quit()
        return urls