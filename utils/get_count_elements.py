import tempfile
import os
import json
import asyncio
import pyppeteer

from fake_useragent import UserAgent  # Use this library for random User-Agents
from selenium.webdriver.common.by import By
from utils.urls import default_url

URL = default_url

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

def is_element_hidden_disabled(element):
    """Determine if an element is hidden."""
    try:
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
        return style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0' || 
               el.offsetParent === null || el.offsetWidth <= 0 || el.offsetHeight <= 0 ||
               el.disabled === true || el.getAttribute('disabled') !== null || el.getAttribute('aria-disabled') === 'true' || el.hasAttribute('disabled');
        """
        return element.parent.execute_script(script, element)
    except Exception as e:
        print(f"Error checking element visibility: {e}")
        return True  # Assume hidden if an error occurs

def sel_get_elements(driver, flag=None):
    """Get all elements and their XPaths."""
    results = []
    elements = driver.find_elements(By.CSS_SELECTOR, "*")

    for element in elements:
        if flag=="exclude_hidden" and is_element_hidden_disabled(element):  # Skip hidden elements
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
                     else "")
            })
    return results

def sel_write_elements_to_json(count_elements, elements, flag=None):
    file_path = os.path.join(tempfile.gettempdir(), "nvda\\xpath\\whole_xpath_exclude_hidden_selenium.json")
    if flag != "exclude_hidden":
        file_path = os.path.join(tempfile.gettempdir(), "nvda\\xpath\\whole_xpath_include_hidden_selenium.json")
    """Write elements and their count to a JSON file."""
    data = {
        "count by default selenium driver": count_elements,
        "total_count of below elements list": len(elements),
        "elements": elements
    }
    try:
        with open(file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)  # Pretty-print with 4 spaces
        print(f"Elements successfully written to {file_path}")
    except Exception as e:
        print(f"Error writing to JSON file: {e}")
