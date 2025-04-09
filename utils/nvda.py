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

def get_focused_element_value():
    file_path = os.path.join(tempfile.gettempdir(), "nvda\\nvda_focused_element.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)  # Load the JSON data into a dictionary

        # Access and print the "role" property
        value = data.get("value")
        if value:
            return value
        else:
            return None
    else:
        print("JSON file does not exist.")
        return None

def get_focused_element_states():
    file_path = os.path.join(tempfile.gettempdir(), "nvda\\nvda_focused_element.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)  # Load the JSON data into a dictionary

        # Access and print the "role" property
        states = data.get("states")
        if states:
            return states
        else:
            print("states does not exist in the data.")
            return None
    else:
        print("JSON file does not exist.")
        return None


def wait_for_nvda_completion():
    """
    Wait for NVDA to signal completion by writing 'done' to a file.
    """
    file_path = os.path.join(tempfile.gettempdir(), "nvda\\nvda_execution_status.txt")
    while True:
        # Check if the file exists
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                content = f.read().strip()

            # If file contains 'done', clear the file and exit the loop
            if content == "done":
                with open(file_path, "w") as f:
                    f.write("")  # Clear the file for future use
                print("NVDA execution completed...")
                return
        time.sleep(2)  # Wait 500ms before checking again

def wait_for_nvda_completion_with_timeout(timeout=5):
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
