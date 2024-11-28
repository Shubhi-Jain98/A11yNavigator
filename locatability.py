import json
import re
import tempfile
import os
import time

from utils.extract_xpath_focussed_element import extract_xpath_focussed_ele
from utils.get_count_actionable_elements import sel_write_actionable_elements_to_json, sel_get_actionable_elements
from utils.key_presses import simulate_tab, focus_on_page_body
from utils.nvda import get_focused_element_role, get_unique_id, get_focused_element_name
from utils.urls import default_url

URL = default_url


# traverse only actionable UI elements
def traverse_website_and_extract_xpath_focussed_ele_and_extract_all_actionable_elements():
    from main import connect_to_existing_chrome, get_actionable_elements_count
    driver = connect_to_existing_chrome()
    if not driver:
        print("No driver found.")
    start_title = driver.title
    print("start_title: ", start_title)
    count_actionable_elements = get_actionable_elements_count(driver) # uses selenium api
    sel_write_actionable_elements_to_json(count_actionable_elements, sel_get_actionable_elements(driver)) # write all actionable elements path to file

    visited_elements = set()  # List to keep track of visited elements
    count_actionable = 0
    focus_on_page_body()
    visited_same_elements_count = 0

    while True:
        simulate_tab()
        time.sleep(2)  # added time delay here
        focused_element_name = get_focused_element_name()
        ia2_unique_id = get_unique_id()
        extract_xpath_focussed_ele(driver, focused_element_name, ia2_unique_id) # extract xpath of currently focussed element

        if ia2_unique_id is None:
            continue

        if ia2_unique_id in visited_elements: # and count_actionable>=count_actionable_elements: # I think condition will be true only if there are no issues
            visited_same_elements_count += 1
            if count_actionable_elements<=70 and visited_same_elements_count >= count_actionable_elements: # implies that we have traversed the complete website >= twice for small websites
                break
            elif visited_same_elements_count >= 70: # for big websites, we are not traversing twice to save time
                break
        else:
            visited_elements.add(ia2_unique_id)
            count_actionable += 1
            #NVDA triggered that write data in file, later to be used by xpath
    name_role_file_path = os.path.join(tempfile.gettempdir(), "nvda\\nvda_xpath.log")
    with open(name_role_file_path, 'a') as file:
        file.write("\ntotal count_actionable_elements: "+str(count_actionable_elements)+", NVDA count_actionable_elements: "+str(count_actionable))
    print("total count_actionable_elements: ", count_actionable_elements, ", NVDA count_actionable_elements: ", count_actionable)


def log_locatability_issues():
    """
        Load JSON data from a given file path.
    """
    file_path = os.path.join(tempfile.gettempdir(), "nvda\\xpath\\xpath_all_selenium.json")
    with open(file_path, "r") as file:
        all_xpaths_data = json.load(file)
    file_path = os.path.join(tempfile.gettempdir(), "nvda\\xpath\\xpath_focused_element.json")
    with open(file_path, "r") as file:
        nvda_xpaths_data = json.load(file)
    """
       Compare XPaths between the two JSON files and identify missing XPaths.
    """
    # Extract XPaths from both files
    all_xpaths = {entry["xpath"] for entry in all_xpaths_data["actionableElements"]}
    nvda_xpaths = {entry["xpath"] for entry in nvda_xpaths_data}

    # Normalize all_xpaths
    normalized_xpaths = set()  # Create a new set to store normalized XPaths
    for xpath in all_xpaths:
        if xpath.startswith('/body'):
            xpath = '/html' + xpath
        xpath = re.sub(r'\[1\]', '', xpath)  # Remove [1] for first-level tags
        normalized_xpaths.add(xpath)  # Add the normalized XPath to the new set

    # Replace the old set with the normalized one if needed
    all_xpaths = normalized_xpaths

    # Find missing XPaths
    missing_xpaths = all_xpaths - nvda_xpaths  # XPaths present in all_xpaths but not in nvda_xpaths
    file_path = os.path.join(tempfile.gettempdir(), "nvda\\nvda_locatability_issue.json")
    # Display results
    if missing_xpaths:
        print(f"Missing XPaths ({len(missing_xpaths)}):")
        data = {
            "count of missing paths": len(missing_xpaths),
            "missing paths": list(sorted(missing_xpaths))
        }
        with open(file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)  # Pretty-print with 4 spaces

    else:
        print("No locatability issue.")
        data = {
            "count of missing paths": len(missing_xpaths),
            "missing paths": None
        }
        with open(file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)  # Pretty-print with 4 spaces



def find_locatability_issues():
    print("Starting execution to find locatability issues")
    traverse_website_and_extract_xpath_focussed_ele_and_extract_all_actionable_elements() # traverse website to log each element data & get count of actionable elements
    log_locatability_issues()




# traverse all UI elements
# def traverse_website():
#     from main import connect_to_existing_chrome, get_dom_structure, get_current_url, get_number_of_tabs
#     driver = connect_to_existing_chrome()
#     if driver:
#         start_url = get_current_url(driver)
#         start_tabs = get_number_of_tabs(driver)
#         start_dom = get_dom_structure(driver)
#         start_title = driver.title
#         print("start_title", start_title)
#     else:
#         print("No driver found.")
#
#     visited_elements = set()  # List to keep track of visited elements
#     all_visited = False
#     loop_start_id = None
#
#     time.sleep(10)
#     #focus_on_page_body()
#     #simulate_tab()
#     #switch_to_nvda_browse_mode() # Set NVDA to Browse mode
#     for i in range (2):
#         simulate_read_current_selected_text()
#     for i in range (2):
#         simulate_shift_down_arrow()
#     for i in range (2):
#         simulate_up_arrow()
#     for i in range (2):
#         simulate_down_arrow()
#     # for i in range (2):
#     #     simulate_left_arrow()
#     # for i in range (2):
#     #     simulate_right_arrow()
#     focus_on_title()
#     open_nvda_elements_list()