import requests
from googlesearch import search


from bs4 import BeautifulSoup

def lookup_company_info(ticker):
    
    # to search
    query = f"{ticker} investor relations"
    
    for j in search(query, tld="co.in", num=10, stop=10, pause=2):
        print(j)
        return j
    


def find_pdf_links_on_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    # tmp_url = "https://www.lincolnfinancial.com/public/aboutus/investorrelations/financialinformation/earnings"
    response = requests.get(url, headers=headers)
    # print(response)
    if response.status_code != 200:
        print("ERROR")
        return []
    soup = BeautifulSoup(response.text, 'html.parser')
    print("SOUP")
    print(soup)
    pdf_links = soup.select('a[href$=".pdf"]')  # Finding all PDF links
    
    # print(pdf_links)
    return [link['href'] for link in pdf_links]

def get_earnings_release_links(ticker):
    ir_url = lookup_company_info(ticker)
    links = find_pdf_links_on_page(ir_url)
    
    print(links)
    # Here you could filter or sort the links based on date or naming convention.
    # This is a simplistic approach and might need adjustments.
    return links[:4]

# Use the function
ticker = 'GOOGL'  # Example ticker
get_earnings_release_links(ticker)
