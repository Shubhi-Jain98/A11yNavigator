import ast
import json
import re
import tempfile
import os
import time
from collections import defaultdict

import unicodedata
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


def find_input_for_label(driver, label_element):
    try:
        target_id = label_element.get_attribute("for")
        if target_id:
            input_element = driver.find_element(By.ID, target_id)
            return input_element
    except:
        return None


def handle_sibling_tags(driver, element, seen_xpaths, results, accessible_name):
    # Pattern 1: Handle label → input via `for`
    if element.tag_name.lower() == "label":
        input_element = find_input_for_label(driver, element)
        if input_element:
            input_xpath = sel_get_element_xpath(input_element)
            if input_xpath and input_xpath not in seen_xpaths:
                seen_xpaths.add(input_xpath)
                results.append({
                    "element": input_element,
                    "xpath": input_xpath,
                    "tag_name": input_element.tag_name,
                    "attributes": {
                        "role": input_element.get_attribute("role"),
                        "aria-label": input_element.get_attribute("aria-label"),
                        "name": input_element.get_attribute("name"),
                        "id": input_element.get_attribute("id"),
                        "placeholder": input_element.get_attribute("placeholder"),
                        "href": input_element.get_attribute("href") if input_element.get_attribute("href") else ""
                    }
                })
    # Pattern 2: label > div (text) + textarea (actionable)
    if element.tag_name.lower() == "label":
        try:
            child_divs = element.find_elements(By.TAG_NAME, "div")
            text_in_divs = " ".join([
                div.get_attribute("textContent").strip()
                for div in child_divs
                if div.get_attribute("textContent") and div.get_attribute("textContent").strip()
            ])
            if accessible_name in text_in_divs:
                textareas = element.find_elements(By.TAG_NAME, "textarea")
                for textarea in textareas:
                    input_xpath = sel_get_element_xpath(textarea)
                    if input_xpath and input_xpath not in seen_xpaths:
                        seen_xpaths.add(input_xpath)
                        results.append({
                            "element": textarea,
                            "xpath": input_xpath,
                            "tag_name": textarea.tag_name,
                            "attributes": {
                                "role": textarea.get_attribute("role"),
                                "aria-label": textarea.get_attribute("aria-label"),
                                "name": textarea.get_attribute("name"),
                                "id": textarea.get_attribute("id"),
                                "placeholder": textarea.get_attribute("placeholder"),
                                "href": textarea.get_attribute("href") if textarea.get_attribute("href") else ""
                            }
                        })
        except:
            pass
    # Pattern 3: div > div (text) + a/button/input
    if element.tag_name.lower() == "div":
        try:
            child_divs = element.find_elements(By.TAG_NAME, "div")
            text_in_divs = " ".join([div.text.strip() for div in child_divs if div.text.strip()])
            if accessible_name.lower() in text_in_divs.lower():
                # Look for actionable elements in the same container
                actionables = element.find_elements(By.XPATH, ".//a | .//button | .//input | .//textarea")
                for act in actionables:
                    act_xpath = sel_get_element_xpath(act)
                    if act_xpath and act_xpath not in seen_xpaths:
                        seen_xpaths.add(act_xpath)
                        results.append({
                            "element": act,
                            "xpath": act_xpath,
                            "tag_name": act.tag_name,
                            "attributes": {
                                "role": act.get_attribute("role"),
                                "aria-label": act.get_attribute("aria-label"),
                                "name": act.get_attribute("name"),
                                "id": act.get_attribute("id"),
                                "placeholder": act.get_attribute("placeholder"),
                                "href": act.get_attribute("href") if act.get_attribute("href") else ""
                            }
                        })
        except:
            pass


