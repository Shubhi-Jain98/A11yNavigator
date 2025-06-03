# A11yNavigator
This is the artifact of the paper "Automated Detection of Web Application Navigation Barriers for Screen Reader Users".

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
If you want to run the NVDA to traverse website and test issues, please feel free to download and install the NVDA version 2024.1 as mentioned above. 
If you want to use NVDA for the purpose we used in paper to log NVDA announcements and elements data, please follow "Build NVDA"
1. **Build NVDA (if using custom build)**:
   ```bash
   # Navigate to NVDA source directory
   cd path/to/nvda
   # Build NVDA
   scons launcher
   ```
   - This will create an executable at the specified output directory
   - [NVDA code](https://anonymous.4open.science/r/A11yNavigator-942F/)


## Running A11yNavigator
1. Run nvda so to run this script on nvda
   1. Can either run from Pycharm configurations or cmd
   2. If cmd- build nvda project by running below command in terminal
      ```
      scons launcher
       ```
      Launches exe at _D:\my_docs\UCI\Research\Spring24\WebImpl\nvda\output_
2. Run main.py of the keyPressControl script
      ```
      python main.py
      ```

### Quick Hacks
To highlight the element using xpath via Inspect tool -> Go to Console and type below command
 ```
      // Replace 'YOUR_XPATH_HERE' with your XPath
      const xpath = "YOUR_XPATH_HERE";
      const element = document.evaluate(
          xpath,
          document,
          null,
          XPathResult.FIRST_ORDERED_NODE_TYPE,
          null
      ).singleNodeValue;
      
      if (element) {
          element.style.border = "3px solid red"; // Highlight the element
          element.scrollIntoView({ behavior: "smooth", block: "center" }); // Scroll into view
          console.log("Element found and highlighted:", element);
      } else {
          console.log("No element found for the given XPath.");
      }
 ```
To highlight the elements using xpath list via Inspect tool -> Go to Console and type below command
```
   function highlightElementsByXPaths(xpaths, borderStyle = "3px solid red", scrollToFirst = true) {
     let foundCount = 0;
     let firstFoundElement = null;
     
     // Process each XPath in the list
     xpaths.forEach((xpath, index) => {
       try {
         const element = document.evaluate(
           xpath,
           document,
           null,
           XPathResult.FIRST_ORDERED_NODE_TYPE,
           null
         ).singleNodeValue;
         
         if (element) {
           // Highlight the element
           element.style.border = borderStyle;
           
           // Save the first found element for scrolling later
           if (foundCount === 0) {
             firstFoundElement = element;
           }
           
           console.log(`Element #${index + 1} found and highlighted:`, element);
           foundCount++;
         } else {
           console.log(`No element found for XPath #${index + 1}: ${xpath}`);
         }
       } catch (error) {
         console.error(`Error processing XPath #${index + 1}: ${xpath}`, error);
       }
     });
     
     // Scroll to the first found element if requested and any were found
     if (scrollToFirst && firstFoundElement) {
       firstFoundElement.scrollIntoView({ behavior: "smooth", block: "center" });
     }
     
     console.log(`Total elements highlighted: ${foundCount} out of ${xpaths.length}`);
     return foundCount;
   }
   
   // Example usage:
   const xpathList = [
   
   ];
   
   highlightElementsByXPaths(xpathList);
```