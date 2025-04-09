import time
import keyboard
from selenium.webdriver import Keys

# NVDA COMMANDS GUIDE: chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/https://dequeuniversity.com/assets/pdf/screenreaders/nvda.pdf
# KEYBOARD DOCUMENT: https://pynput.readthedocs.io/en/latest/keyboard.html


def simulate_tab():
    print("Simulating Tab key press...")
    keyboard.press_and_release('tab')

def simulate_shift_tab():
    print("Simulating Shift + Tab key press...")
    keyboard.press_and_release('shift+tab')

def simulate_enter():
    print("Simulating Enter key press...")
    keyboard.press_and_release('enter')
    time.sleep(5)

def simulate_enter_new_tab():
    print("Simulating Ctrl+Enter key press for new tab...")
    keyboard.press('ctrl')  # Hold ctrl
    keyboard.press_and_release('enter')  # Press and release enter
    keyboard.release('ctrl')  # Release ctrl
    time.sleep(5)

def simulate_space():
    print("Simulating Space key press...")
    keyboard.press_and_release('space')
    time.sleep(2)

def go_back_to_previous_page_same_tab():
    print("Going back to the previous page...")
    keyboard.press_and_release('alt+left')
    time.sleep(5)  # Wait for the page to load


def go_back_to_previous_page_diff_tab():
    print("Going back to the previous page...")
    keyboard.press_and_release('ctrl+w')
    time.sleep(5)  # Wait for the page to load

def navigate_all():
    print("Navigating to all UI elements...")
    keyboard.press('ctrl')
    keyboard.press_and_release('down arrow')
    keyboard.release('ctrl')
    time.sleep(3)  # Wait for the page to load

def simulate_up_arrow():
    print("Simulating Home key press...numpad7 (prior line)")
    keyboard.press_and_release('home')

def simulate_read_current_selected_text():
    print("Simulating Up arrow key press...")
    keyboard.press_and_release('caps lock + shift + up arrow')
    #keyboard.press_and_release('up arrow')
    time.sleep(3)  # Wait for the page to load

def simulate_down_arrow():
    print("Simulating Down arrow key press...numpad9 (next line)")
    keyboard.press_and_release('page_up')

def simulate_shift_down_arrow():
    print("Simulating Down arrow key press...")
    keyboard.press_and_release('shift + down arrow')
    #keyboard.press_and_release('down arrow')
    time.sleep(3)  # Wait for the page to load

def simulate_right_arrow(driver):
    print("Simulating Right arrow key press...")
    # keyboard.press_and_release('caps lock + right arrow')
    # keyboard.press_and_release('right')
    element = driver.switch_to.active_element
    element.send_keys(Keys.ARROW_RIGHT)
    time.sleep(3)  # Wait for the page to load

def simulate_left_arrow():
    print("Simulating Left arrow key press...")
    # keyboard.press_and_release('caps lock + left arrow')
    keyboard.press_and_release('left arrow')
    time.sleep(3)  # Wait for the page to load

def switch_to_nvda_browse_mode():
    print("Switching NVDA to Browse mode...")
    keyboard.press('caps lock')
    keyboard.press_and_release('space')
    keyboard.release('caps lock')
    time.sleep(3)

def focus_on_title():
    print("Focusing on document title...")
    keyboard.press_and_release('caps lock+t')  # Focus on the document title
    time.sleep(3)

def open_nvda_elements_list():
    print("Opening NVDA Elements List...")
    keyboard.press_and_release('caps lock+f7')
    time.sleep(5)


def focus_on_page_body():
    print("Setting focus to the page body...")
    # Press 'Ctrl+Home' to move to the top of the page, focusing the body content
    keyboard.press_and_release('ctrl+home')
    time.sleep(2)


def simulate_nvda_mode_change():
    print("Changing nvda mode...")
    keyboard.press_and_release('caps lock + space')
    time.sleep(3)

def simulate_k_link_key():
    print("Simulating k (link) key press...")
    keyboard.press_and_release('k')

def simulate_f_form_key():
    print("Simulating f (form) key press...")
    keyboard.press_and_release('f')

def simulate_b_button_key():
    print("Simulating b (button) key press...")
    keyboard.press_and_release('b')

def simulate_e_editable_key():
    print("Simulating e (editable) key press...")
    keyboard.press_and_release('e')

def simulate_x_checkbox_key():
    print("Simulating x (Check box) key press...")
    keyboard.press_and_release('x')

def simulate_r_radio_key():
    print("Simulating r (radio button) key press...")
    keyboard.press_and_release('r')

def simulate_c_combobox_key():
    print("Simulating c (combobox) key press...")
    keyboard.press_and_release('c')

def simulate_l_list_key():
    print("Simulating l (list) key press...")
    keyboard.press_and_release('l')

def simulate_i_listitem_key():
    print("Simulating i (list item) key press...")
    keyboard.press_and_release('i')

def simulate_shift_k_link_key():
    print("Simulating shift+k (link) key press...")
    keyboard.press_and_release('shift+k')

def simulate_shift_f_form_key():
    print("Simulating shift+f (form) key press...")
    keyboard.press_and_release('shift+f')

def simulate_shift_b_button_key():
    print("Simulating shift+b (button) key press...")
    keyboard.press_and_release('shift+b')

def simulate_shift_e_editable_key():
    print("Simulating shift+e (editable) key press...")
    keyboard.press_and_release('shift+e')

def simulate_shift_x_checkbox_key():
    print("Simulating shift+x (Check box) key press...")
    keyboard.press_and_release('shift+x')

def simulate_shift_r_radio_key():
    print("Simulating shift+r (radio button) key press...")
    keyboard.press_and_release('shift+r')

def simulate_shift_c_combobox_key():
    print("Simulating shift+c (combobox) key press...")
    keyboard.press_and_release('shift+c')

def simulate_shift_l_list_key():
    print("Simulating shift+l (list) key press...")
    keyboard.press_and_release('shift+l')

def simulate_shift_i_listitem_key():
    print("Simulating shift+i (list item) key press...")
    keyboard.press_and_release('shift+i')