import os
import tempfile

import pygetwindow as gw
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from locatability import find_locatability_issues
from actionability import find_actionability_issues
from websites.reddit import dynamic_pause
from websites.staticScroll import scrape_with_height_limit


def get_current_url(driver):
    return driver.current_url  # Return the current URL from the browser


# Get the number of tabs open in Chrome
def get_number_of_tabs(driver):
    return len(driver.window_handles)


# Get the DOM structure of the active tab
def get_dom_structure(driver):
    return driver.page_source


# Get the number of actionable elements (like links, buttons, input fields, etc.)
def get_actionable_elements_count(driver):
    actionable_elements = driver.find_elements(By.CSS_SELECTOR, "a, button, input, select, textarea, [role='button'], [role='link']")
    return len(actionable_elements)


# Connect to the existing Chrome session using remote debugging
def connect_to_existing_chrome():
    try:
        # Use webdriver_manager to automatically get the correct ChromeDriver version
        service = Service(ChromeDriverManager().install())

        options = webdriver.ChromeOptions()
        options.debugger_address = "localhost:9222"

        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        print(f"Error connecting to Chrome: {e}")
        return None

# Connect to the existing Chrome session using remote debugging
def connect_to_existing_chrome_old_code():
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")  # Connect to remote debugging

    # Set the path to your downloaded ChromeDriver
    service = Service(executable_path='C:\\chromedriver-win64\\chromedriver.exe')  # Adjust the path as necessary
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def focus_chrome():
    # Find and focus the Chrome window
    chrome_windows = [win for win in gw.getWindowsWithTitle('Chrome') if win.visible]
    if chrome_windows:
        chrome_window = chrome_windows[0]
        try:
            chrome_window.activate()  # Bring the first Chrome window to the front
            # print(f"Activated window: {chrome_window.title}")  # Debugging line
        except Exception as e:
            print(f"Error focusing window: {e}")
        time.sleep(3)  # Give the focus time to settle
    else:
        print("No visible Chrome window found.")


def delete_files_in_folder(folder_path):
    # Check if the folder exists
    if not os.path.exists(folder_path):
        print(f"Folder does not exist: {folder_path}")
        return
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")


def print_hi(name):
    print(f'Hi, {name}')


if __name__ == "__main__":
    # url = "https://www.reddit.com/"
    # scrape_with_height_limit(url, max_height=1000)

    delete_files_in_folder(os.path.join(tempfile.gettempdir(), "nvda\\")) # clear folder before starting
    delete_files_in_folder(os.path.join(tempfile.gettempdir(), "nvda\\xpath\\")) # clear folder before starting
    find_locatability_issues()
    time.sleep(8)
    find_actionability_issues()

    print_hi('Simulated key presses for NVDA')

