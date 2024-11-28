import tempfile
import os
import json
import time

from bs4 import BeautifulSoup
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from locatability import log_locatability_issues
from utils.extract_xpath_focussed_element import run_script_to_get_xpath, write_to_file
from utils.key_presses import simulate_space, simulate_enter, go_back_to_previous_page_same_tab, \
    go_back_to_previous_page_diff_tab, simulate_tab, focus_on_page_body
from utils.nvda import get_unique_id, get_focused_element_role, get_focused_element_name, wait_for_nvda_completion

CHECKBOX = "CHECKBOX"


# Unused code: to extract code using chrome driver
def get_dom_from_driver(driver):
    from main import get_dom_structure
    start_dom = get_dom_structure(driver)

    fileName = os.path.join(tempfile.gettempdir(), "nvda\\nvda_dom.log")
    with open(fileName, 'w', encoding='utf-8') as file:
        file.write("\n Starting DOM: " + get_dom_structure(driver) + "\n")

    fileName = os.path.join(tempfile.gettempdir(), "nvda\\nvda_dom.json")
    # Parse the HTML DOM structure using BeautifulSoup
    soup = BeautifulSoup(start_dom, "html.parser")
    def parse_element(element):
        """Recursively parse an HTML element into a dictionary format."""
        element_dict = {
            "tag": element.name,
            "attributes": element.attrs,
            "children": [parse_element(child) for child in element.find_all(recursive=False)]
        }
        return element_dict
    # Assuming we want to parse the body of the DOM
    dom_dict = parse_element(soup.body)
    # Write to JSON file
    with open(fileName, 'w', encoding='utf-8') as file:
        json.dump(dom_dict, file, indent=4)


def get_count_of_elements_not_reachable(): # this implies locatability issues
    file_path = os.path.join(tempfile.gettempdir(), "nvda\\nvda_locatability_issue.json")
    with open(file_path, "r") as file:
        locatability_issues = json.load(file)
    # Extract count
    return locatability_issues["count of missing paths"]


def traverse_website_claude():
    from main import (
        connect_to_existing_chrome,
        get_dom_structure,
        get_current_url,
        get_number_of_tabs,
        get_actionable_elements_count,
        focus_chrome
    )

    # Constants
    MAX_WAIT_TIME = 10
    NAVIGATION_RETRY_COUNT = 3
    PAGE_LOAD_WAIT = 2

    def wait_for_page_load(driver):
        """Wait for the page to completely load."""
        try:
            WebDriverWait(driver, MAX_WAIT_TIME).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            time.sleep(PAGE_LOAD_WAIT)  # Additional buffer for dynamic content
        except TimeoutException:
            print("Page load timeout - continuing anyway")

    def ensure_window_focus(driver):
        """Ensure the Chrome window has focus."""
        try:
            driver.switch_to.window(driver.current_window_handle)
            ActionChains(driver).send_keys(Keys.ESCAPE).perform()  # Close any system dialogs
            focus_chrome()
            time.sleep(0.5)  # Small delay to ensure focus is set
        except Exception as e:
            print(f"Error ensuring window focus: {e}")

    def safe_navigation_back(driver, start_tabs, start_url):
        """Safely navigate back with retries."""
        for attempt in range(NAVIGATION_RETRY_COUNT):
            try:
                current_tabs = get_number_of_tabs(driver)

                if current_tabs > start_tabs:
                    # Handle new tab
                    driver.switch_to.window(driver.window_handles[0])
                    for handle in driver.window_handles[1:]:
                        driver.switch_to.window(handle)
                        driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                else:
                    # Handle same tab
                    driver.execute_script("window.history.go(-1)")
                    # Alternative: ActionChains(driver).key_down(Keys.ALT).send_keys(Keys.LEFT).key_up(Keys.ALT).perform()

                wait_for_page_load(driver)
                ensure_window_focus(driver)

                if get_current_url(driver) == start_url:
                    return True
            except Exception as e:
                print(f"Navigation attempt {attempt + 1} failed: {e}")
                time.sleep(1)
        # Fallback: Directly navigate to the start URL
        try:
            # print("All navigation attempts failed. Navigating directly to the start URL.")
            driver.get(start_url)
            wait_for_page_load(driver)
            ensure_window_focus(driver)

            if get_current_url(driver) == start_url:
                return True
        except Exception as e:
            print(f"Failed to load the start URL directly: {e}")
        return False

    # Initialize driver and get initial state
    driver = connect_to_existing_chrome()
    if not driver:
        print("No driver found.")
        return

    start_url = get_current_url(driver)
    start_tabs = get_number_of_tabs(driver)
    start_dom = get_dom_structure(driver)
    start_title = driver.title
    count_actionable_elements = get_actionable_elements_count(driver)
    print("start_title: ", start_title)

    # Initialize tracking variables
    visited_elements_xpath = set()
    count = 0
    focus_on_page_body()
    count_locatability_issue = get_count_of_elements_not_reachable()
    print("count_locatability_issue....", count_locatability_issue)

    automation_error = 0
    while True:
        try:
            print("visited_elements_xpath: ", len(visited_elements_xpath))
            ensure_window_focus(driver)
            simulate_tab()
            wait_for_nvda_completion() # added time delay here

            focused_element_role = get_focused_element_role()
            focused_element_name = get_focused_element_name()
            ia2_unique_id = get_unique_id()
            result_xpath = run_script_to_get_xpath(driver)
            write_to_file(result_xpath, focused_element_name, ia2_unique_id)

            print(len(visited_elements_xpath), "+", count_locatability_issue, ">=", count_actionable_elements, " & ", automation_error, ">=", 2*count_locatability_issue)
            if len(visited_elements_xpath) + count_locatability_issue >= count_actionable_elements and automation_error >= 2*count_locatability_issue:
                break

            if focused_element_role is not None:
                if result_xpath:
                    xpath = result_xpath["xpath"]
                    if xpath in visited_elements_xpath or xpath == "/html/body":
                        if xpath != "/html/body":
                            automation_error += 1
                        continue
                    else:
                        time.sleep(5)

                    visited_elements_xpath.add(xpath)
                    count += 1

                if CHECKBOX in focused_element_role.split()[0]:
                    simulate_space()
                else:
                    simulate_enter()
                    wait_for_page_load(driver)

                    current_url = get_current_url(driver)
                    current_dom = get_dom_structure(driver)

                    if start_url != current_url:
                        if not safe_navigation_back(driver, start_tabs, start_url):
                            print("Failed to navigate back after multiple attempts")
                            # break
                    else:
                        if start_dom == current_dom:
                            print("Dom is same, there might be accessibility issue.")
                        else:
                            print("All good.")

        except StaleElementReferenceException:
            print("Element became stale, continuing to next element")
            continue
        except Exception as e:
            print(f"Unexpected error: {e}")
            ensure_window_focus(driver)
            continue

    # update locatability issues list - 2nd update. If locatability script missed some issues, then will get updated here
    log_locatability_issues()


