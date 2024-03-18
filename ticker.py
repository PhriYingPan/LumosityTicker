import requests
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from googlesearch import search


from bs4 import BeautifulSoup

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
        

def get_earnings_release_links(ticker):
    ir_url = lookup_company_info(ticker)
    link_info = find_pdf_links_on_page(ir_url)

    ''' logic to make sure the pdf's are the earnings releases '''

    # check if the hyperlinked text includes "earnings" or "release"
    possible_links = [link for (text, link) in link_info if ("earnings" in text.lower() or "release" in text.lower())]
    
    if len(possible_links) < 4: 
        # need to find some more
        

    # while loop? to go further into nested pages to get link where the earnings releases are

    # Here you could filter or sort the links based on date or naming convention.
    # This is a simplistic approach and might need adjustments.
    return possible_links[:4]

# Use the function
ticker = 'GOOG'  # Example ticker
get_earnings_release_links(ticker)
