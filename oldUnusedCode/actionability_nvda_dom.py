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

                # Verify focus
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

    def perform_action(self, driver, start_url, start_tabs):
        from main import get_current_url, get_number_of_tabs, focus_chrome
        try:
            focused_element_role = get_focused_element_role()
            if focused_element_role is not None and CHECKBOX in focused_element_role.split()[0]:
                simulate_space()
                time.sleep(2)
                simulate_tab() # test
                time.sleep(7)
            else:
                simulate_enter()
                time.sleep(7)
                current_url = get_current_url(driver)
                current_tabs = get_number_of_tabs(driver)

                if current_url != start_url or current_tabs != start_tabs: # items where link changes
                    if current_tabs > start_tabs:
                        # Close any new tabs
                        for handle in driver.window_handles[1:]:
                            driver.switch_to.window(handle)
                            driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        time.sleep(2)
                        focus_chrome()
                    # elif focused_element_role is not None and focused_element_role != "LINK (19)": # for tabs, link may change by adding parameters #tabs...
                    #     focus_chrome()
                    #     simulate_tab()
                    #     time.sleep(3)
                    file_path = os.path.join(tempfile.gettempdir(),
                                             "nvda\\actionability\\is_link_working_element.txt")  # write link status to file
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write("link worked")  # this link status will be populated in after_perform_action_element_data.json

                else: # items not marked as links
                      # this will also get hit for elements marked as LINK but url or number_of_tabs do not change. Example: "Skip to main content" links on main page
                    focus_chrome()
                    simulate_tab() #test
                    time.sleep(3)
                # Return to original URL if current_url != start_url or still load page to undo any changes done to current element
                driver.get(start_url)
                return True
        except Exception as e:
            print(f"Error in perform_action: {str(e)}")
            return False


    def process_elements_from_file(self, driver):
        """
        Read elements from JSON file - nvda_all_focused_elements, and attempt to focus each one.
        Returns list of results with focus status.
        Final {name, value, states} is written by NVDA only
        """
        from main import get_current_url, get_number_of_tabs, delete_all_cookies
        results = []
        file_path = os.path.join(tempfile.gettempdir(), "nvda\\nvda_all_focused_elements.json")
        try:
            with open(file_path, 'r', encoding="utf-8") as file:
                elements_data = json.load(file)

            start_url = get_current_url(driver)
            start_tabs = get_number_of_tabs(driver)
            loop=0
            focus_on_page_body() # TRIALS
            for element_data in elements_data:
                loop+=1
                print("Finding & acting on ", loop, " UI element...")
                xpath = element_data.get('xpath')
                file_path = os.path.join(tempfile.gettempdir(), "nvda\\actionability\\xpath_focused_element.txt") # write xpath to file
                with open(file_path, "w") as f:
                    f.write(xpath) # this xpath will be populated in after_perform_action_element_data.json

                # delete_all_cookies(driver)

                if xpath:
                    try:
                        focused_element = self.focus_element_by_xpath(xpath)
                        # Verify focus
                        element_properties = None
                        focus_verification = None
                        if focused_element is not None:
                            # Store properties immediately after focusing
                            element_properties = {
                                'tag_name': focused_element.tag_name,
                                'text': focused_element.text,
                                'location': focused_element.location
                            }
                            focus_verification = self.verify_focus(element_data, focused_element)

                        time.sleep(5)
                        action_successful = self.perform_action(driver, start_url, start_tabs)
                        time.sleep(3)

                        result = {
                            'focus_successful': focused_element is not None,
                            'action_performed': action_successful if focused_element is not None else False,
                            'element_data': element_data,
                            'focused_element_properties': element_properties,
                            'focus_verification': focus_verification
                        }
                    except StaleElementReferenceException as e:
                        print(f"Stale element encountered: {str(e)}")
                        result = {
                            'focus_successful': True,  # It was focused before becoming stale
                            'element_data': element_data,
                            'focused_element_properties': element_properties if 'element_properties' in locals() else None,
                            'focus_verification': focus_verification if 'focus_verification' in locals() else None,
                            'action_performed': True,  # Element became stale likely due to successful action
                            'note': 'Element became stale after action'
                        }
                    except Exception as e:
                        print(f"Error processing element: {str(e)}")
                        result = {
                            'focus_successful': False,
                            'element_data': element_data,
                            'error': str(e)
                        }

                    results.append(result)
                    time.sleep(0.5)

        except Exception as e:
            print(f"Error processing elements: {str(e)}")

        return results

    def log_actionability_issues_second_iter(self, driver, start_url):
        from main import get_dom_structure, get_current_url, delete_all_cookies
        file_path = os.path.join(tempfile.gettempdir(), "nvda\\actionability\\actionability_issues.json")
        try:
            with open(file_path, 'r', encoding="utf-8") as file:
                elements_data = json.load(file)
            actionability_issues = []

            loop = 0
            for element_data in elements_data["missing paths"]:
                loop += 1
                print("Finding & acting on ", loop, " UI element...")
                xpath = element_data.get('xpath')
                # delete_all_cookies(driver)
                if xpath:
                    try:
                        focused_element = self.focus_element_by_xpath(xpath)
                        # Verify focus
                        if focused_element is not None:
                            self.verify_focus(element_data, focused_element)
                        time.sleep(3)
                        # 1. log start dom 2. Perform action 3. log final DOM 4. if same->log in actionability_second_iter issues
                        start_dom = get_dom_structure(driver)
                        focused_element_role = element_data.get('nvda_role')
                        if focused_element_role is not None and CHECKBOX in focused_element_role.split()[0]:
                            simulate_space()
                        else:
                            simulate_enter()
                        time.sleep(5)
                        after_dom = get_dom_structure(driver)
                        if start_dom == after_dom:
                            actionability_issues.append(element_data)
                        # theoretically, if our previous implementation if correct
                        # then no actionable item should be link here -> hence we are just getting to start_url and not closing any new tabs
                        driver.get(start_url)
                        time.sleep(5)
                    except StaleElementReferenceException as e:
                        print(f"Stale element encountered: {str(e)}")
                    except Exception as e:
                        print(f"Error processing element: {str(e)}")
                    time.sleep(0.5)

            file_path_issues = os.path.join(tempfile.gettempdir(),
                                     "nvda\\actionability\\actionability_issues_second_iter.json")
            if actionability_issues:
                print("Number of Actionability issues", len(actionability_issues))
                data = {
                    "count of actionability issues": len(actionability_issues),
                    "missing paths": list(actionability_issues)
                }
            else:
                print("No actionability issue.")
                data = {
                    "count of actionability issues": len(actionability_issues),
                    "missing paths": None
                }
            with open(file_path_issues, "w") as json_file:
                json.dump(data, json_file, indent=4)  # Pretty-print with 4 spaces

        except Exception as e:
            print(f"Error processing elements: {str(e)}")