# Main function to focus Chrome and simulate key presses
def find_actionability_issues():
    print("Starting execution to find actionability issues...")
    from main import focus_chrome
    focus_chrome()  # Focus the Chrome window
    traverse_website_claude()







# old code unused
def traverse_website():
    from main import connect_to_existing_chrome, get_dom_structure, get_current_url, get_number_of_tabs, get_actionable_elements_count, focus_chrome
    driver = connect_to_existing_chrome()

    if driver:
        start_url = get_current_url(driver)
        start_tabs = get_number_of_tabs(driver)
        start_dom = get_dom_structure(driver)
        start_title = driver.title
        count_actionable_elements = get_actionable_elements_count(driver) # uses selenium api
        print("start_title: ", start_title)
        # print("get_actionable_elements_count: ", count_actionable_elements)
    else:
        print("No driver found.")


    # dummy_old_while_code()

    visited_elements_xpath = set()
    count = 0
    focus_on_page_body()
    count_locatability_issue = get_count_of_elements_not_reachable()
    print("count_locatability_issue....", count_locatability_issue)
    while True:
        print("visited_elements_xpath: ", len(visited_elements_xpath))
        simulate_tab()
        focused_element_role = get_focused_element_role()
        unique_id = get_unique_id()
        result_xpath = run_script_to_get_xpath(driver)

        if len(visited_elements_xpath)-count_locatability_issue >= count_actionable_elements: # in case of locatability issue, len will never be > count_actionable_elements
            break

        if focused_element_role is not None:
            if result_xpath:
                # xpath = result_xpath["xpath"]
                xpath = unique_id
                if xpath in visited_elements_xpath or xpath == "/html/body": # Check if the XPath is already in the set
                    continue
                else:
                    visited_elements_xpath.add(xpath)  # Add the XPath to the set
                    count += 1  # Increment count if it's a new element

            if CHECKBOX in focused_element_role.split()[0]:
                simulate_space()
            else:
                simulate_enter()
                current_url = get_current_url(driver)
                current_tabs = get_number_of_tabs(driver)
                current_dom = get_dom_structure(driver)
                if start_url != current_url:
                    if start_tabs == current_tabs:
                        # 1. If a new page is detected in same tab, go back
                        print("New page opened in same tab.", current_url)
                        go_back_to_previous_page_same_tab()
                        #focus_chrome()
                    else:
                        # 2. If a new page is detected in different tab, go back
                        print("New page opened in different tab.", current_url)
                        go_back_to_previous_page_diff_tab()
                        #focus_chrome()
                else:
                    # 3. Else some action occurred, keep tabbing through the elements
                    if start_dom == current_dom:
                        print("Dom is same, there might be accessibility issue.")
                    else:
                        print("All good.")
