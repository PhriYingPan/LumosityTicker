import requests
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from googlesearch import search
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


from bs4 import BeautifulSoup

def lookup_company_info(ticker):
    
    # to search
    query = f"{ticker} investor relations"
    
    for j in search(query, tld="co.in", num=10, stop=10, pause=2):
        print(j)
        return j
    


def find_pdf_links_on_page(url):
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Specify the path to chromedriver.exe (download and save it on your system)
    service = Service("/Users/conanpan/Downloads/chromedriver-mac-arm64/chromedriver")
    
    # Initialize the WebDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # print("hello")
    try:
        # Open the URL
        tmp_url = "https://www.lincolnfinancial.com/public/aboutus/investorrelations/financialinformation/earnings"
        driver.get(tmp_url)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href$=".pdf"]'))
        )
        # Get page source and parse with BeautifulSoup
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        print(soup)
        
        # Select all <a> tags with href attributes ending in ".pdf"
        pdf_links = soup.select('a[href$=".pdf"]')
        
        # Extract and return the href attributes of these <a> tags
        return [link['href'] for link in pdf_links]
    
    finally:
        driver.quit() # Make sure to quit the driver to free resources



    # user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

    # tmp_url = "https://www.lincolnfinancial.com/public/aboutus/investorrelations/financialinformation/earnings"
    # # Create a request object with the URL and User-Agent header
    # req = Request(url, headers={'User-Agent': user_agent})
    # try:
        
    #     # Use urlopen to send the request and receive the response
    #     response = urlopen(req)
        
    #     # Read the response content
    #     html = response.read()
    #     # Parse the HTML content of the page with BeautifulSoup
    #     soup = BeautifulSoup(html, 'html.parser')
    #     # print("SOUP")
    #     # print(soup)
    #     # time.sleep(5)
        
    #     # Select all <a> tags with href attributes ending in ".pdf"
    #     # links = soup.find_all("a")
    #     # print("LINKS:",links)
    #     pdf_links = soup.select('a[href$=".pdf"]')
        
    #     # Extract and return the href attributes of these <a> tags
    #     return [link['href'] for link in pdf_links]
    
    # except HTTPError as e:
    #     print("HTTP Error:", e.code, url)
    #     return []
    # except URLError as e:
    #     print("URL Error:", e.reason, url)
    #     return []
        

def get_earnings_release_links(ticker):
    ir_url = lookup_company_info(ticker)
    links = find_pdf_links_on_page(ir_url)
    
    print(links)
    # Here you could filter or sort the links based on date or naming convention.
    # This is a simplistic approach and might need adjustments.
    return links[:4]

# Use the function
ticker = 'LNC'  # Example ticker
get_earnings_release_links(ticker)