def is_interactive_element(element):
    # Check for interactive states. Considering only TABS for now.
    # I guess this is true for TABS, RADIOBUTTONS as these are pre-selected
    interactive_states = {
        'SELECTABLE': 8388608,
        'SELECTED': 4,
        'MODAL': 262144
    }
    # Get element states as a list of numbers
    state_numbers = [
        int(state.split('(')[1].strip(')'))
        for state in element['nvda_states']
    ]
    # Check if any interactive states are present
    has_interactive_state = any(
        state_num in state_numbers
        for state_num in interactive_states.values()
    )
    return has_interactive_state


def is_similar_to_next_element(current_elem, next_elem):
    if current_elem['xpath'] == next_elem['xpath']:
        # removing the case where current things are pre-selected and need not be considered
        if "TAB" in current_elem['nvda_role'] and is_interactive_element(current_elem):
            return False
        # Check if any differences exist in name, value, or states
        if current_elem['nvda_name'] == next_elem['nvda_name']:
            if current_elem['nvda_value'] == next_elem['nvda_value']:
                if current_elem['nvda_states'] == next_elem['nvda_states']:
                    return True
    return False


def is_non_navigating_link(href): # href = nvda_value
    # Check for problematic patterns
    problematic_patterns = [
        # Internal anchors
        lambda h: h.startswith('#'),
        # JavaScript void
        lambda h: 'javascript:void' in h,
        # Empty or pound
        lambda h: h in ['#', ''],
    ]
    return any(pattern(href) for pattern in problematic_patterns)


