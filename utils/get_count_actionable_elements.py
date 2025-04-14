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
        # Commenting below code otherwise, for some elements x  path is returned in form of id, example: "//*[@id='hiddenLanguageInput']", Since it is different from the one extracted using javascript, it is displayed as locatability issue which is incorrect
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

 # Extract all actionable elements with listeners
def is_element_hidden(element):
    """Determine if an element is hidden."""
    try:
        # Check if element is disabled
        is_disabled = (
                element.get_attribute("disabled") is not None or
                element.get_attribute("aria-disabled") == "true" or
                "disabled" in element.get_attribute("class") or
                element.get_attribute("disabled") == "true"
        )
        if is_disabled:
            return True

        # Check if element is displayed
        if not element.is_displayed():
            return True

        # Check if the element or any ancestor has aria-hidden="true"
        parent = element
        while parent:
            aria_hidden = parent.get_attribute("aria-hidden")
            if aria_hidden and aria_hidden.lower() == "true":
                return True  # The element is hidden due to aria-hidden
            parent = parent.find_element("xpath","..") if parent.tag_name.lower() != "html" else None  # Move up the DOM tree

        script = """
        const el = arguments[0];
        const style = window.getComputedStyle(el);
        return style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0' || el.offsetParent === null || el.offsetWidth <= 0 || el.offsetHeight <= 0;        
        """
        return element.parent.execute_script(script, element)
    except Exception as e:
        print(f"Error checking element visibility: {e}")
        return True  # Assume hidden if an error occurs

def sel_get_actionable_elements(driver, flag=None):
    """Get all actionable elements and their XPaths."""
    results = []
    actionable_xpath = ", ".join(actionable_selectors)  # CSS selector syntax
    elements = driver.find_elements(By.CSS_SELECTOR, actionable_xpath)

    for element in elements:
        # print(element.accessible_name)
        # if element.accessible_name == "Miami (FL)\n2,355 accommodations":
        #     print("reached")
        if flag=="exclude_hidden" and is_element_hidden(element):  # Skip hidden elements
            continue
        xpath = sel_get_element_xpath(element)
        if xpath:
            results.append({
                "tag_name": element.tag_name,
                "xpath": xpath,
                "text": (element.text.strip() if element.text
                     else element.get_attribute("aria-label")
                     if element.get_attribute("aria-label")
                     else element.get_attribute("alt")
                     if element.tag_name == "img"
                     else ""),
                "aria-label": (element.get_attribute("aria-label") if element.get_attribute("aria-label") else ""),
                "id": (element.get_attribute("id") if element.get_attribute("id") else ""),
                "href": (element.get_attribute("href") if element.get_attribute("href") else "")
            })

    div_elements_event_listeners = get_actionable_elements_with_listeners(driver)
    # for element in div_elements_event_listeners:
    #     print( element.tag_name, ", ", element.text)
    # print(len(div_elements_event_listeners), "done....")

    for element in div_elements_event_listeners:
        xpath = sel_get_element_xpath(element)
        if xpath:
            results.append({
                "tag_name": element.tag_name,
                "xpath": xpath,
                "text": element.text.strip(),
                "aria-label": (element.get_attribute("aria-label") if element.get_attribute("aria-label") else ""),
                "id": (element.get_attribute("id") if element.get_attribute("id") else ""),
                "href": (element.get_attribute("href") if element.get_attribute("href") else ""),
                "event_listener": "yes"
            })
    return results

def sel_write_actionable_elements_to_json(count_actionable_elements, elements, flag=None):
    file_path = os.path.join(tempfile.gettempdir(), "nvda\\xpath\\xpath_exclude_hidden_selenium.json")
    if flag != "exclude_hidden":
        file_path = os.path.join(tempfile.gettempdir(), "nvda\\xpath\\xpath_include_hidden_selenium.json")
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


def get_actionable_elements_with_listeners(driver):
    """Extract all actionable elements based on event listeners."""
    try:
        # JavaScript to get all elements with specific event listeners
        script = """
        const actionableElements = [];
        const allElements = document.querySelectorAll('*');
        
        function hasActionableChildren(element) {
            // List of actionable element tags
            const actionableTags = ['BUTTON', 'A', 'INPUT', 'SELECT', 'TEXTAREA'];
            
            // Check direct children for actionable elements
            const children = element.children;
            for (let child of children) {
                if (actionableTags.includes(child.tagName) || 
                    child.hasAttribute('role') || 
                    child.hasAttribute('tabindex') ||
                    hasActionableChildren(child)) {
                    return true;
                }
            }
            return false;
        }
        
        allElements.forEach(el => {
            
            // Check for JavaScript event listeners
            const events = ['click', 'mousedown', 'mouseup', 'keypress', 'touchstart', 'touchend'];
            let hasEventListener = false;
            for (const ev of events) {
                if (typeof el['on' + ev] === 'function') {
                    hasEventListener = true;
                    break;
                }
            }

            if (hasEventListener && el.tagName == "DIV") {
                // Check if element has actionable children
                if (!hasActionableChildren(el)) {
                    // Check visibility
                    const style = window.getComputedStyle(el);
                    const isVisible = style.display !== 'none' &&
                                      style.visibility !== 'hidden' &&
                                      style.opacity !== '0' &&
                                      el.offsetParent !== null &&
                                      el.offsetWidth > 0 &&
                                      el.offsetHeight > 0;
    
                    if (isVisible) {
                        actionableElements.push(el);  // Return the actual DOM element
                    }
                } 
            }
        });
        return actionableElements;
        """
        # Execute the script in the browser
        actionable_elements = driver.execute_script(script)
        return actionable_elements
    except Exception as e:
        print(f"Error finding actionable elements: {e}")
        return []