def find_element_by_accessible_name(driver, accessible_name):
    """
    Find an element by its accessible name (what screen readers would announce)
    and return its XPath.
    """
    if accessible_name == "." or accessible_name == ",":
        return []
    if accessible_name.startswith("•") or accessible_name.endswith("•"): # for names that have bullet, example genius.com
        accessible_name = accessible_name.strip("•").strip()
    # Try various attributes that contribute to accessible name
    potential_elements = []

    # Uppercase matches where text-transform style is used in css to mark all text in caps
    if accessible_name.isupper():
        try:
            elements = driver.find_elements(By.XPATH, f"//*[translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='{accessible_name.lower()}']")
            potential_elements.extend(elements)
        except:
            pass

    # Case insensitive text content matching - this should catch the "Load More" div
    try:
        # Finds <span> elements whose text contains the name and are likely visually hidden (based on style or classes like sr-only).
        elements = driver.find_elements(By.XPATH, f"//span[normalize-space(text(), '{accessible_name}') and (contains(@style, 'clip:') or contains(@style, 'position: absolute') or contains(@class, 'sr-only') or contains(@class, 'visually-hidden'))]")
        potential_elements.extend(elements)
    except:
        pass

    try:
        # Look for the parent element of the hidden text (often the interactive element)
        elements = driver.find_elements(By.XPATH, f"//span[normalize-space(text(), '{accessible_name}')]/parent::*")
        potential_elements.extend(elements)
    except:
        pass

    try:
        # Finds anchor (<a>) elements containing a span with matching text.
        elements = driver.find_elements(By.XPATH, f"//a[.//span[normalize-space(text(), '{accessible_name}')]]")
        potential_elements.extend(elements)
    except:
        pass

    try:
        # Finds anchor tags whose visible text exactly matches accessible_name.
        elements = driver.find_elements(By.XPATH, f"//a[normalize-space(text())='{accessible_name}']")
        potential_elements.extend(elements)
    except:
        pass

    # Check input or button elements with matching value attribute
    try:
        elements = driver.find_elements(By.XPATH,  f"//input[@value='{accessible_name}'] | //button[@value='{accessible_name}']")
        potential_elements.extend(elements)
    except:
        pass

    # Check if the accessible_name is a substring of any href attribute in anchor tags
    try:
        # Find <a> elements where href is the accessible_name. This is useful for elements that has, no text, no aria-label and no id attribute. Example: duckduckgo #features
        elements = driver.find_elements(By.XPATH, f"//a[(@href, '{accessible_name}')]")
        potential_elements.extend(elements)
    except:
        pass

    # Check div elements specifically (common for fake buttons)
    try:
        elements = driver.find_elements(By.XPATH, f"//div[normalize-space(text())='{accessible_name}']")
        potential_elements.extend(elements)
    except:
        pass

    # Check span elements specifically (common for fake buttons)
    try:
        elements = driver.find_elements(By.XPATH, f"//span[normalize-space(text())='{accessible_name}']")
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
                        let name = el.getAttribute('aria-label') ||
                                   el.getAttribute('title') ||
                                   el.getAttribute('alt') || 
                                   el.getAttribute('placeholder') || '';
                        if (!name && el.innerText) {{
                            name = el.innerText.trim();
                        }}
                        if (!name && el.getAttribute('aria-labelledby')) {{
                            let label = document.getElementById(el.getAttribute('aria-labelledby'));
                            name = label ? label.innerText.trim() : '';
                        }}
                        if (!name && el.getAttribute('value')) {{
                            name = el.getAttribute('value');
                        }}
                        return name;
                    }}
                    
                    function normalize(str) {{
                        return str.replace(/\\s+/g, '');
                    }}
                    
                    function searchElements(root) {{
                        let matches = [];
                        let elements = root.querySelectorAll('*');
                        for (let el of elements) {{
                            try {{
                                let accessibleName = getAccessibleName(el);
                                if (normalize(accessibleName) === normalize("{accessible_name}")) {{
                                    matches.push(el);
                                }}
                            }} catch (e) {{}}
                        }}
                        return matches;
                    }}
                    
                    let results = searchElements(document);
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
    seen_xpaths = set()
    results = []
    for element in potential_elements:
        try:
            # Generate XPath using the existing function
            xpath = sel_get_element_xpath(element)
            if xpath and xpath not in seen_xpaths:
                seen_xpaths.add(xpath)
                results.append({
                    "element": element,
                    "xpath": xpath,
                    "tag_name": element.tag_name,
                    "attributes": {
                        "role": element.get_attribute("role"),
                        "aria-label": element.get_attribute("aria-label"),
                        "name": element.get_attribute("name"),
                        "id": element.get_attribute("id"),
                        "placeholder": element.get_attribute("placeholder"),
                        "href": element.get_attribute("href") if element.get_attribute("href") else ""
                    }
                })
            # Handle associated input field if it's a label
            handle_sibling_tags(driver, element, seen_xpaths, results, accessible_name)

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
    sel_write_actionable_elements_to_json(count_actionable_elements, sel_get_actionable_elements(driver, flag="exclude_hidden"), flag="exclude_hidden")  # write all actionable elements path to file
    focus_on_page_body()
    simulate_tab()
    while True:
        if are_last_n_lines_equal(os.path.join(tempfile.gettempdir(), "nvda\\locatability\\down_arrow_loop.txt")):
            break
        time.sleep(4)
        simulate_up_arrow()

    count_actionable = 0
    print(count_actionable, " ", count_elements)
    # while count_actionable <= count_elements:
    for i in range (20):
        time.sleep(2)
        simulate_down_arrow()
        count_actionable += 1
        time.sleep(4)  # added time delay here
        if count_actionable >=10 and are_last_n_lines_equal(os.path.join(tempfile.gettempdir(), "nvda\\locatability\\down_arrow_loop.txt")):
            break

