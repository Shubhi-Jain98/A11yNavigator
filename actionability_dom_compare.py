import re
import tempfile
import os
import json
import time

from selenium.common import StaleElementReferenceException

from utils.get_count_actionable_elements import sel_write_actionable_elements_to_json, sel_get_actionable_elements
from utils.key_presses import simulate_space, simulate_enter, simulate_tab, focus_on_page_body, simulate_up_arrow
from utils.nvda import get_focused_element_role, wait_for_nvda_completion

CHECKBOX = "CHECKBOX"
SPINBUTTON = "SPINBUTTON"

def perform_action_dom_compare(element_data, driver, start_url, start_tabs):
    is_link_working = None
    from main import get_current_url, get_number_of_tabs, focus_chrome, get_dom_structure
    try:
        focused_element_role = get_focused_element_role()
        start_dom = get_dom_structure(driver)
        if focused_element_role is not None and CHECKBOX in focused_element_role.split()[0]:
            simulate_space()
            time.sleep(2)
            after_dom = get_dom_structure(driver)
        elif focused_element_role is not None and SPINBUTTON in focused_element_role.split()[0]: # means the previous element in xpath list was spinbutton
            simulate_up_arrow()
            time.sleep(2)
            after_dom = get_dom_structure(driver)
        else:
            simulate_enter()
            time.sleep(2)
            after_dom  = get_dom_structure(driver)
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
                    is_link_working = "link worked"
            driver.get(start_url) # Return to original URL if current_url != start_url or still load page to undo any changes done to current element

        if is_link_working == "link worked":
            return True
        if start_dom == after_dom:
            print("DOM same...issue")
            return "issue"
        return True
    except Exception as e:
        print(f"Error in perform_action: {str(e)}")
        return False


def log_actionability_issues(actionability_issues):
    file_path = os.path.join(tempfile.gettempdir(), "nvda\\actionability\\actionability_issues_dom_compare.json")
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
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4)  # Pretty-print with 4 spaces


def process_elements_from_file(driver, focus_handler):
    """
    Read elements from JSON file - nvda_all_focused_elements, and attempt to focus each one.
    Returns list of results with focus status.
    Final {name, value, states} is written by NVDA only
    """
    from main import get_current_url, get_number_of_tabs, delete_all_cookies
    results = []
    file_path = os.path.join(tempfile.gettempdir(), "nvda\\xpath\\xpath_exclude_hidden_selenium.json")
    file_path_focus = os.path.join(tempfile.gettempdir(), "nvda\\actionability\\not_focused_element.json")
    try:
        with open(file_path, 'r', encoding="utf-8") as file:
            elements_data = json.load(file)

        start_url = get_current_url(driver)
        start_tabs = get_number_of_tabs(driver)
        loop=0
        focus_on_page_body() # TRIALS
        actionability_issues = []
        for element_data in elements_data['actionableElements']:
            # delete_all_cookies(driver)
            loop+=1
            print("Finding & acting on ", loop, " UI element...")
            xpath = element_data.get('xpath')
            if xpath.startswith('/body'):
                xpath = '/html' + xpath
            xpath = re.sub(r'\[1\]', '', xpath)  # Remove [1] for first-level tags
            file_path = os.path.join(tempfile.gettempdir(), "nvda\\actionability\\xpath_focused_element.txt") # write xpath to file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(xpath) # this xpath will be populated in after_perform_action_element_data.json
            if xpath:
                try:
                    focused_element = focus_handler.focus_element_by_xpath(xpath)
                    # Verify focus
                    element_properties = None
                    focus_verification = None
                    if focused_element is None:
                        with open(file_path_focus, "a", encoding="utf-8") as f:
                            f.write(xpath + '\n')  # this xpath will be populated in after_perform_action_element_data.json
                        continue
                    # Store properties immediately after focusing
                    element_properties = {
                        'tag_name': focused_element.tag_name,
                        'text': focused_element.text,
                        'location': focused_element.location
                    }
                    focus_verification = focus_handler.verify_focus(element_data, focused_element)

                    time.sleep(2)
                    action_successful = perform_action_dom_compare(element_data, driver, start_url, start_tabs)
                    if action_successful == "issue":
                        actionability_issues.append(element_data)
                    time.sleep(4)

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
                    actionability_issues.append(element_data)
                    result = {
                        'focus_successful': False,
                        'element_data': element_data,
                        'error': str(e)
                    }

                results.append(result)
                time.sleep(0.5)

        log_actionability_issues(actionability_issues)

    except Exception as e:
        print(f"Error processing elements: {str(e)}")

    return results


