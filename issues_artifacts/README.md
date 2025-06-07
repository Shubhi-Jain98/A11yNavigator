# A11yNavigator
This is the issues artifact of the paper "Automated Detection of Web Application Navigation Barriers for Screen Reader Users".

## Subject Apps
 The list of all subject apps can be found below.

| Id | Website       | Category                        | View Mode | #Traffic |
|----|---------------|---------------------------------|-----------|----------|
| 1  | ADP           | Human Resources                 | Desktop   | >50M     |
|    |               |                                 | Compact   | >50M     |
| 2  | Agoda         | Hospitality                     | Desktop   | >10M     |
|    |               |                                 | Compact   | >10M     |
| 3  | Capitalone    | Banking                         | Desktop   | >50M     |
|    |               |                                 | Compact   | >100M    |
| 4  | Chase         | Banking                         | Desktop   | >100M    |
|    |               |                                 | Compact   | >10M     |
| 5  | Craiglist     | Real Estate                     | Desktop   | >50M     |
| 6  | Discord       | Computer Software & Development | Desktop   | >50M     |
|    |               |                                 | Compact   | >100M    |
| 7  | Doordash      | Restaurants                     | Desktop   | >10M     |
|    |               |                                 | Compact   | >10M     |
| 8  | Doubleclick   | Online service                  | Desktop   | >10M     |
|    |               |                                 | Compact   | >100M    |
| 9  | DuckDuckGo    | Food & Beverages                | Desktop   | >100M    |
|    |               |                                 | Compact   | >1B      |
| 10 | Formula1      | Automative                      | Desktop   | >10M     |
|    |               |                                 | Compact   | >10M     |
| 11 | Fragrantica   | Beauty and Cosmetics            | Desktop   | >10M     |
|    |               |                                 | Compact   | >10M     |
| 12 | Genius        | Music                           | Desktop   | >50M     |
|    |               |                                 | Compact   | >100M    |
| 13 | Google        | Online services                 | Desktop   | >100B    |
| 14 | IRCTC         | Airlines                        | Desktop   | >10M     |
|    |               |                                 | Compact   | >50M     |
| 15 | Makemytrip    | Airlines                        | Desktop   | >10M     |
| 16 | Microsoft     | Information Technology          | Desktop   | >1B      |
|    |               |                                 | Compact   | >500M    |
| 17 | NIH           | Healthcare                      | Desktop   | >100M    |
|    |               |                                 | Compact   | >100M    |
| 18 | OpenAI        | Computer Software & Development | Desktop   | >100M    |
|    |               |                                 | Compact   | >500M    |
| 19 | Progressive   | Insurance                       | Desktop   | >10M     |
|    |               |                                 | Compact   | >10M     |
| 20 | Samsung       | Telecom                         | Desktop   | >10M     |
|    |               |                                 | Compact   | >100M    |
| 21 | Sciencedirect | Science                         | Desktop   | >50M     |
|    |               |                                 | Compact   | >10M     |
| 22 | Stackoverflow | Distance Learning               | Desktop   | >100M    |
|    |               |                                 | Compact   | >10M     |
| 23 | USPS          | Transportation and Logistics    | Desktop   | >50M     |
|    |               |                                 | Compact   | >100M    |
| 24 | Wikipedia     | Newspapers                      | Desktop   | >1M      |
| 25 | Youtube       | Newspapers                      | Desktop   | >10B     |
| 26 | Zerodha       | Investment                      | Desktop   | >10M     |
|    |               |                                 | Compact   | >10M     |

## Quick Hacks
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
To highlight all the elements using xpath list via Inspect tool -> Go to Console and type below command
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