import tempfile
import os
import json
import time
import traceback
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
                # Wait for element to be present and visible
                wait = WebDriverWait(self.driver, 10)
                element = wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))

                # First ensure the element is visible in viewport
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(1)  # Give more time for scroll and rendering

                # Check if element is interactable
                if not self.driver.execute_script("return arguments[0].offsetParent !== null", element):
                    print(f"Element at {xpath} is not interactable (hidden or has zero size)")
                    continue

                # Try to focus using JavaScript directly with error handling
                try:
                    self.driver.execute_script("""
                        try {
                            arguments[0].focus();
                            return true;
                        } catch(e) {
                            console.error('JS focus error:', e);
                            return false;
                        }
                    """, element)

                    # Verify if focus worked by checking document.activeElement
                    is_focused = self.driver.execute_script(
                        "return document.activeElement === arguments[0]", element)

                    if is_focused:
                        return element

                except Exception as js_error:
                    print(f"JavaScript focus error: {js_error}")

                # If JS focus fails, try click focusing with ActionChains
                try:
                    # Move to element with offset to avoid any overlays
                    action = ActionChains(self.driver)
                    action.move_to_element_with_offset(element, 1, 1).click().perform()
                    time.sleep(0.5)

                    # Verify focus
                    active_element = self.driver.switch_to.active_element
                    if active_element.id == element.id:
                        return element

                except Exception as click_error:
                    print(f"Click focus error: {click_error}")

                # Final attempt using tab navigation is less reliable, so let's improve it
                try:
                    # First click on a known good element (like body) to reset focus
                    self.driver.execute_script("document.body.focus()")

                    # Then use JavaScript to find the tab index position of our element
                    tab_sequence = self.driver.execute_script("""
                        let allElements = Array.from(document.querySelectorAll('*'));
                        return allElements.filter(el => 
                            el.tabIndex >= 0 && 
                            window.getComputedStyle(el).display !== 'none'
                        ).sort((a, b) => a.tabIndex - b.tabIndex);
                    """)

                    # Press tab a reasonable number of times (max 10)
                    for _ in range(10):
                        ActionChains(self.driver).send_keys(Keys.TAB).perform()
                        time.sleep(0.2)
                        active_element = self.driver.switch_to.active_element
                        if active_element.id == element.id:
                            return element

                except Exception as tab_error:
                    print(f"Tab navigation error: {tab_error}")

                # If we reach here, all focus methods failed for this attempt
                print(f"All focus methods failed for attempt {attempt + 1}")

            except StaleElementReferenceException:
                if attempt == max_attempts - 1:
                    print(f"Element at {xpath} remained stale after {max_attempts} attempts")
                else:
                    print(f"Stale element, retrying... (attempt {attempt + 1})")
                    time.sleep(1.5)  # Longer wait before retry

            except Exception as e:
                print(f"Error focusing element: {str(e)}")
                traceback.print_exc()  # Print full traceback for debugging

                if "ElementNotInteractableException" in str(e):
                    print("Element may be hidden or blocked by another element")

                # Try to get more information about the element
                try:
                    element_info = self.driver.execute_script("""
                        const el = arguments[0];
                        return {
                            tag: el.tagName,
                            id: el.id,
                            class: el.className,
                            isVisible: el.offsetParent !== null,
                            rect: el.getBoundingClientRect()
                        }
                    """, element)
                    print(f"Element info: {element_info}")
                except:
                    pass

                if attempt < max_attempts - 1:
                    continue
                else:
                    return None

        return None  # All attempts failed


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


def second_iter_to_verify_detected_issues(driver, focus_handler):
    start_title = driver.title
    print("start_title: ", start_title)

    # extract all elements xpath - xpath\\xpath_exclude_hidden_selenium.json
    results = process_elements_from_file(driver, focus_handler)
    file_path = os.path.join(tempfile.gettempdir(), "nvda\\actionability\\focused_element.json")
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(results, json_file, indent=4)  # Pretty-print with 4 spaces


def traverse_website(driver, focus_handler):
    # this file will be used by nvda to log issues, so clearing before starting execution of nvda code
    file_path = os.path.join(tempfile.gettempdir(), "nvda\\actionability\\after_perform_action_element_data.json")
    with open(file_path, 'w', encoding="utf-8") as file:
        json.dump([], file)
    file_path = os.path.join(tempfile.gettempdir(), "nvda\\actionability\\is_link_working_element.txt")  # write link status to file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("")
    file_path = os.path.join(tempfile.gettempdir(),  "nvda\\actionability\\xpath_focused_element.txt")  # write xpath to file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("")

    traverse_and_log_actionability_issues_second_iter(driver, focus_handler, "first")

    source_path = os.path.join(tempfile.gettempdir(), "nvda\\actionability\\after_perform_action_element_data.json")
    destination_path = os.path.join(tempfile.gettempdir(), "nvda\\actionability\\after_perform_action_element_data_first_iter.json")
    with open(source_path, 'r', encoding='utf-8') as src_file:
        data = json.load(src_file)
    with open(destination_path, 'w', encoding='utf-8') as dest_file:
        json.dump(data, dest_file, indent=2)
    with open(source_path, 'w', encoding="utf-8") as file:
        json.dump([], file)

    traverse_and_log_actionability_issues_second_iter(driver, focus_handler, "second")


# Main function to focus Chrome and simulate key presses
def find_actionability_issues(argv_two):
    from main import connect_to_existing_chrome, get_actionable_elements_count
    print("Starting execution to find actionability issues...")
    driver = connect_to_existing_chrome()
    if not driver:
        print("No driver found.")
    if argv_two == "pre":
        pre_traversal(driver)

    focus_handler = ElementFocusHandler(driver)
    sel_write_actionable_elements_to_json(get_actionable_elements_count(driver), sel_get_actionable_elements(
        driver, flag="exclude_hidden"), flag="exclude_hidden")  # write all actionable elements path to file
    traverse_website(driver, focus_handler) # this used NVDA {name, value, states} to verify the logged actionability issues