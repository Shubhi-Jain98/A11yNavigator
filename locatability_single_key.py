import tempfile
import os
import time

from utils.extract_xpath_focussed_element import extract_xpath_focussed_ele
from utils.get_count_actionable_elements import sel_write_actionable_elements_to_json, sel_get_actionable_elements
from utils.key_presses import simulate_k_link_key, simulate_shift_l_list_key, simulate_nvda_mode_change, \
    simulate_b_button_key, simulate_f_form_key, simulate_e_editable_key, simulate_x_checkbox_key, simulate_l_list_key, \
    simulate_i_listitem_key, simulate_r_radio_key, simulate_c_combobox_key, simulate_shift_k_link_key, \
    simulate_shift_b_button_key, simulate_shift_x_checkbox_key, simulate_shift_c_combobox_key, \
    simulate_shift_i_listitem_key, simulate_shift_f_form_key, simulate_shift_e_editable_key, simulate_shift_r_radio_key, \
    focus_on_page_body, simulate_tab, simulate_shift_tab
from utils.nvda import get_unique_id, get_focused_element_name, get_focused_element_value, get_focused_element_states


def traverse_whole_website_single_key():
    file_path = os.path.join(tempfile.gettempdir(), "nvda\\locatability\\nvda_mode.txt")
    os.makedirs(os.path.dirname(file_path), exist_ok=True) # Ensure directory exists
    if not os.path.exists(file_path): # Create file if it doesn't exist
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("")

    from main import get_current_url, connect_to_existing_chrome, get_actionable_elements_count
    driver = connect_to_existing_chrome()
    if not driver:
        print("No driver found.")
    start_title = driver.title
    start_url = get_current_url(driver)
    print("start_title: ", start_title)
    count_actionable_elements = get_actionable_elements_count(driver)  # uses selenium api
    print("count_elements: ", count_actionable_elements)
    # sel_write_actionable_elements_to_json(count_actionable_elements, sel_get_actionable_elements(driver, flag="exclude_hidden"), flag="exclude_hidden")  # write all actionable elements path to file

    # Create a list of function references
    single_keys_list = [simulate_k_link_key, simulate_shift_k_link_key, simulate_b_button_key, simulate_shift_b_button_key,
                        simulate_x_checkbox_key, simulate_shift_x_checkbox_key, simulate_r_radio_key, simulate_shift_r_radio_key,
                        simulate_c_combobox_key, simulate_shift_c_combobox_key, simulate_l_list_key, simulate_shift_l_list_key,
                        simulate_i_listitem_key, simulate_shift_i_listitem_key, simulate_f_form_key, simulate_shift_f_form_key,
                        simulate_e_editable_key, simulate_shift_e_editable_key]

    min_keypresses = {}
    for index, func in enumerate(single_keys_list):
        visited_elements = {}  # List to keep track of visited elements
        nvda_mode_restored = 0
        key_interaction = 0
        key_interaction_map = {}
        focus_on_page_body()
        while True:
            time.sleep(2)
            func()
            time.sleep(2)
            ia2_unique_id = get_unique_id()
            res_xpath = extract_xpath_focussed_ele(driver, key_interaction, "single_key", get_focused_element_name(), get_focused_element_value(),
                                       get_focused_element_states(), ia2_unique_id)  # extract xpath of currently focussed element
            if res_xpath:
                if res_xpath["xpath"] not in key_interaction_map or key_interaction_map[res_xpath["xpath"]] > key_interaction:
                    key_interaction += 1
                    key_interaction_map[res_xpath["xpath"]] = key_interaction
                    print(res_xpath["text"], "-", key_interaction)

            browse_focus_mode_text = ""
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as file:
                    lines = [line.strip() for line in file.readlines() if line.strip()]
                    if lines:
                        browse_focus_mode_text = lines[-1]
            if browse_focus_mode_text == "Focus_mode": # Focus mode will appear in file twice (i.e. after two keypresses), we need to handle them
                nvda_mode_restored += 1
                if nvda_mode_restored == 1:
                    simulate_nvda_mode_change()
                else:
                    nvda_mode_restored = 0

            if ia2_unique_id is None:
                continue

            visited_elements[ia2_unique_id] = visited_elements.get(ia2_unique_id, 0) + 1
            max_trials = 3
            if func == simulate_f_form_key or func == simulate_shift_f_form_key:
                max_trials = 8
            if visited_elements[ia2_unique_id] >= max_trials:
                print(f"Completed finding locatability issues. Break")
                break

        driver.get(start_url)
        # Update the global minimum keypresses after testing this key
        for xpath, keypresses in key_interaction_map.items():
            if xpath not in min_keypresses or min_keypresses[xpath] > keypresses:
                min_keypresses[xpath] = keypresses

    # average keypresses
    total_keypresses = 0
    for xpath, keypresses in min_keypresses.items():
        total_keypresses += keypresses  # Simply add the integer value
    print("Average number fo single key keypresses:", total_keypresses / len(min_keypresses) if min_keypresses else 0)

def log_single_key_locatability_issues():
    from locatability import log_issues

    log_issues(os.path.join(tempfile.gettempdir(), "nvda\\xpath\\xpath_exclude_hidden_selenium.json"),
               os.path.join(tempfile.gettempdir(), "nvda\\xpath\\single_key_xpath_focused_element.json"),
               os.path.join(tempfile.gettempdir(), "nvda\\locatability\\single_key_locatability_issue.json"),
               "exclude_hidden")