import shutil
import subprocess
import os
import time

import requests
from urllib.parse import urlparse
import distutils.dir_util

from main import main_func


def run_all_steps(url_to_open):
    # -------- Step 1: Launch Chrome with remote debugging --------
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    user_data_dir = r"C:\chrome_temp"
    chrome_command = f'"{chrome_path}" --remote-debugging-port=9222 --user-data-dir="{user_data_dir}" "{url_to_open}"'
    chrome_proc = subprocess.Popen(chrome_command, shell=True)
    print("[✓] Chrome launched.")
    time.sleep(5)

    # -------- Step 2: Launch NVDA -------- WILL DO MANUALLY
    # nvda_executable = r"C:\Program Files (x86)\NVDA\nvda.exe"  # Update path if needed
    # nvda_proc = subprocess.Popen(nvda_executable)
    # print("[✓] NVDA launched.")
    # time.sleep(5)  # Let NVDA initialize

    # -------- Step 3: Run your automation script --------
    main_func()
    print("[✓] Automation script executed.")

    # -------- Step 4: Copy data from one folder to another --------
    source_folder = r"C:\Users\jains\AppData\Local\Temp\nvda\xpath"
    parsed_url = urlparse(url_to_open)                  # Get domain from URL
    domain = parsed_url.netloc                          # if url_to_open="https://www.live.com" this will give 'www.live.com'
    domain = domain.replace('www.', '')
    destination_base = r"D:\my_docs\UCI\Research\Spring24\WebImpl\Website_logs_interactions_auto\html_paths"
    destination_folder = os.path.join(destination_base, domain)
    os.makedirs(destination_folder, exist_ok=True)      # Ensure destination exists
    distutils.dir_util.copy_tree(source_folder, destination_folder)
    print("[✓] Data copied.")

    # -------- Step 5: Close Chrome --------
    # Connect to the remote debugging endpoint and get window info
    debug_url = "http://localhost:9222/json"
    try:
        tabs = requests.get(debug_url).json()
        for tab in tabs:
            if "webSocketDebuggerUrl" in tab:
                target_id = tab.get("id")
                close_url = f"http://localhost:9222/json/close/{target_id}"
                response = requests.get(close_url)
                if response.status_code == 200:
                    print(f"[✓] Closed Chrome tab with ID: {target_id}")
    except requests.exceptions.ConnectionError:
        print("[i] Chrome already closed or debugging server shut down.")
    except Exception as e:
        print(f"[!] Unexpected error while closing Chrome: {e}")

if __name__ == "__main__":
    urls = [
        "https://www.chase.com/",
        "https://www.capitalone.com/",
        "https://openai.com/",
        "https://www.stackoverflow.com",
        "https://www.fragrantica.com/",
        "https://genius.com/",
        "https://doubleclick.net/",
        "https://nih.gov/",
        "https://www.doordash.com/",
        "https://duckduckgo.com/",
        "https://www.wikipedia.org",
        "https://www.live.com",
        "https://discord.com/",
        "https://craiglist.org/",
        "http://adp.com/",
        "https://www.progressive.com/",
        "https://www.google.com",
        "https://zerodha.com/",
        "https://www.sciencedirect.com/",
        "https://www.agoda.com/",
        "https://www.formula1.com/",
        "https://www.usps.com/",
        "https://www.samsung.com/us/",
        "https://www.dmv.ca.gov/portal/",
        "https://www.makemytrip.com/",
        "https://www.irctc.co.in/nget/train-search",
        "https://www.youtube.com/",

    ]
    for url in urls:
        run_all_steps(url)
        time.sleep(5)
