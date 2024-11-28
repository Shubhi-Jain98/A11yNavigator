import tempfile
import os
import json
import time


def get_focused_element_role():
    file_path = os.path.join(tempfile.gettempdir(), "nvda\\nvda_focused_element.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)  # Load the JSON data into a dictionary

        # Access and print the "role" property
        role = data.get("role", "")  # Safely get the "role" property
        name = data.get("name")
        name = name if name is not None else ""
        if role:
            #print("Focused element: ", name + ", role: " + role.split()[0])  # Print only the role name
            return role
        else:
            print("Focused element Role does not exist in the data.")
            return None
    else:
        print("JSON file does not exist.")
        return None


def get_focused_element_name():
    file_path = os.path.join(tempfile.gettempdir(), "nvda\\nvda_focused_element.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)  # Load the JSON data into a dictionary

        # Access and print the "role" property
        name = data.get("name")
        return name if name is not None else ""
    else:
        print("JSON file does not exist.")
        return None


def get_unique_id():
    file_path = os.path.join(tempfile.gettempdir(), "nvda\\nvda_focused_element.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)  # Load the JSON data into a dictionary

        # Access and print the "role" property
        ia2_unique_id = data.get("IA2UniqueID")
        if ia2_unique_id:
            print("ia2_unique_id: ", ia2_unique_id)
            return ia2_unique_id
        else:
            print("ia2_unique_id does not exist in the data.")
            return None
    else:
        print("JSON file does not exist.")
        return None


def wait_for_nvda_completion(timeout=5):
    """
    Wait for NVDA to signal completion by writing 'done' to a file.
    :param timeout: Timeout in seconds to wait for NVDA completion.
    :raises TimeoutError: If NVDA does not signal completion within the timeout period.
    """
    file_path = os.path.join(tempfile.gettempdir(), "nvda\\nvda_execution_status.txt")
    start_time = time.time()
    while True:
        # Check if the file exists
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                content = f.read().strip()

            # If file contains 'done', clear the file and exit the loop
            if content == "done":
                with open(file_path, "w") as f:
                    f.write("")  # Clear the file for future use
                #print("NVDA execution completed.")
                return
        # Check for timeout
        if time.time() - start_time > timeout:
            raise TimeoutError("Timeout waiting for NVDA completion.")
        time.sleep(0.5)  # Wait 500ms before checking again















'''

def connect_to_nvda():
    # Connect to the NVDA application
    try:
        app = Application(backend="win32").connect(path="nvda_snapshot_source-master-383b204.exe")  # Use the appropriate path for NVDA
        print("Connected to NVDA.")
        return app
    except Exception as e:
        print(f"Error connecting to NVDA: {e}")
        return None


def get_focused_element(app):
    try:
        # Log all child elements of NVDA's main window
        window = app.window()
        all_elements = window.children()

        for element in all_elements:
            print(
                f"Element: {element.element_info.name}, Control type: {element.element_info.control_type}, Class: {element.element_info.class_name}")
    except Exception as e:
        print(f"Error logging NVDA elements: {e}")


def check_if_checkbox(focused_element):
    # Check if the element is a checkbox
    control_type = focused_element.element_info.control_type.lower()
    if "checkbox" in control_type:
        print("This is a checkbox.")
    else:
        print(f"This is not a checkbox, it is a {control_type}.")


# Main function
def nvda_main():
    app = connect_to_nvda()
    if app:
        focused_element = get_focused_element(app)
        if focused_element:
            check_if_checkbox(focused_element)
'''