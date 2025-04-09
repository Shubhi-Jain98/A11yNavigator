import re
import tempfile
import os
import json
import time

from selenium.common import StaleElementReferenceException

from utils.get_count_actionable_elements import sel_write_actionable_elements_to_json, sel_get_actionable_elements
from utils.key_presses import simulate_space, simulate_enter, simulate_tab, focus_on_page_body
from utils.nvda import get_focused_element_role, wait_for_nvda_completion

CHECKBOX = "CHECKBOX"


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
            if current_elem['xpath'] == "":
                continue
            if i>0: # already processed this data, no need to do again
                prev_elem = elements_data[i-1]
                if current_elem['xpath'] == prev_elem['xpath']:
                    continue
            if "EDITABLETEXT" in current_elem['nvda_role']: # these elements require a written input to process
                continue
            if "LINK" in current_elem['nvda_role']: # Check if element is a link
                has_visited = any("VISITED" in state for state in current_elem['nvda_states'])
                if not has_visited:
                    if i < len(elements_data) - 1:  # Compare with next element if exists.
                        next_elem = elements_data[i + 1]
                        if current_elem['xpath'] == next_elem['xpath']: # this is non-navigating link, means a link that point to other element on same page. For this scenario, we are pressing TAB after ENTER
                            if is_similar_to_next_element(current_elem, next_elem):
                                actionability_issues.append(current_elem)
                        else: # this check is for pure links that opens a new page
                            actionability_issues.append(current_elem)
                    elif i == len(elements_data) - 1:
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
    with open(file_path_issues, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4)  # Pretty-print with 4 spaces


def perform_action_nvda_compare(driver, start_url, start_tabs):
    from main import get_current_url, get_number_of_tabs, focus_chrome
    try:
        focused_element_role = get_focused_element_role()
        if focused_element_role is not None and CHECKBOX in focused_element_role.split()[0]:
            simulate_space()
            time.sleep(2)
            simulate_tab()
            time.sleep(7)
        else:
            simulate_enter()
            time.sleep(7)
            current_url = get_current_url(driver)
            current_tabs = get_number_of_tabs(driver)

            if current_url != start_url or current_tabs != start_tabs:  # items where link changes
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
                    f.write(
                        "link worked")  # this link status will be populated in after_perform_action_element_data.json

            else:  # items not marked as links
                # this will also get hit for elements marked as LINK but url or number_of_tabs do not change. Example: "Skip to main content" links on main page
                focus_chrome()
                simulate_tab()
                time.sleep(3)
            # Return to original URL if current_url != start_url or still load page to undo any changes done to current element
            driver.get(start_url)
            return True
    except Exception as e:
        print(f"Error in perform_action nvda: {str(e)}")
        return False


def traverse_and_log_actionability_issues_second_iter(driver, focus_handler):
    from main import get_current_url, delete_all_cookies, get_number_of_tabs
    file_path = os.path.join(tempfile.gettempdir(), "nvda\\actionability\\actionability_issues_dom_compare.json") # this will contain data in format of xpath_exclude_hidden_selenium file
    try:
        with open(file_path, 'r', encoding="utf-8") as file:
            elements_data = json.load(file)
        focus_on_page_body()  # TRIALS
        start_url = get_current_url(driver)
        start_tabs = get_number_of_tabs(driver)
        loop = 0
        for element_data in elements_data['missing paths']:
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
            if xpath and xpath != "":
                try:
                    focused_element = focus_handler.focus_element_by_xpath(xpath)
                    if focused_element:
                        driver.execute_script("arguments[0].style.border = '3px solid blue';", focused_element)
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                                              focused_element)
                    # Verify focus
                    if focused_element is not None:
                        focus_handler.verify_focus(element_data, focused_element)

                    time.sleep(5)
                    perform_action_nvda_compare(driver, start_url, start_tabs)
                    time.sleep(3)
                except StaleElementReferenceException as e:
                    print(f"Stale element encountered: {str(e)}")
                except Exception as e:
                    print(f"Error processing element: {str(e)}")
                time.sleep(0.5)
    except Exception as e:
        print(f"Error processing elements: {str(e)}")

    log_actionability_issues()

