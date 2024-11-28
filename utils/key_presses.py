import time
import keyboard

def simulate_tab():
    print("Simulating Tab key press...")
    keyboard.press_and_release('tab')

def simulate_enter():
    print("Simulating Enter key press...")
    keyboard.press_and_release('enter')
    time.sleep(7)


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
    keyboard.press('caps lock')
    keyboard.press_and_release('down arrow')
    keyboard.release('caps lock')
    time.sleep(3)  # Wait for the page to load

def simulate_up_arrow():
    print("Simulating Up arrow key press...")
    keyboard.press_and_release('caps lock + up arrow')
    #keyboard.press_and_release('up arrow')
    time.sleep(3)  # Wait for the page to load

def simulate_read_current_selected_text():
    print("Simulating Up arrow key press...")
    keyboard.press_and_release('caps lock + shift + up arrow')
    #keyboard.press_and_release('up arrow')
    time.sleep(3)  # Wait for the page to load

def simulate_down_arrow():
    print("Simulating Down arrow key press...")
    keyboard.press_and_release('caps lock + down arrow')
    #keyboard.press_and_release('down arrow')
    time.sleep(3)  # Wait for the page to load

def simulate_shift_down_arrow():
    print("Simulating Down arrow key press...")
    keyboard.press_and_release('shift + down arrow')
    #keyboard.press_and_release('down arrow')
    time.sleep(3)  # Wait for the page to load

def simulate_right_arrow():
    print("Simulating Right arrow key press...")
    keyboard.press_and_release('caps lock + right arrow')
    #keyboard.press_and_release('right arrow')
    time.sleep(3)  # Wait for the page to load

def simulate_left_arrow():
    print("Simulating Left arrow key press...")
    keyboard.press_and_release('caps lock + left arrow')
    #keyboard.press_and_release('left arrow')
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
