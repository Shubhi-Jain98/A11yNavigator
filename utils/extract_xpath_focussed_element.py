# this implementation uses javsacript script to get xpath of element currently focussed
import json
import os
import tempfile


def run_script_to_get_xpath(driver):
    # JavaScript function to compute XPath of the focused element
    script = """
    function getXPathAndText(element) {
        if (!element) return null;
        // Compute XPath
        var paths = [];
        for (; element && element.nodeType == 1; element = element.parentNode) {
            var index = 0;
            for (var sibling = element.previousSibling; sibling; sibling = sibling.previousSibling) {
                if (sibling.nodeType === Node.ELEMENT_NODE && sibling.nodeName === element.nodeName) {
                    ++index;
                }
            }
            var tagName = element.nodeName.toLowerCase();
            var pathIndex = (index ? `[${index + 1}]` : "");
            paths.unshift(tagName + pathIndex);
        }
        var xpath = paths.length ? "/" + paths.join("/") : null;
        
        // Get text content
        var text = element.textContent ? element.textContent.trim() : "";

        return { xpath, text };
    }
    return getXPathAndText(document.activeElement);
    """

    # Execute the script to get the XPath of the focused element
    result = driver.execute_script(script)
    return result


def write_to_file(result, focused_element_name, ia2_unique_id):
    if result:
        file_path = os.path.join(tempfile.gettempdir(), "nvda\\xpath\\xpath_focused_element.json")
        data = {
            "IA2UniqueID": ia2_unique_id,
            "nvda_name": focused_element_name,
            "xpath": result["xpath"],
        }
        try:
            if os.path.exists(file_path):
                with open(file_path, "r") as json_file:
                    existing_data = json.load(json_file)
            else:
                existing_data = []

            existing_data.append(data)
            with open(file_path, "w") as json_file:
                json.dump(existing_data, json_file, indent=4)  # Pretty-print with 4 spaces
                # print(f"XPath of the focused element successfully written to {file_path}")
        except Exception as e:
            print(f"Error writing to JSON file: {e}")
    else:
        print("No element is currently focused.")


def extract_xpath_focussed_ele(driver, focused_element_name, ia2_unique_id):
    result = run_script_to_get_xpath(driver)
    write_to_file(result, focused_element_name, ia2_unique_id)