import ast
import json
import re
import tempfile
import os
import time

from selenium.webdriver.common.by import By

from utils.get_count_actionable_elements import sel_get_element_xpath, sel_write_actionable_elements_to_json, \
    sel_get_actionable_elements
from utils.get_count_elements import sel_get_elements, sel_write_elements_to_json
from utils.key_presses import simulate_tab, focus_on_page_body, simulate_down_arrow, simulate_up_arrow


# Below code was generating too many false negatives. So removing this from workflow
def generate_xpath_to_interactive_tag(driver, element, results):
    interactive_tags = ['a', 'button', 'input', 'textarea', 'select']
    try:
        # Check parent
        parent = element.find_element(By.XPATH, '..')

        # Find all interactive elements within this parent
        for tag in interactive_tags:
            try:
                interactive_elements = parent.find_elements(By.TAG_NAME, tag)
                for interactive_element in interactive_elements:
                    interactive_xpath = sel_get_element_xpath(interactive_element)
                    # Add if it's not already in results
                    if not any(r.get('xpath') == interactive_xpath for r in results):
                        interactive_entry = {
                            "element": interactive_element,
                            "xpath": interactive_xpath,
                            "tag_name": interactive_element.tag_name,
                            "attributes": {
                                "role": interactive_element.get_attribute("role"),
                                "aria-label": interactive_element.get_attribute("aria-label"),
                                "name": interactive_element.get_attribute("name"),
                                "id": interactive_element.get_attribute("id"),
                                "placeholder": interactive_element.get_attribute("placeholder"),
                                "href": interactive_element.get_attribute("href") if tag == 'a' else None
                            },
                            "is_interactive": True,
                            "relation": "sibling_or_child"
                        }
                        results.append(interactive_entry)
            except:
                pass

        # Check if the element is inside a label, and if so, find associated form controls
        if element.tag_name.lower() == 'label' or parent.tag_name.lower() == 'label':
            label_element = element if element.tag_name.lower() == 'label' else parent

            # Try to find form control via 'for' attribute
            for_id = label_element.get_attribute('for')
            if for_id:
                try:
                    form_control = driver.find_element(By.ID, for_id)
                    control_xpath = sel_get_element_xpath(form_control)
                    # Add if it's not already in results
                    if not any(r.get('xpath') == control_xpath for r in results):
                        form_control_entry = {
                            "element": form_control,
                            "xpath": control_xpath,
                            "tag_name": form_control.tag_name,
                            "attributes": {
                                "role": form_control.get_attribute("role"),
                                "aria-label": form_control.get_attribute("aria-label"),
                                "name": form_control.get_attribute("name"),
                                "id": form_control.get_attribute("id"),
                                "placeholder": form_control.get_attribute("placeholder")
                            },
                            "is_interactive": True,
                            "relation": "label_for"
                        }
                        results.append(form_control_entry)
                except:
                    pass
    except:
        pass


