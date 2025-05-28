# Web Automated Scraper for accessibility


### Setup
**PyCharm setup:**
This will run **keyPressControl script**. It will traverse the website by sending all the keypresses for actionable UI elements that will trigger NVDA. Next, the script will extract the DOM of a page using pyppeteer tool that will be used to find locatability issues.
1. Install required packages
    ```
    pip install selenium webdriver-manager
    ```
   ```
    pip install keyboard
    ```
2. Download Chromedriver
   1. Open Chrome.
   2. Go to chrome://settings/help. This will show your current Chrome version. Note it down (e.g., 115.0.5790.99).
   3. Download the matching ChromeDriver for your version of Chrome and set the path under method connect_to_existing_chrome() in main.py.


### Build
1. Start Chrome with remote debugging using below command. This allows your script to communicate with an already open Chrome instance, get information such as the URL, tabs, and DOM structure.
   1. Keep path to chrome.exe
   2. Add website you want to debug
       ```
       "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\chrome_temp" "https://www.yelp.com/search?find_desc=Restaurants&find_loc=Mountain+View%2C+CA"
       ```
       <details>
       <summary> Why is this command necessary?</summary>
       Remote Debugging: Chrome, by default, doesn't allow external programs (like Python scripts) to access its internal details (tabs, URLs, DOM, etc.) unless it's explicitly told to do so via the --remote-debugging-port flag. This flag opens a communication channel that tools like Selenium can use to interact with a running Chrome session.
       </details>
2. Run nvda so to run this script on nvda
   1. Can either run from Pycharm configurations or cmd
   2. If cmd- build nvda project by running below command in terminal
      ```
      scons launcher
       ```
      Launches exe at _D:\my_docs\UCI\Research\Spring24\WebImpl\nvda\output_
3. Run main.py of the keyPressControl script
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