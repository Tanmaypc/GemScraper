import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class eProcureScraper:
    def __init__(self, chromedriver_path):
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        
        # Initialize the Chrome driver with explicit path
        service = Service(executable_path=chromedriver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)
        self.url = "https://eprocure.gov.in/eprocure/app?page=FrontEndLatestActiveTenders&service=page"
        self.data = []
        
    def open_site(self):
        self.driver.get(self.url)
        print("Website opened successfully")
        
    def handle_captcha(self):
        print("Please enter the captcha manually in the browser...")
        
        self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[value='Search']"))
        )
        
        input("Press Enter after entering the captcha and clicking Search...")
        
    def extract_tender_titles_and_links(self):
        # Wait for table to load
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table td")))
        
        # Using the specific selector you provided for tender links
        tender_links = self.driver.find_elements(By.CSS_SELECTOR, "#table td+ td a")
        
        for link in tender_links:
            try:
                title = link.text.strip()
                href = link.get_attribute("href")
                
                if title and href:
                    tender_data = {
                        'Title': title,
                        'Link': href
                    }
                    self.data.append(tender_data)
                    print(f"Extracted: {title[:50]}...")
            except Exception as e:
                print(f"Error extracting link data: {e}")
                continue
        
        print(f"Extracted {len(tender_links)} tender titles and links from current page")
        
    def go_to_next_page(self):
        try:
            # Using the specific selector you provided for next button
            next_button = self.driver.find_element(By.CSS_SELECTOR, "#loadNext b")
            if next_button:
                print("Clicking next button...")
                next_button.click()
                # Wait for the page to load
                time.sleep(3)
                return True
            else:
                return False
        except NoSuchElementException:
            print("No more pages or next button not found")
            return False
            
    def scrape_all_pages(self, max_pages=None):
        page_num = 1
        while True:
            print(f"\nScraping page {page_num}")
            self.extract_tender_titles_and_links()
            
            if max_pages and page_num >= max_pages:
                print(f"Reached maximum pages limit ({max_pages})")
                break
                
            if not self.go_to_next_page():
                break
                
            page_num += 1
            
    def filter_endpoint_security_tenders(self):
        security_keywords = [
            'endpoint security', 'antivirus', 'anti-virus', 'malware', 'cybersecurity', 
            'cyber security', 'security software', 'endpoint protection', 'edr', 
            'endpoint detection', 'threat protection', 'virus protection'
        ]
        
        filtered_data = []
        
        for tender in self.data:
            title = tender['Title'].lower()
            if any(keyword in title for keyword in security_keywords):
                filtered_data.append(tender)
                
        print(f"Found {len(filtered_data)} tenders related to endpoint security out of {len(self.data)} total tenders")
        return filtered_data
        
    def save_to_csv(self, data, filename="tender_titles_links.csv"):
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
        
    def close(self):
        self.driver.quit()
        
    def run(self, max_pages=None):
        try:
            self.open_site()
            self.handle_captcha()
            self.scrape_all_pages(max_pages)
            
            # Save all tender titles and links
            self.save_to_csv(self.data, "all_tender_titles_links.csv")
            
            # Filter and save endpoint security tenders
            security_tenders = self.filter_endpoint_security_tenders()
            self.save_to_csv(security_tenders, "security_tender_titles_links.csv")
            
            print("Scraping completed successfully")
            
        except Exception as e:
            print(f"An error occurred: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.close()


if __name__ == "__main__":
    # Replace this with your actual chromedriver path
    CHROMEDRIVER_PATH = "/usr/local/bin/chromedriver/chromedriver"
    
    # Optionally limit the number of pages to scrape (remove or set to None for all pages)
    MAX_PAGES = 5
    
    scraper = eProcureScraper(CHROMEDRIVER_PATH)
    scraper.run(MAX_PAGES)