def find_element_by_accessible_name(driver, accessible_name):
    """
    Find an element by its accessible name (what screen readers would announce)
    and return its XPath.
    """
    # Try various attributes that contribute to accessible name
    potential_elements = []
    # Case insensitive text content matching - this should catch the "Load More" div
    try:
        # Look for hidden spans with the exact text
        elements = driver.find_elements(By.XPATH, f"//span[contains(text(), '{accessible_name}') and (contains(@style, 'clip:') or contains(@style, 'position: absolute') or contains(@class, 'sr-only') or contains(@class, 'visually-hidden'))]")
        potential_elements.extend(elements)
    except:
        pass

    try:
        # Look for the parent element of the hidden text (often the interactive element)
        elements = driver.find_elements(By.XPATH, f"//span[contains(text(), '{accessible_name}')]/parent::*")
        potential_elements.extend(elements)
    except:
        pass

    try:
        # Look specifically for anchor tags that contain the hidden span
        elements = driver.find_elements(By.XPATH, f"//a[.//span[contains(text(), '{accessible_name}')]]")
        potential_elements.extend(elements)
    except:
        pass

    try:
        # Use case-insensitive text matching and look for both exact and containing matches
        elements = driver.find_elements(By.XPATH, f"//*[(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{accessible_name.lower()}')]")
        potential_elements.extend(elements)
    except:
        pass

    try:
        # Also try with normalize-space to handle whitespace issues
        elements = driver.find_elements(By.XPATH, f"//*[(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{accessible_name.lower()}')]")
        potential_elements.extend(elements)
    except:
        pass

    # Check div elements specifically (common for fake buttons)
    try:
        elements = driver.find_elements(By.XPATH, f"//div[normalize-space(text())='{accessible_name}' or contains(normalize-space(text()), '{accessible_name}')]")
        potential_elements.extend(elements)
    except:
        pass

    # Check span elements specifically (common for fake buttons)
    try:
        elements = driver.find_elements(By.XPATH, f"//span[normalize-space(text())='{accessible_name}' or contains(normalize-space(text()), '{accessible_name}')]")
        potential_elements.extend(elements)
    except:
        pass

    # Check elements with matching text content
    try:
        elements = driver.find_elements(By.XPATH, f"//*[normalize-space(text())='{accessible_name}']")
        potential_elements.extend(elements)
    except:
        pass

    escaped_name = accessible_name.replace("'", "', \"'\", '")  # Properly escape single quotes
    try:
        elements = driver.find_elements(By.XPATH, f"//*[normalize-space(text())=concat('{escaped_name}')]")
        potential_elements.extend(elements)
    except:
        pass

    try:
        # It extracts elements based on the accessibility tree, capturing hidden elements used for screen readers, like "Read article on WIRED Magazine".
        # Uses getComputedAccessibleName(el) (same as NVDA does!)
        # Searches aria-labelledby, aria-label, title, alt, innerText
        # Handles elements inside iframe
        script = f"""
                function getElementsByAccessibleName(name) {{
                    function getAccessibleName(el) {{
                        return el.getAttribute('aria-label') || 
                               el.getAttribute('title') || 
                               el.getAttribute('alt') || 
                               (el.innerText ? el.innerText.trim() : '') || 
                               (el.getAttribute('aria-labelledby') ? 
                                   document.getElementById(el.getAttribute('aria-labelledby'))?.innerText.trim() : '');
                    }}
                
                    function searchElements(root) {{
                        let matches = [];
                        let elements = root.querySelectorAll('*');
                        for (let el of elements) {{
                            try {{
                                let computedName = (window.getComputedAccessibleName ? window.getComputedAccessibleName(el) : '') || getAccessibleName(el);
                                if (computedName.toLowerCase() === name.toLowerCase()) {{
                                    matches.push(el);
                                }}
                            }} catch (e) {{}}
                        }}
                        return matches;
                    }}
                
                    let results = searchElements(document);
                    
                    // Handle iframes separately
                    let iframes = document.querySelectorAll('iframe');
                    for (let iframe of iframes) {{
                        try {{
                            let doc = iframe.contentDocument || iframe.contentWindow.document;
                            if (doc) {{
                                results = results.concat(searchElements(doc));
                            }}
                        }} catch (e) {{}}
                    }}
                
                    return results;
                }}
                
                return getElementsByAccessibleName("{accessible_name}");
                """

        elements = driver.execute_script(script)
        potential_elements.extend(elements)
    except:
        pass

    # Check elements with matching aria-label
    try:
        elements = driver.find_elements(By.XPATH, f"//*[@aria-label='{accessible_name}']")
        potential_elements.extend(elements)
    except:
        pass

    # Check elements with matching placeholder
    try:
        elements = driver.find_elements(By.XPATH, f"//*[@placeholder='{accessible_name}']")
        potential_elements.extend(elements)
    except:
        pass


    # Check elements with matching title
    try:
        elements = driver.find_elements(By.XPATH, f"//*[@title='{accessible_name}']")
        potential_elements.extend(elements)
    except:
        pass

    # Check elements with matching alt text (for images)
    try:
        elements = driver.find_elements(By.XPATH, f"//img[@alt='{accessible_name}']")
        potential_elements.extend(elements)
    except:
        pass

    # Check elements with matching name attribute
    try:
        elements = driver.find_elements(By.NAME, accessible_name)
        potential_elements.extend(elements)
    except:
        pass

    # Check labels pointing to form controls
    try:
        elements = driver.find_elements(By.XPATH, f"//label[normalize-space(text())='{accessible_name}']/..//input")
        potential_elements.extend(elements)
    except:
        pass

    # For each found element, generate its XPath
    results = []
    for element in potential_elements:
        try:
            # Generate XPath using the existing function
            xpath = sel_get_element_xpath(element)
            if xpath:
                results.append({
                    "element": element,
                    "xpath": xpath,
                    "tag_name": element.tag_name,
                    "attributes": {
                        "role": element.get_attribute("role"),
                        "aria-label": element.get_attribute("aria-label"),
                        "name": element.get_attribute("name"),
                        "id": element.get_attribute("id")
                    }
                })

            # generate_xpath_to_interactive_tag(driver, element, results)
        except:
            pass

    return results


