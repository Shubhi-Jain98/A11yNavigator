import tempfile
import os
import time

from selenium.common import NoSuchElementException, StaleElementReferenceException

from utils.extract_xpath_focussed_element import extract_xpath_focussed_ele
from utils.get_count_actionable_elements import sel_write_actionable_elements_to_json, sel_get_actionable_elements
from utils.key_presses import simulate_tab, focus_on_page_body, simulate_enter, simulate_right_arrow, \
    simulate_shift_tab
from utils.nvda import get_focused_element_role, get_unique_id, get_focused_element_name, get_focused_element_value, get_focused_element_states


def get_currently_focused_element(driver):
    """Get the currently focused element with robust error handling"""
    try:
        return driver.switch_to.active_element
    except (StaleElementReferenceException, NoSuchElementException):
        return None


def is_dropdown_or_select(element):
    """
    Identify if the current element is a dropdown or select element
    """
    try:
        # Check for common dropdown/select indicators
        dropdown_indicators = [
            'select', 'dropdown', 'combobox',
            'aria-haspopup="listbox"', 'aria-expanded'
        ]

        element_classes = element.get_attribute('class')
        element_role = element.get_attribute('role')

        return any(indicator in str(element_classes).lower() or
                   indicator in str(element_role).lower()
                   for indicator in dropdown_indicators)
    except Exception:
        return False


# traverse only actionable UI elements using tab
def traverse_website_and_extract_xpath_focussed_ele_and_extract_all_actionable_elements():
    from main import connect_to_existing_chrome, get_actionable_elements_count
    driver = connect_to_existing_chrome()
    if not driver:
        print("No driver found.")
    start_title = driver.title
    print("start_title: ", start_title)

    count_actionable_elements = get_actionable_elements_count(driver) # uses selenium api
    sel_write_actionable_elements_to_json(count_actionable_elements, sel_get_actionable_elements(
        driver, flag="exclude_hidden"), flag="exclude_hidden") # write all actionable elements path to file
    # sel_write_actionable_elements_to_json(count_actionable_elements, sel_get_actionable_elements(
    #     driver))  # write all actionable elements path to file. this includes hidden as well

    visited_elements = set()  # List to keep track of visited elements
    count_actionable = 0
    focus_on_page_body()
    visited_same_elements_count = 0

    key_interactions = 0
    while True:
        time.sleep(4)
        simulate_tab()
        time.sleep(12)  # added time delay here

        focused_element_role = get_focused_element_role()
        ia2_unique_id = get_unique_id()
        extract_xpath_focussed_ele(driver, key_interactions, "tab", get_focused_element_name(), get_focused_element_value(), get_focused_element_states(), ia2_unique_id) # extract xpath of currently focussed element
        current_element = get_currently_focused_element(driver)  # Check if current element is a dropdown or select

        if ia2_unique_id is None:
            continue

        if focused_element_role == "TAB (22)" or focused_element_role == "RADIOBUTTON (6)":
            simulate_shift_tab()
            time.sleep(4)
            for i in range(6):
                simulate_right_arrow(driver)
                extract_xpath_focussed_ele(driver, key_interactions, "tab", get_focused_element_name(), get_focused_element_value(), get_focused_element_states(), get_unique_id())  # extract xpath of currently focussed element
                time.sleep(8)  # added time delay here
            simulate_tab()

        if ia2_unique_id in visited_elements: # and count_actionable>=count_actionable_elements: # I think condition will be true only if there are no issues
            visited_same_elements_count += 1
            if count_actionable_elements<=70 and visited_same_elements_count >= count_actionable_elements/2: # implies that we have traversed the complete website >= twice for small websites
                print("Completed finding locatability issues. Break visited_same_elements_count<=70")
                break
            elif visited_same_elements_count >= 70: # for big websites, we are not traversing twice to save time
                print("Completed finding locatability issues. Break visited_same_elements_count>=70")
                break
        else:
            key_interactions += 1
            visited_elements.add(ia2_unique_id)
            count_actionable += 1
            if is_dropdown_or_select(current_element):
                simulate_enter()
                # Once dropdown is open, traverse its items

            #NVDA triggered that write data in file, later to be used by xpath
    name_role_file_path = os.path.join(tempfile.gettempdir(), "nvda\\nvda_xpath.log")
    with open(name_role_file_path, 'a') as file:
        file.write("\ntotal count_actionable_elements: "+str(count_actionable_elements)+", NVDA count_actionable_elements: "+str(count_actionable))
    print("total count_actionable_elements: ", count_actionable_elements, ", NVDA count_actionable_elements: ", count_actionable)

def log_tab_locatability_issues():
    from locatability import log_issues

    log_issues(os.path.join(tempfile.gettempdir(), "nvda\\xpath\\xpath_exclude_hidden_selenium.json"),
               os.path.join(tempfile.gettempdir(), "nvda\\xpath\\xpath_focused_element.json"),
               os.path.join(tempfile.gettempdir(), "nvda\\locatability\\nvda_locatability_issue_exclude_hidden.json"), "exclude_hidden")

    # log_issues(os.path.join(tempfile.gettempdir(), "nvda\\xpath\\xpath_include_hidden_selenium.json"),
    #            os.path.join(tempfile.gettempdir(), "nvda\\xpath\\xpath_focused_element.json"),
    #            os.path.join(tempfile.gettempdir(), "nvda\\locatability\\nvda_locatability_issue_include_hidden.json"), "include_hidden")