import requests
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from googlesearch import search
from bs4 import BeautifulSoup
import PyPDF2
from urllib.request import urlopen
import io

def lookup_company_info(ticker):
    
    # to search
    query = f"{ticker} investor relations"
    
    for j in search(query, tld="co.in", num=10, stop=10, pause=2):
        print(j)
        return j
    


def find_pdf_links_on_page(url):
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    
    # Create a request object with the URL and User-Agent header
    req = Request(url, headers={'User-Agent': user_agent})
    try:
        # Use urlopen to send the request and receive the response
        response = urlopen(req)
        
        # Read the response content
        html = response.read()
        
        # Parse the HTML content of the page with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        # Select all <a> tags with href attributes ending in ".pdf"
        pdf_links = soup.select('a[href$=".pdf"]')
        # return tuple of (hyperlinked text, actual link)
        pdf_info = [(link.text, link['href']) for link in pdf_links]
        
        # Extract and return the href attributes of these <a> tags
        return pdf_info
    
    except HTTPError as e:
        print("HTTP Error:", e.code, url)
        return []
    except URLError as e:
        print("URL Error:", e.reason, url)
        return []
        

def check_keywords(url, keyword_list):    
    try:
        # Open the URL
        with urlopen(url) as response:
            # Read the PDF content
            pdf_file = response.read()
        
        # Create a PDF reader object
        pdf_content = io.BytesIO(pdf_file)
        pdf_reader = PyPDF2.PdfReader(pdf_content)
        
        # Iterate through first 3 pages in pdf
        keyword_counter = 0
        for page_num in range(min(len(pdf_reader.pages), 3)):
            # Extract text from the page
            page_text = pdf_reader.pages[page_num].extract_text().lower()
            
            # Check if any keyword is present in the page text
            for keyword in keyword_list:
                if keyword in page_text:
                    keyword_counter += 1
        
        return keyword_counter
    
    except Exception as e:
        print("Error:", str(e))
        return -1

def get_earnings_release_links(ticker):
    ir_url = lookup_company_info(ticker)
    link_info = find_pdf_links_on_page(ir_url)

    ''' logic to make sure the pdf's are the earnings releases '''

    # check if the hyperlinked text includes "earnings" or "release"
    possible_links = [link for (text, link) in link_info if ("earnings" in text.lower() or "release" in text.lower())]
    
    # TODO: prob better to make tuple of (link, num_keywords_in_link) and sort by number of keywords BUT this will be really slow
    # TODO: you can probably generate a "score" of how likely a link is to be a quarterly earnings release by weighting diff factors 
    # like hyperlink text match, number of keyword match, if link has "q1/q2/q3/q4" in it, etc

    if len(possible_links) < 4: 
        # need to find some more
        keywords = ['quarter', 'EPS', 'earnings per share'] # 'revenue', 'income', 'costs'
        all_links = [link for (text, link) in link_info]
        links_keyword_count = []
        # TODO: only searching the first 10 links rn
        for link in all_links[:10]:
            num_matching_pages = check_keywords(link, keywords)
            links_keyword_count.append((num_matching_pages, link))
            sorted_links_keyword_count = sorted(links_keyword_count, key=lambda x: x[0])
    else:
        return possible_links[:4]
    
    # while loop? to go further into nested pages to get link where the earnings releases are

    # Here you could filter or sort the links based on date or naming convention.
    # This is a simplistic approach and might need adjustments.
    return [link for (val, link) in sorted_links_keyword_count][:4]

# Use the function
ticker = 'GOOG'  # Example ticker
print(get_earnings_release_links(ticker))
