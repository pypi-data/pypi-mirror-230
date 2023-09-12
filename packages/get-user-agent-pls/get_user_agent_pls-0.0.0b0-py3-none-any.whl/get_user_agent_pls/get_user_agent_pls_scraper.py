import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# URLs for scraping user-agent strings for various browsers
browser_urls = {
    "Edge": "https://useragentstring.com/pages/Edge/",
    "Chrome": "https://useragentstring.com/pages/Chrome/",
    "Firefox": "https://useragentstring.com/pages/Firefox/",
    "Safari": "https://useragentstring.com/pages/Safari/",
    "GoogleBot": "https://useragentstring.com/pages/Googlebot/"
}

# Selector for the first record on each page
first_record_selector = "#liste > ul > li:nth-child(1) > a"

# Selector for the user-agent string on the redirected page
user_agent_selector = "#uas_textfeld"

def fetch_html(url):
    """Fetch HTML content from a URL."""
    response = requests.get(url)
    return response.text

def extract_first_user_agent_url(html_content, base_url, selector=first_record_selector):
    """Extract the URL of the first user-agent string from the HTML content."""
    soup = BeautifulSoup(html_content, 'html.parser')
    first_record = soup.select_one(selector)
    return urljoin(base_url, first_record['href']) if first_record else None

def extract_user_agent_string(html_content, selector=user_agent_selector):
    """Extract the user-agent string from the redirected page's HTML content."""
    soup = BeautifulSoup(html_content, 'html.parser')
    user_agent_field = soup.select_one(selector)
    return user_agent_field.text if user_agent_field else None

def main():
    user_agents = {}
    for browser, url in browser_urls.items():
        html_content = fetch_html(url)
        first_url = extract_first_user_agent_url(html_content, url)
        if first_url:
            new_html_content = fetch_html(first_url)
            user_agent = extract_user_agent_string(new_html_content)
            if user_agent:
                user_agents[browser] = user_agent
                print(f"New user-agent string for {browser}: {user_agent}")

    return user_agents

if __name__ == "__main__":
    main()
