# A11yNavigator
This is the artifact of the paper "Automated Detection of Web Application Navigation Barriers for Screen Reader Users".


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