def log_actionability_issues():
    file_path = os.path.join(tempfile.gettempdir(), "nvda\\actionability\\after_perform_action_element_data.json")
    actionability_issues = []
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding="utf-8") as file:
            elements_data = json.load(file)
        # Filter out entries where is_link_working is "link worked"
        elements_data = [
            entry for entry in elements_data
            if not (entry.get('is_link_working') == "link worked")
        ]
        for i in range(len(elements_data)):
            current_elem = elements_data[i]
            if i>0: # already processed this data, no need to do again
                prev_elem = elements_data[i-1]
                if current_elem['xpath'] == prev_elem['xpath']:
                    continue
            if "LINK" in current_elem['nvda_role']: # Check if element is a link
                has_visited = any("VISITED" in state for state in current_elem['nvda_states'])
                if not has_visited:
                    if i < len(elements_data) - 1:  # Compare with next element if exists
                        next_elem = elements_data[i + 1]
                        if current_elem['xpath'] == next_elem['xpath']: # this is non-navigating link, means a link that point to other element on same page. For this scenario, we are pressing TAB after ENTER
                            if is_similar_to_next_element(current_elem, next_elem):
                                actionability_issues.append(current_elem)
                        else: # this check is for pure links that opens a new page
                            actionability_issues.append(current_elem)
            else:
                if i < len(elements_data) - 1: # Compare with next element if exists
                    next_elem = elements_data[i + 1]
                    if is_similar_to_next_element(current_elem, next_elem) and "PROPERTYPAGE" not in current_elem['nvda_role'] :
                        actionability_issues.append(current_elem)
    file_path_issues = os.path.join(tempfile.gettempdir(), "nvda\\actionability\\actionability_issues.json")
    if actionability_issues:
        print("Number of Actionability issues", len(actionability_issues))
        data = {
            "count of actionability issues": len(actionability_issues),
            "missing paths": list(actionability_issues)
        }
    else:
        print("No actionability issue.")
        data = {
            "count of actionability issues": len(actionability_issues),
            "missing paths": None
        }
    with open(file_path_issues, "w") as json_file:
        json.dump(data, json_file, indent=4)  # Pretty-print with 4 spaces


def pre_traversal(driver):
    from main import get_actionable_elements_count, focus_chrome
    sel_write_actionable_elements_to_json(get_actionable_elements_count(driver), sel_get_actionable_elements(
        driver, flag="exclude_hidden"), flag="exclude_hidden")  # write all actionable elements path to file
    focus_chrome()
    simulate_tab()
    wait_for_nvda_completion()  # this is done to ensure nvda_all_focused_element.json is written by nvda


def traverse_website():
    from main import connect_to_existing_chrome
    print("Starting execution to find actionability issues...")
    driver = connect_to_existing_chrome()
    if not driver:
        print("No driver found.")

    # pre_traversal(driver)

    start_title = driver.title
    print("start_title: ", start_title)
    focus_handler = ElementFocusHandler(driver)

    # extract all elements information + xpath - nvda: fetch_focused_element_properties(api)
    results = focus_handler.process_elements_from_file(driver)
    file_path = os.path.join(tempfile.gettempdir(), "nvda\\actionability\\focused_element.json")
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(results, json_file, indent=4)  # Pretty-print with 4 spaces

def second_iter_to_verify_detected_issues():
    from main import connect_to_existing_chrome, get_current_url
    print("Starting execution to find actionability issues...")
    driver = connect_to_existing_chrome()
    if not driver:
        print("No driver found.")
    focus_handler = ElementFocusHandler(driver)
    start_url = get_current_url(driver)
    focus_handler.log_actionability_issues_second_iter(driver, start_url)


# Main function to focus Chrome and simulate key presses
def find_actionability_issues(argv):
    traverse_website()
    log_actionability_issues()
    second_iter_to_verify_detected_issues() # this used DOM to verify the logged actionability issues



