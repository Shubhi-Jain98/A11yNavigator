# to run this file, call this way: asyncio.run(extract_dom_pptr()) # Extract DOM

import tempfile
import os
import json
import asyncio
import pyppeteer

from bs4 import BeautifulSoup
from fake_useragent import UserAgent  # Use this library for random User-Agents
from utils.urls import default_url

URL = default_url

async def get_dom(browser, page):
    # Scroll the page in steps to load dynamic content
    scroll_pause_time = 5  # seconds
    for _ in range(5):  # Scroll a few times
        try:
            await page.evaluate('window.scrollBy(0, window.innerHeight);')
            await asyncio.sleep(scroll_pause_time)
        except pyppeteer.errors.NetworkError as e:
            print("Network error during scrolling:", e)
            break  # Exit the loop if the execution context is destroyed due to navigation.
        except Exception as e:
            print("Other scrolling error:", e)
            break

    # Wait for the page to load
    try:
        await page.waitForSelector("body", {'timeout': 5000})
    except pyppeteer.errors.TimeoutError:
        print("Timeout waiting for body element.")
        await browser.close()
        return

    # Extract the DOM as HTML
    dom_content = await page.evaluate('document.documentElement.outerHTML')
    fileName = os.path.join(tempfile.gettempdir(), "nvda\\nvda_dom_pptr.json")

    # Parse the HTML DOM structure using BeautifulSoup
    soup = BeautifulSoup(dom_content, "html.parser")

    def parse_element(element):
        """Recursively parse an HTML element into a dictionary format."""
        element_dict = {
            "tag": element.name,
            "attributes": element.attrs,
            "text": element.get_text(strip=True) if element.text else "",
            "children": [parse_element(child) for child in element.find_all(recursive=False)]
        }
        return element_dict

    # Assuming we want to parse the body of the DOM
    dom_dict = parse_element(soup.body)
    # Write to JSON file
    with open(fileName, 'w', encoding='utf-8') as file:
        json.dump(dom_dict, file, indent=4)

    print(f"DOM content saved to: {fileName}")


async def extract_dom_pptr():
    print("Launching Chrome...")

    ua = UserAgent()
    user_agent = ua.random
    executable_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'

    # Launch a new browser instance
    browser = await pyppeteer.launch({
        'headless': False,  # Set to False to see the browser UI, True for headless mode
        'executablePath': executable_path,
        'args': ['--no-sandbox',
                 '--disable-setuid-sandbox',
                 '--disable-blink-features=AutomationControlled',
                 '--disable-features=IsolateOrigins,site-per-process',
                 '--window-size=1920,1080',
                 f'--user-agent={user_agent}'
        ]  # Additional launch arguments
    })
    # Open a new page
    page = await browser.newPage()
    await page.setUserAgent(user_agent)
    # Adding a random delay to mimic human-like browsing
    await asyncio.sleep(2)

    # Navigate to a URL
    try:
        await page.goto(URL,
                        {'waitUntil': 'networkidle2'})
    except pyppeteer.errors.PageError as e:
        print("Navigation error:", e)
        await browser.close()
        return

    #1. Extract DOM
    await get_dom(browser, page)

    # Close the browser
    await browser.close()
