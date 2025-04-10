import json
import re
import tempfile
import os

from locatability_down_arrow import traverse_whole_website_down_arrow, log_down_arrow_locatability_issues, fetch_xpath
from locatability_single_key import traverse_whole_website_single_key, log_single_key_locatability_issues
from locatability_tab import traverse_website_and_extract_xpath_focussed_ele_and_extract_all_actionable_elements, \
    log_tab_locatability_issues

from utils.urls import default_url

URL = default_url


def log_issues(file_path_truth, file_path_logged, file_path_write, type):
    """
        Load JSON data from a given file path.
    """
    with open(file_path_truth, "r", encoding="utf-8") as file:
        all_xpaths_data = json.load(file)
    with open(file_path_logged, "r", encoding="utf-8") as file:
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
    # Display results
    if missing_xpaths:
        print("Missing XPaths", type, f"({len(missing_xpaths)}):")
        data = {
            "count of missing paths": len(missing_xpaths),
            "missing paths": list(sorted(missing_xpaths))
        }
        with open(file_path_write, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4)  # Pretty-print with 4 spaces

    else:
        print("No locatability issue.")
        data = {
            "count of missing paths": len(missing_xpaths),
            "missing paths": None
        }
        with open(file_path_write, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4)  # Pretty-print with 4 spaces


def clean_locatability_folder():
    from main import delete_specific_files
    file_path = os.path.join(tempfile.gettempdir(), "nvda\\locatability", "down_arrow_clickable.txt")
    delete_specific_files(file_path)
    file_path = os.path.join(tempfile.gettempdir(), "nvda\\locatability", "down_arrow_all_speech.txt")
    delete_specific_files(file_path)
    file_path = os.path.join(tempfile.gettempdir(), "nvda\\locatability", "down_arrow_locatability_issues.json")
    delete_specific_files(file_path)
    file_path = os.path.join(tempfile.gettempdir(), "nvda\\xpath", "xpaths_down_arrow.json")
    delete_specific_files(file_path)


def log_all_locatability_issues():
    def normalize_xpath(nor_xpaths):
        normalized_xpaths = set()  # Create a new set to store normalized XPaths
        for xpath in nor_xpaths:
            if xpath.startswith('/body'):
                xpath = '/html' + xpath
            xpath = re.sub(r'\[1\]', '', xpath)  # Remove [1] for first-level tags
            normalized_xpaths.add(xpath)  # Add the normalized XPath to the new set
        return normalized_xpaths

    file_path_tab = os.path.join(tempfile.gettempdir(), "nvda\\xpath\\xpath_focused_element.json")
    file_path_down_arrow = os.path.join(tempfile.gettempdir(), "nvda\\xpath\\xpaths_down_arrow.json")
    file_path_single_key = os.path.join(tempfile.gettempdir(), "nvda\\xpath\\single_key_xpath_focused_element.json")
    file_path_xpath = os.path.join(tempfile.gettempdir(), "nvda\\xpath\\xpath_exclude_hidden_selenium.json")
    file_path_issues = os.path.join(tempfile.gettempdir(), "nvda\\locatability\\all_locatability_issues.json")
    """
        Load JSON data from a given file path.
    """
    with open(file_path_xpath, "r", encoding="utf-8") as file:
        true_xpaths = json.load(file)
    with open(file_path_tab, "r", encoding="utf-8") as file:
        tab_logged = json.load(file)
    with open(file_path_down_arrow, "r", encoding="utf-8") as file:
        down_arrow_logged = json.load(file)
    with open(file_path_single_key, "r", encoding="utf-8") as file:
        single_key_logged = json.load(file)
    """
       Compare XPaths between the two JSON files and identify missing XPaths.
    """
    # Extract XPaths from all files
    true_xpaths = {entry["xpath"] for entry in true_xpaths["actionableElements"]}
    tab_logged_xpaths = {entry["xpath"] for entry in tab_logged}
    down_arrow_logged_xpaths = set()
    for headline, elements in down_arrow_logged.items():  # Iterate through each key (headline) in the JSON
        if elements:  # Extract XPaths, ignoring empty lists
            for element in elements:  # Add XPaths to the set (which automatically removes duplicates)
                down_arrow_logged_xpaths.add(element['xpath'])
    single_key_logged_xpaths = {entry["xpath"] for entry in single_key_logged}

    # normalize xpaths
    true_xpaths = normalize_xpath(true_xpaths)
    tab_logged_xpaths = normalize_xpath(tab_logged_xpaths)
    down_arrow_logged_xpaths = normalize_xpath(down_arrow_logged_xpaths)
    single_key_logged_xpaths = normalize_xpath(single_key_logged_xpaths)

    # Find missing XPaths
    missing_xpaths = true_xpaths - (tab_logged_xpaths | single_key_logged_xpaths | down_arrow_logged_xpaths)  # XPaths present in all_xpaths but not in nvda_xpaths
    # Display results
    print("Missing XPaths", type, f"({len(missing_xpaths)}):")
    data = {
        "count of missing paths": len(missing_xpaths),
        "missing paths": list(sorted(missing_xpaths))
    }
    with open(file_path_issues, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4)  # Pretty-print with 4 spaces



def find_locatability_issues(argv_two):
    print("Starting execution to find locatability issues")
    if argv_two == "tab":
        traverse_website_and_extract_xpath_focussed_ele_and_extract_all_actionable_elements() # traverse website to log each element data & get count of actionable elements
        log_tab_locatability_issues()
    elif argv_two == "down_arrow":
        # traverse_whole_website_down_arrow()
        fetch_xpath()
        log_down_arrow_locatability_issues()
    elif argv_two == "single_key":
        traverse_whole_website_single_key()
        log_single_key_locatability_issues()
    elif argv_two == "all":
        log_all_locatability_issues()
