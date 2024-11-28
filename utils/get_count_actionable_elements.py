import tempfile
import os
import json
import asyncio
import pyppeteer

from fake_useragent import UserAgent  # Use this library for random User-Agents
from selenium.webdriver.common.by import By
from utils.urls import default_url

URL = default_url

# This marks the puppeteer implementation
async def pptr_count_actionable():
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

    await page.waitForSelector('body')
    # Randomly moving the mouse on the page
    await page.mouse.move(100, 100)
    await asyncio.sleep(1)

    # Scrolling the page to simulate human-like interaction
    await page.evaluate('window.scrollBy(0, 500)')
    await asyncio.sleep(1)

    await asyncio.sleep(10)
    # Query for actionable elements
    # This includes links, buttons, and input elements
    actionable_elements = await page.querySelectorAll(
        'a, button, input, select, textarea, [role="button"], [role="link"]')

    # Get the count of actionable elements
    count = len(actionable_elements)

    print(f"Number of actionable elements: {count}")

    # Close the browser
    await browser.close()

def get_count_actionable_elements():
    asyncio.run(pptr_count_actionable()) # find count using pyppeteer


# Below marks the selenium implementation
actionable_selectors = ["a", "button", "input", "select", "textarea", "[role='button']", "[role='link']"]
def sel_get_element_xpath(element):
    """Generate XPath for a given WebElement."""
    try:
        # If the element has an ID, use it directly
        '''
        # Commenting below code otherwise, for some elements xpath is returned in form of id, example: "//*[@id='hiddenLanguageInput']", Since it is different from the one extracted using javascript, it is displayed as locatability issue which is incorrect
        element_id = element.get_attribute("id")
        if element_id:
            return f"//*[@id='{element_id}']"
        '''

        # Otherwise, construct XPath
        path = []
        while element.tag_name.lower() != "html":
            siblings = element.find_elements(By.XPATH, f"./preceding-sibling::{element.tag_name}")
            index = len(siblings) + 1  # XPath index starts from 1
            path.insert(0, f"{element.tag_name}[{index}]")
            element = element.find_element(By.XPATH, "..")  # Navigate to parent
        return f"/{'/'.join(path)}"
    except Exception as e:
        print(f"Error generating XPath: {e}")
        return None


def sel_get_actionable_elements(driver):
    """Get all actionable elements and their XPaths."""
    actionable_xpath = ", ".join(actionable_selectors)  # CSS selector syntax

    elements = driver.find_elements(By.CSS_SELECTOR, actionable_xpath)
    results = []

    for element in elements:
        xpath = sel_get_element_xpath(element)
        if xpath:
            results.append({
                "tag_name": element.tag_name,
                "xpath": xpath,
                "text": element.text.strip()
            })
    return results


def sel_write_actionable_elements_to_json(count_actionable_elements, elements):
    file_path = os.path.join(tempfile.gettempdir(), "nvda\\xpath\\xpath_all_selenium.json")

    """Write actionable elements and their count to a JSON file."""
    data = {
        "count by default selenium driver": count_actionable_elements,
        "total_count based on actionable selectors": len(elements),
        "actionableElements": elements
    }
    try:
        with open(file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)  # Pretty-print with 4 spaces
        print(f"Actionable elements successfully written to {file_path}")
    except Exception as e:
        print(f"Error writing to JSON file: {e}")