5
# fetch xpath based on name, it includes "Pre-processing of lines" + "xpath extraction"
def fetch_xpath():
    from main import connect_to_existing_chrome
    driver = connect_to_existing_chrome()
    if not driver:
        print("No driver found.")
    start_title = driver.title
    print("start_title: ", start_title)

    exclude_words = ["out of list", "list", "link", "clickable", "link", "out of slide", "slide", "button", "graphic", "heading", "menu bar", "menu item", "menu button", "subMenu", "selected", "level 3", "level 2"]
    file_path_read = os.path.join(tempfile.gettempdir(), "nvda\\locatability", "down_arrow_all_speech.txt")
    unique_strings = defaultdict(list)
    merged_links = defaultdict(list) # to handle scenarios where NVDA announces name in two parts. Hence, to find a link for a name, we need to merge those two parts and then look for it. For reference see Chase website example
    parsed_lines = []  # First read all lines and parse them
    with open(file_path_read, 'r', encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            try:
                if line.startswith('[') and line.endswith(']'):
                    parsed_list = ast.literal_eval(line)
                    parsed_lines.append(parsed_list)
                else:
                    parsed_lines.append([line])
            except (SyntaxError, ValueError):
                parsed_lines.append([line])

    i = 0 # Now iterate line-by-line with index
    while i < len(parsed_lines):
        current = parsed_lines[i]
        # Check if current line ends with 'link' as second last and next line starts with 'link'
        if i + 1 < len(parsed_lines) and parsed_lines[i+1] != [] and len(current) >= 2 and current[-2] == 'link':
            if parsed_lines[i + 1][0] == 'link':
                first_text = current[-1]
                second_text = parsed_lines[i + 1][1].strip() if len(parsed_lines[i + 1]) > 1 else ''
                merged_links[first_text + second_text].append(i+1)
            else:
                j = 0 # Find the index of 'link' in next_line *after* skipping excluded leading words
                while j < len(parsed_lines[i + 1]) and parsed_lines[i + 1][j].strip() in exclude_words:
                    j += 1

                # Now check if the last word was 'link' (i.e. next_line[j-1] == 'link')
                if 0 < j < len(parsed_lines[i + 1]) and parsed_lines[i + 1][j - 1].strip() == 'link':
                    first_text = current[-1]
                    second_text = parsed_lines[i + 1][j]
                    merged_links[first_text + second_text].append(i+1)

        for item in current: # Otherwise, process normally
            item = item.strip()
            if item not in exclude_words:
                unique_strings[item].append(i+1)
        i += 1
    for merged, indices in merged_links.items():
        unique_strings[merged].extend(indices)

    print(f"Pre-processing done! Moving ahead for xpath extraction")
    results = {}
    for name, indices in unique_strings.items():
        if name == '':
            continue
        print(f"Processing: {name}")
        elements = find_element_by_accessible_name(driver, name)
        serializable_elements = []
        for element_info in elements:
            # Convert WebElement to serializable data
            serializable_element = {
                "xpath": element_info["xpath"],
                "tag_name": element_info["tag_name"],
                "attributes": element_info["attributes"],
                "number of keypresses": indices
            }
            serializable_elements.append(serializable_element)
        results[name] = serializable_elements
    output_json_path = os.path.join(tempfile.gettempdir(), "nvda\\xpath\\xpaths_down_arrow.json")
    with open(output_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(results, json_file, indent=2, ensure_ascii=False)


def log_down_arrow_locatability_issues():
    def normalize_name(name):
        if not name:
            return ""
        name = name.replace('\n', '').strip()
        # Normalize unicode (like converting 'Zelle®' to 'Zelle' by stripping special chars)
        name = unicodedata.normalize("NFKD", name)
        # Remove specific known symbols like ® (you can add more if needed)
        name = name.replace("®", "")
        # Collapse multiple spaces
        name = re.sub(r'\s+', ' ', name)
        return name.strip()

    try:
        # Define file paths
        selenium_file_path = os.path.join(tempfile.gettempdir(), "nvda\\xpath\\xpath_exclude_hidden_selenium.json")
        nvda_file_path = os.path.join(tempfile.gettempdir(), "nvda\\xpath\\xpaths_down_arrow.json")

        # Load JSON data
        with open(selenium_file_path, "r", encoding="utf-8") as file:
            selenium_xpaths_data = json.load(file)
        with open(nvda_file_path, "r", encoding="utf-8") as file:
            nvda_xpaths_data = json.load(file)

        # Extract XPaths
        selenium_xpaths = selenium_xpaths_data.get("actionableElements", [])
        unmatched_selenium_name_label = []
        matched_down_arrow = []   # Keep track of matched down_arrow xpaths

    # Step1: Compare Selenium elements with Down Arrow. We are checking only for name and aria-label match
        for sel_elem in selenium_xpaths:
            sel_name = sel_elem.get("text", "").strip()
            sel_aria_label = sel_elem.get("aria-label", "").strip()
            sel_xpath = sel_elem.get("xpath")

            # Normalize name for matching
            # sel_name_norm = sel_name.replace("\n", "").strip()
            sel_name_norm = normalize_name(sel_name)
            sel_aria_label_norm = normalize_name(sel_aria_label)

            matched = False
            for down_name, down_items in nvda_xpaths_data.items():
                # down_name_norm = down_name.replace("\n", "").strip()
                down_name_norm = normalize_name(down_name)
                if sel_name_norm == down_name_norm or sel_aria_label_norm == down_name_norm: # Matching both text and aria-label
                    for item in down_items:
                        if item.get("xpath") == sel_xpath:
                            matched = True
                            merged = dict(sel_elem)
                            merged['number_of_keypresses'] = item.get('number of keypresses', [])
                            matched_down_arrow.append(merged)
                            break                                               # from xpaths list
                    if matched: break                                           # from nvda_down_arrow list
            if not matched:
                unmatched_selenium_name_label.append(sel_elem)

        file_path_intermediate_issues = os.path.join(tempfile.gettempdir(), "nvda\\locatability\\down_arrow_intermediate_locatability_issues.json")
        data = {
            "count of missing paths": len(unmatched_selenium_name_label),
            "missing paths": unmatched_selenium_name_label if unmatched_selenium_name_label else None
        }
        with open(file_path_intermediate_issues, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4)

        print(f"{'Intermediate missing XPaths found after text+aria-label' if unmatched_selenium_name_label else 'No intermediate locatability issue after text+aria-label'} ({len(unmatched_selenium_name_label)})")

    # Step2: In this iteration, we will check for "id" and substring match with href for issues logged by above logic
        unmatched_selenium_id_href = []
        for sel_elem in unmatched_selenium_name_label:
            sel_id = sel_elem.get("id")
            sel_xpath = sel_elem.get("xpath")
            sel_href = sel_elem.get("href")
            matched = False
            for down_name, down_items in nvda_xpaths_data.items(): # iterate over all nvda logged names
                for item in down_items:                            # iterate over all xpaths of a name
                    down_id = item.get("attributes").get("id")
                    if sel_id != "" and sel_id == down_id and item.get("xpath") == sel_xpath:
                        matched = True
                        merged = dict(sel_elem)
                        merged['number_of_keypresses'] = item.get('number of keypresses', [])
                        matched_down_arrow.append(merged)
                        break                                               # from xpaths list
                if matched: break
            for down_name, down_items in nvda_xpaths_data.items(): # iterate over all nvda logged names
                for item in down_items:                            # iterate over all xpaths of a name
                    down_href = item.get("attributes").get("href")
                    if sel_href != "" and down_name in sel_href and sel_href == down_href:
                        matched = True
                        merged = dict(sel_elem)
                        merged['number_of_keypresses'] = item.get('number of keypresses', [])
                        matched_down_arrow.append(merged)
                        break
                if matched: break
            if not matched:
                unmatched_selenium_id_href.append(sel_elem)
        print( f"{'Intermediate missing XPaths found after id+href' if unmatched_selenium_id_href else 'No intermediate locatability issue after id+href'} ({len(unmatched_selenium_id_href)})")

    # Step3: Final substring xpath match
        # Step 3.1: Extract all XPaths from down_arrow.json
        nvda_all_full_xpaths = []
        for elements in nvda_xpaths_data.values():
            for element in elements:
                xpath = element.get("xpath", "")
                if xpath:
                    nvda_all_full_xpaths.append({
                        "xpath": xpath,
                        "number_of_keypresses": element.get("number of keypresses", [])
                    })
        # Step 3.2: Extract unmatched issue objects (not just xpath)
        unmatched_selenium = []
        for issue in unmatched_selenium_id_href:
            issue_xpath = issue["xpath"]
            match = next((item for item in nvda_all_full_xpaths if item.get("xpath") and issue_xpath in item["xpath"]), None)
            if match:
                matched_entry = dict(issue)
                matched_entry["number_of_keypresses"] = match.get("number_of_keypresses", [])
                matched_down_arrow.append(matched_entry)
            else:
                unmatched_selenium.append(issue)

        file_path_keypresses = os.path.join(tempfile.gettempdir(), "nvda\\locatability\\number_of_keypress.json")
        with open(file_path_keypresses, "w", encoding="utf-8") as json_file:
            json.dump(matched_down_arrow, json_file, indent=4)

    # Find unmatched down arrow entries
    #     unmatched_down_arrow = []
    #     for down_name, down_items in nvda_xpaths_data.items():
    #         for item in down_items:
    #             if (down_name, item["xpath"]) not in matched_down_arrow:
    #                 unmatched_down_arrow.append(item)
    # write issues to file
        file_path_issues = os.path.join(tempfile.gettempdir(), "nvda\\locatability\\down_arrow_locatability_issues.json")
        data = {
            "count of missing paths": len(unmatched_selenium),
            "missing paths": unmatched_selenium if unmatched_selenium else None
        }
        with open(file_path_issues, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4)
        print(f"{'Missing XPaths found' if unmatched_selenium else 'No locatability issue'} ({len(unmatched_selenium)})")

    # EXTRA: write issues by normalizing so that they could be highlighted easily
        normalized_xpaths = set()  # Create a new set to store normalized XPaths
        for sel_item in unmatched_selenium_name_label:
            xpath = sel_item.get("xpath")
            if xpath.startswith('/body'):
                xpath = '/html' + xpath
            xpath = re.sub(r'\[1\]', '', xpath)  # Remove [1] for first-level tags
            normalized_xpaths.add(xpath)  # Add the normalized XPath to the new set
        file_path_issues = os.path.join(tempfile.gettempdir(), "nvda\\locatability\\down_arrow_intermediate_issues_highlight.json")
        data = {
            "count of missing paths": len(normalized_xpaths),
            "missing paths": sorted(list(normalized_xpaths)) if normalized_xpaths else None
        }
        with open(file_path_issues, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4)


    except FileNotFoundError as e:
        print(f"Error: Could not find file: {e.filename}")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in one of the files")
    except Exception as e:
        print(f"Unexpected error occurred: {str(e)}")

def log_number_of_keypresses():
    file_path_keypresses = os.path.join(tempfile.gettempdir(), "nvda\\locatability\\number_of_keypress.json")
    with open(file_path_keypresses, "r", encoding="utf-8") as file:
        keypress_data = json.load(file)

    keypress_tracker = {} # Dictionary to track how many times we've seen each multi-entry list
    total_sum = 0
    for item in keypress_data:
        keypress_list = item.get("number_of_keypresses", [])
        key_tuple = tuple(keypress_list)    # Convert list to tuple (because lists can't be keys in dicts)
        if len(keypress_list) == 1:
            total_sum += keypress_list[0]
        elif len(keypress_list) > 1:
            count = keypress_tracker.get(key_tuple, 0)
            if count < len(keypress_list):
                total_sum += keypress_list[count]
            else:
                # If count exceeds list, pick the last value
                total_sum += keypress_list[-1]
            keypress_tracker[key_tuple] = count + 1

    print("Average number of keypresses:", total_sum/len(keypress_data))