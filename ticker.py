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

import PyPDF2
from urllib.request import urlopen
import io
from collections import deque
from urllib.parse import urljoin
from urllib.parse import urljoin, urlparse



from bs4 import BeautifulSoup

def lookup_company_info(ticker):
    
    # to search
    query = f"{ticker} investor relations"
    
    for j in search(query, tld="co.in", num=10, stop=10, pause=2):
        # print(j)
        return j
    


def find_pdf_links_on_page(url):
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Specify the path to chromedriver.exe
    service = Service("/Users/conanpan/Downloads/chromedriver-mac-arm64/chromedriver")
    
    # Initialize the WebDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    pdf_links = []
    try:
        # Open the URL
        driver.get(url)
        
        # Wait for the presence of any <a> tags with href ending with ".pdf"
        # WebDriverWait(driver, 10).until(
        #     EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[href$=".pdf"]'))
        # )
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, 'a'))
        )
        # Set implicit wait time

        # driver.implicitly_wait(10)

        
        
        # Get page source and parse with BeautifulSoup
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # Get the base URL to use for joining with relative links
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # Find all <a> tags with href attributes ending in ".pdf"
        for link in soup.select('a[href$=".pdf"]'):
            href = link['href']
            # Check if href is relative and join it with the base url if needed
            if not href.lower().startswith('http'):
                href = urljoin(base_url, href)
            pdf_links.append(href)
    
    finally:
        driver.quit() # Make sure to quit the driver to free resources
    
    return pdf_links


def find_sub_links(url):
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Specify the path to chromedriver.exe
    service = Service("/Users/conanpan/Downloads/chromedriver-mac-arm64/chromedriver")
    
    # Initialize the WebDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    non_pdf_links = []
    try:
        # Open the URL
        driver.get(url)

        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, 'a'))
        )
        
        # Get page source and parse with BeautifulSoup
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # print("SOUP")
        # print(soup)

        # Get the base URL to use for joining with relative links
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # Select all <a> tags but exclude those with href attributes ending in ".pdf"
        for link in soup.find_all('a', href=lambda href: href and not href.endswith('.pdf') and '#' not in href):
            href = link.get('href')
            # Ensure the link is absolute
            if href.startswith('http'):
                for word in link_keywords:
                    if word in href:
                        non_pdf_links.append(href)
                        break
            else:
                # If the link is relative, make it absolute by combining with the base URL
                for word in link_keywords:
                    if word in href:
                        non_pdf_links.append(urljoin(base_url, href))
                        break
        
    finally:
        driver.quit()  # Make sure to quit the driver to free resources
    
    return non_pdf_links


def check_keywords(url, keyword_list): 
    is_2023 = False   
    try:
        # Open the URL
        with urlopen(url) as response:
            # Read the PDF content
            pdf_file = response.read()
        
        # Create a PDF reader object
        pdf_content = io.BytesIO(pdf_file)
        pdf_reader = PyPDF2.PdfReader(pdf_content)
        
        # Iterate through first pages 2 in pdf
        keyword_counter = 0
        for page_num in range(min(len(pdf_reader.pages), 2)):
            # Extract text from the page
            page_text = pdf_reader.pages[page_num].extract_text().lower()
            
            # Check if any keyword is present in the page text
            if '2023' in page_text:
                is_2023 = True
            for keyword in keyword_list:
                if keyword in page_text:
                    keyword_counter += 1
        
        return keyword_counter, is_2023 
    
    except Exception as e:
        print("Error:", str(e))
        return -1, False
        

def get_earnings_release_links(ticker):
    ir_url = lookup_company_info(ticker)


    # pdf_list = find_pdf_links_on_page(ir_url)

    sub_links = find_sub_links(ir_url)

    print(sub_links)
    print(len(sub_links))

    

    output_links = []
    j = 0
    q = deque()
    visited = set()
    q.append(ir_url)
    visited.add(ir_url)
    step = 0
    while q:
        # print("entered q")
        if step > 1:
            return output_links
        size = len(q)
        for i in range(size):
            # print("step:",step)

            if step > 1:
                # print("RETURNING")
                return output_links
            curr = q.popleft()
            print("current url:",curr, j)
            j+=1
            pdf_list = find_pdf_links_on_page(curr)
            
            # call method to check if pdf is a quarterly earnings, if it is add
            # print("num pdfs:", len(pdf_list))
            for link in pdf_list:
                num_keys, is_2023 = check_keywords(link, earnings_keywords)
                if link not in output_links and num_keys >= 5 and is_2023:
                    # print("appending:",link)
                    # print("num keywords:", num_keys)
                    output_links.append(link)

                if len(output_links) >= 4:
                    return output_links

            sub_links = find_sub_links(ir_url)
            # if len(sub_links) > 10:
            #     sub_links = sub_links[:10]
            # print("sub_links:",len(sub_links))
            # print("sub_links:",sub_links)
            for sub_link in sub_links:
                if sub_link not in visited:
                    q.append(sub_link)
                    visited.add(sub_link)
        step += 1


    return output_links

earnings_keywords = {
    "revenue",
    "profit",
    "loss",
    "EBITDA",
    "net income",
    "operating income",
    "gross margin",
    "earnings per share",
    "dividend",
    "balance sheet",
    "income statement",
    "cash flow statement",
    "year-over-year",
    "quarter-over-quarter",
    "guidance",
    "forecast",
    "market capitalization",
    "share price",
    "SEC",
    "10-Q",
    "10-K",
    "GAAP",
    "non-GAAP",
    "CEO",
    "CFO",
    "Q1",
    "Q2",
    "Q3",
    "Q4",
    "4Q",
    "3Q",
    "2Q",
    "1Q",
    "fiscal year",
    "capital expenditure",
    "research and development",
    "R&D"
}

link_keywords = {
    "release",
    "earning"
}



# Use the function
ticker = 'LNC'  # Example ticker
print(get_earnings_release_links(ticker))

if __name__ == '__main__':




# browse through all pdfs on current page and add to global array if we can confirm that it is a earnings release 
# bfs through all links on the current page and enter them 
# stop traversing once our global array has 4 items or stop when we have traversed more than 2 steps