def are_last_n_lines_equal(file_path, n=15):
    if os.path.exists(file_path):
        # Read all lines from the file
        with open(file_path, 'r', encoding="utf-8") as file:
            lines = file.readlines()

        if len(lines) < n: # Check if file has at least n lines
            return False

        last_n_lines = [line.strip() for line in lines[-n:]] # Get the last n lines
        return all(line == last_n_lines[0] for line in last_n_lines) # Check if all last n lines are equal


def traverse_whole_website_down_arrow():
    from main import connect_to_existing_chrome, get_elements_count, get_actionable_elements_count
    from locatability import clean_locatability_folder

    # clean_locatability_folder()
    driver = connect_to_existing_chrome()
    if not driver:
        print("No driver found.")
    start_title = driver.title
    print("start_title: ", start_title)
    count_elements = get_elements_count(driver) # uses selenium api
    # sel_write_elements_to_json(count_elements, sel_get_elements(driver, flag="exclude_hidden"), flag="exclude_hidden") # write all elements path to file

    count_actionable_elements = get_actionable_elements_count(driver)
    # sel_write_actionable_elements_to_json(count_actionable_elements,
    #                                       sel_get_actionable_elements(driver, flag="exclude_hidden"),
    #                                       flag="exclude_hidden")  # write all actionable elements path to file

    # focus_on_page_body()
    # simulate_tab()
    # while True:
    #     if are_last_n_lines_equal(os.path.join(tempfile.gettempdir(), "nvda\\locatability\\down_arrow_loop.txt")):
    #         break
    #     time.sleep(4)
    #     simulate_up_arrow()

    # count_actionable = 0
    # print(count_actionable, " ", count_elements)
    # while count_actionable <= count_elements:
    #     time.sleep(2)
    #     simulate_down_arrow()
    #     count_actionable += 1
    #     time.sleep(4)  # added time delay here
    #     if count_actionable >=10 and are_last_n_lines_equal(os.path.join(tempfile.gettempdir(), "nvda\\locatability\\down_arrow_loop.txt")):
    #         break

    # fetch xpath based on name
    file_path_read = os.path.join(tempfile.gettempdir(), "nvda\\locatability", "down_arrow_all_speech.txt")
    unique_strings = set()
    with open(file_path_read, 'r', encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            try:
                if line.startswith('[') and line.endswith(']'):
                    parsed_list = ast.literal_eval(line) # Parse the string as a Python list
                    for item in parsed_list:
                        unique_strings.add(item)
                else:
                    unique_strings.add(line)
            except (SyntaxError, ValueError):
                unique_strings.add(line)
    results = {}
    for name in unique_strings:
        print(f"Processing: {name}")
        elements = find_element_by_accessible_name(driver, name)
        serializable_elements = []
        for element_info in elements:
            # Convert WebElement to serializable data
            serializable_element = {
                "xpath": element_info["xpath"],
                "tag_name": element_info["tag_name"],
                "attributes": element_info["attributes"]
            }
            serializable_elements.append(serializable_element)
        results[name] = serializable_elements
    output_json_path = os.path.join(tempfile.gettempdir(), "nvda\\xpath\\xpaths_down_arrow.json")
    with open(output_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(results, json_file, indent=2, ensure_ascii=False)


def log_down_arrow_locatability_issues():
    """Load and compare XPath data from JSON files to identify missing XPaths."""
    def is_ancestor_or_equal_xpath(possible_ancestor, possible_descendant):
        """
        Check if one XPath is an ancestor of or equal to another XPath.
        Returns True if possible_ancestor is an ancestor of or equal to possible_descendant.
        """
        # Handle exact match
        if possible_ancestor == possible_descendant:
            return True
        # Check if ancestor is a prefix of descendant
        # We need to be careful about partial tag name matches, so check if:
        # 1. The ancestor is a prefix of the descendant
        # 2. The character after the prefix is a "/" (indicating it's truly a parent path)
        if possible_descendant.startswith(possible_ancestor) and (
                len(possible_descendant) == len(possible_ancestor) or
                possible_descendant[len(possible_ancestor)] == "/"):
            return True
        return False

    def find_matching_xpaths(interactive_xpaths, key_xpaths):
        """
        Find matches between interactive XPaths and name-based XPaths,
        considering hierarchical relationships.
        """
        missing_elements = set()
        for interactive_xpath in interactive_xpaths:
            has_match = False
            for key_xpath in key_xpaths:
                # Check if interactive XPath is represented by any key XPath
                # either as ancestor or descendant
                if is_ancestor_or_equal_xpath(interactive_xpath, key_xpath) or \
                        is_ancestor_or_equal_xpath(key_xpath, interactive_xpath):
                    has_match = True
                    break
            if not has_match:
                missing_elements.add(interactive_xpath)
        return missing_elements

    try:
        # Define file paths
        interactive_file_path = os.path.join(tempfile.gettempdir(), "nvda\\xpath\\xpath_exclude_hidden_selenium.json")
        key_file_path = os.path.join(tempfile.gettempdir(), "nvda\\xpath\\xpaths_down_arrow.json")

        # Load JSON data
        with open(interactive_file_path, "r", encoding="utf-8") as file:
            interactive_xpaths_data = json.load(file)
        with open(key_file_path, "r", encoding="utf-8") as file:
            key_xpaths_data = json.load(file)

        # Extract XPaths
        interactive_xpaths = {entry["xpath"] for entry in interactive_xpaths_data["actionableElements"]}
        key_xpaths = set()
        for headline, elements in key_xpaths_data.items(): # Iterate through each key (headline) in the JSON
            if elements: # Extract XPaths, ignoring empty lists
                for element in elements: # Add XPaths to the set (which automatically removes duplicates)
                    key_xpaths.add(element['xpath'])

        # Normalize interactive_xpaths
        normalized_interactive_xpaths = {
            '/html' + xpath if xpath.startswith('/body') else xpath
            for xpath in interactive_xpaths
        }
        normalized_interactive_xpaths = {
            re.sub(r'\[1\]', '', xpath) for xpath in normalized_interactive_xpaths
        }

        # Normalize key_xpaths
        normalized_key_xpaths = {
            '/html' + xpath if xpath.startswith('/body') else xpath
            for xpath in key_xpaths
        }
        normalized_key_xpaths = {
            re.sub(r'\[1\]', '', xpath) for xpath in normalized_key_xpaths
        }

        # Find missing XPaths using proper set operations
        missing_xpaths = find_matching_xpaths(normalized_interactive_xpaths, normalized_key_xpaths)

        # Write results
        file_path_issues = os.path.join(tempfile.gettempdir(), "nvda\\locatability\\down_arrow_locatability_issues.json")
        data = {
            "count of missing paths": len(missing_xpaths),
            "missing paths": list(sorted(missing_xpaths)) if missing_xpaths else None
        }
        with open(file_path_issues, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4)
        print(f"{'Missing XPaths found' if missing_xpaths else 'No locatability issue'} ({len(missing_xpaths)})")

    except FileNotFoundError as e:
        print(f"Error: Could not find file: {e.filename}")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in one of the files")
    except Exception as e:
        print(f"Unexpected error occurred: {str(e)}")