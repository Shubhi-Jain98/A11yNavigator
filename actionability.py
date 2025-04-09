import tempfile
import os
import json
import time
from turtledemo.penrose import start

from selenium.common import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from actionability_dom_compare import process_elements_from_file
from actionability_nvda_compare import traverse_and_log_actionability_issues_second_iter
from utils.get_count_actionable_elements import sel_write_actionable_elements_to_json, sel_get_actionable_elements
from utils.key_presses import simulate_space, simulate_enter, simulate_tab, focus_on_page_body
from utils.nvda import get_focused_element_role, wait_for_nvda_completion

CHECKBOX = "CHECKBOX"


class ElementFocusHandler:
    def __init__(self, driver):
        self.driver = driver

    def focus_element_by_xpath(self, xpath):
        """
        Focus an element using its XPath.
        Returns the focused element if successful, None otherwise.
        """
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                # Wait for element to be present
                wait = WebDriverWait(self.driver, 10)
                element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))

                # Scroll element into view
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(0.5)  # Allow time for scroll to complete

                # Try multiple focusing methods
                try:
                    # Method 1: Direct focus using JavaScript
                    self.driver.execute_script("arguments[0].focus();", element)
                except:
                    try:
                        # Method 2: Click to focus
                        ActionChains(self.driver).move_to_element(element).click().perform()
                    except:
                        try:
                            # Method 3: Send TAB key until element is focused
                            current_element = self.driver.switch_to.active_element
                            while current_element != element:
                                ActionChains(self.driver).send_keys(Keys.TAB).perform()
                                time.sleep(0.1)
                                current_element = self.driver.switch_to.active_element
                        except:
                            return None

                active_element = self.driver.switch_to.active_element
                return active_element if active_element == element else None

            except StaleElementReferenceException:
                if attempt == max_attempts - 1:  # Last attempt
                    print(f"Element at {xpath} remained stale after {max_attempts} attempts")
                    return None
                print(f"Stale element, retrying... (attempt {attempt + 1})")
                time.sleep(1)  # Wait before retry

            except Exception as e:
                print(f"Error focusing element: {str(e)}")
                return None


    @staticmethod
    def verify_focus(element_data, focused_element):
        """
        Verify if the focused element matches the expected properties from element_data.
        """
        try:
            # Get current element properties
            current_name = focused_element.get_attribute('aria-label') or focused_element.text
            current_value = focused_element.get_attribute('value')

            # Compare with expected properties
            name_matches = element_data['nvda_name'] in current_name if current_name else False
            value_matches = element_data['nvda_value'] == current_value

            return {
                'name_matches': name_matches,
                'value_matches': value_matches,
                'focused': 'FOCUSED (2)' in element_data['nvda_states']
            }

        except Exception as e:
            #print(f"Error verifying focus: {str(e)}")
            return None


def pre_traversal(driver):
    from main import get_actionable_elements_count, focus_chrome, delete_files_in_folder
    delete_files_in_folder(os.path.join(tempfile.gettempdir(), "nvda\\xpath\\"))
    sel_write_actionable_elements_to_json(get_actionable_elements_count(driver), sel_get_actionable_elements(
        driver, flag="exclude_hidden"), flag="exclude_hidden")  # write all actionable elements path to file
    focus_chrome()
    simulate_tab()
    wait_for_nvda_completion()  # this is done to ensure nvda_all_focused_element.json is written by nvda


def traverse_website(driver, focus_handler):
    start_title = driver.title
    print("start_title: ", start_title)

    # extract all elements xpath - xpath\\xpath_exclude_hidden_selenium.json
    results = process_elements_from_file(driver, focus_handler)
    file_path = os.path.join(tempfile.gettempdir(), "nvda\\actionability\\focused_element.json")
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(results, json_file, indent=4)  # Pretty-print with 4 spaces


def second_iter_to_verify_detected_issues(driver, focus_handler):
    # this file will be used by nvda to log issues, so clearing before starting execution of nvdea code
    file_path = os.path.join(tempfile.gettempdir(), "nvda\\actionability\\after_perform_action_element_data.json")
    with open(file_path, 'w', encoding="utf-8") as file:
        json.dump([], file)
    file_path = os.path.join(tempfile.gettempdir(), "nvda\\actionability\\is_link_working_element.txt")  # write link status to file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("")
    file_path = os.path.join(tempfile.gettempdir(),  "nvda\\actionability\\xpath_focused_element.txt")  # write xpath to file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("")
    traverse_and_log_actionability_issues_second_iter(driver, focus_handler)


# Main function to focus Chrome and simulate key presses
def find_actionability_issues(argv_two):
    from main import connect_to_existing_chrome
    print("Starting execution to find actionability issues...")
    driver = connect_to_existing_chrome()
    if not driver:
        print("No driver found.")
    if argv_two == "pre":
        pre_traversal(driver)

    focus_handler = ElementFocusHandler(driver)
    traverse_website(driver, focus_handler) # logs issues in nvda\\actionability\\actionability_issues_dom_compare.json
    second_iter_to_verify_detected_issues(driver, focus_handler) # this used NVDA {name, value, states} to verify the logged actionability issues



