# A11yNavigator
This is the artifact of the paper "Automated Detection of Web Application Navigation Barriers for Screen Reader Users".
For the list of issues detected by our tool, please visit [issues_artifacts](https://anonymous.4open.science/r/A11yNavigator-942F/issues_artifacts/README.md)

## Prerequisites
### System Requirements
- **Operating System**: Windows (required for NVDA integration)
- **Python**: Python 3.7 or higher
- **Google Chrome**: Latest version
- **NVDA Screen Reader**: Version 2024.1

### Software Downloads
1. **Python**: Download from [python.org](https://www.python.org/downloads/)
2. **Google Chrome**: Download from [google.com/chrome](https://www.google.com/chrome/)
3. **NVDA**: Download from [nvaccess.org](https://www.nvaccess.org/download/?nvdaVersion=2024.1)


## Setup

### Step 1: Clone the Repository
```bash
git clone https://github.com/Shubhi-Jain98/A11yNavigator.git
cd A11yNavigator
```
Create a virtual environment in .env (python3 -m venv .env)

### Step 2: Install Python Dependencies
```bash
# Core dependencies
pip install selenium webdriver-manager
pip install keyboard

# Additional dependencies
pip install asyncio
pip install requests
```

### Step 3: ChromeDriver Setup
1. **Check Chrome Version**:
   - Open Google Chrome
   - Navigate to `chrome://settings/help`
   - Note down your Chrome version (e.g., 115.0.5790.99)

2. **Download ChromeDriver**:
   - Go to [ChromeDriver downloads](https://chromedriver.chromium.org/downloads)
   - Download the version matching your Chrome browser
   - Extract the `chromedriver.exe` file
   - Note the path where you saved it

3. **Update Configuration**:
   - Open `main.py` in your project
   - Find the `connect_to_existing_chrome()` method
   - Update the ChromeDriver path to match your installation

4. Update "chrome_path" in `run_all_steps.py` to reflect chrome installation path

### Step 4: NVDA Setup
To run NVDA to traverse websites and detect accessibility issues, please download and install NVDA version 2024.1 as mentioned above.
To use NVDA for the purpose described in our paper—to log NVDA announcements and element data—please follow the "Build NVDA" instructions below:
1**Build NVDA (for custom functionality)**:
   ```bash
   # Navigate to NVDA source directory
   cd path/to/nvda
   # Build NVDA
   scons launcher
   ```
   - This will create an executable at the specified output directory
   - Here is the repository link for the custom NVDA code: [NVDA code](https://anonymous.4open.science/r/nvda-8DC5/readme.md)


## Running A11yNavigator
1. Run NVDA custom build before running A11yNavigator tool
   1. Can either run from Run button inside IDE or can run command on cmd
   2. If cmd - build nvda project by running below command in terminal
      ```bash
      scons launcher
       ```
      Launches exe at _D:\my_docs\UCI\Research\Spring24\WebImpl\nvda\output_
2. The main entry point is `run_all_steps.py` which automates the entire process:
   1. For Locatability Analysis, please run below command based on navigation mode
      ```bash
      python run_all_steps.py locatability single_key # Single key shortcuts testing
      python run_all_steps.py locatability tab        # Tab navigation testing
      python run_all_steps.py locatability down_arrow # Arrow key navigation testing
      ```
   2. For Actionability Analysis, please run below command 
      ```bash
      python run_all_steps.py actionability none      # Interactive element testing
      ```
   
   **What this does automatically:**
   1. **Launches Chrome** with remote debugging on port 9222
   2. **Loads target websites** (predefined list of 26 websites)
   3. **Calls detection algorithms** for locatability and actionability issues
   4. **Manages file operations** (cleanup, data copying)
   5. **Closes Chrome** after each website analysis