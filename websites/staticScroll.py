import os
import tempfile
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from locatability import find_locatability_issues


class StaticHeightScraper:
    def __init__(self, max_height=2000):
        self.max_height = max_height
        options = Options()
        # Disable JavaScript-based infinite scroll
        options.add_experimental_option("prefs", {
            "profile.managed_default_content_settings.javascript": 2
        })
        self.driver = webdriver.Chrome(options=options)

    def enforce_static_height(self):
        """
        Strictly enforce height limit and prevent scrolling
        """
        script = f"""
        // Force fixed height on body and html
        document.body.style.maxHeight = '{self.max_height}px';
        document.body.style.overflow = 'hidden';
        document.documentElement.style.maxHeight = '{self.max_height}px';
        document.documentElement.style.overflow = 'hidden';

        // Find and limit main content container
        const contentSelectors = ['main', '#content', '.content', '[role="main"]'];
        contentSelectors.forEach(selector => {{
            const element = document.querySelector(selector);
            if (element) {{
                element.style.maxHeight = '{self.max_height}px';
                element.style.overflow = 'hidden';
            }}
        }});

        // Disable all scroll events
        document.addEventListener('scroll', function(e) {{
            e.preventDefault();
            e.stopPropagation();
            window.scrollTo(0, 0);
            return false;
        }}, true);

        // Remove infinite scroll triggers
        const observerScript = `
            window.IntersectionObserver = function() {{
                return {{
                    observe: function() {{}},
                    unobserve: function() {{}},
                    disconnect: function() {{}}
                }};
            }};
        `;

        // Prevent dynamic content loading
        const originalFetch = window.fetch;
        window.fetch = function(url, options) {{
            if (url.includes('?after=') ||
                url.includes('page=') ||
                url.includes('offset=') ||
                url.includes('cursor=')) {{
                return new Promise(resolve => resolve({{json: () => ({{items: []}})}}));
            }}
            return originalFetch(url, options);
        }};
        """
        self.driver.execute_script(script)

    def scrape_static_page(self, url):
        """
        Scrape page with strict height limit
        """
        try:
            # Load the page
            self.driver.get(url)

            # Wait for initial content
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Apply height restrictions and scroll prevention
            self.enforce_static_height()

            # Find content within the height limit
            if "reddit.com" in url:
                items = self.driver.find_elements(By.CSS_SELECTOR, "div[data-testid='post-container']")
            elif "youtube.com" in url:
                items = self.driver.find_elements(By.CSS_SELECTOR, "ytd-video-renderer")
            else:
                items = self.driver.find_elements(By.CSS_SELECTOR, "article, .post, .item")

            return items

        except Exception as e:
            print(f"Error scraping page: {e}")
            return []

    def close(self):
        self.driver.quit()


# Example usage
def scrape_with_height_limit(url, max_height=2000):
    from main import delete_files_in_folder
    scraper = StaticHeightScraper(max_height=max_height)
    try:
        items = scraper.scrape_static_page(url)
        print(f"Found {len(items)} items within height limit")

        # Process found items
        for item in items:
            try:
                # Extract relevant information based on the site
                if "reddit.com" in url:
                    title = item.find_element(By.CSS_SELECTOR, "h3").text
                    print(f"Title: {title}")
                elif "youtube.com" in url:
                    title = item.find_element(By.CSS_SELECTOR, "#video-title").text
                    print(f"Video: {title}")
            except Exception as e:
                print(f"Error processing item: {e}")
    finally:
        scraper.close()









#
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.options import Options
# import time
# import re
# from urllib.parse import urlparse
#
#
# class GenericStaticScraper:
#     def __init__(self, max_height=2000):
#         self.max_height = max_height
#         options = Options()
#         # Disable JavaScript-based infinite scroll
#         options.add_experimental_option("prefs", {
#             "profile.managed_default_content_settings.javascript": 2
#         })
#         self.driver = webdriver.Chrome(options=options)
#
#     def enforce_static_height(self):
#         """
#         Apply height limit with more generic content detection
#         """
#         script = f"""
#         function findMainContent() {{
#             // Common content container patterns
#             const contentPatterns = [
#                 // Generic content containers
#                 'main', '#main', '.main', '[role="main"]',
#                 '#content', '.content', '#primary', '.primary',
#                 'article', '.articles', '#articles',
#                 '.posts', '#posts', '.feed', '#feed',
#                 '.timeline', '#timeline',
#
#                 // Layout containers
#                 '.container', '.wrapper', '#container', '#wrapper',
#                 '.content-wrapper', '#content-wrapper',
#
#                 // Site-specific but common patterns
#                 '[data-testid*="content"]',
#                 '[data-testid*="feed"]',
#                 '[data-testid*="posts"]',
#                 '[class*="content"]',
#                 '[class*="feed"]',
#                 '[class*="posts"]',
#                 '[id*="content"]',
#                 '[id*="feed"]',
#                 '[id*="posts"]'
#             ];
#
#             // Try each selector
#             for (const pattern of contentPatterns) {{
#                 const elements = document.querySelectorAll(pattern);
#                 // Find the largest visible container
#                 let maxArea = 0;
#                 let bestElement = null;
#
#                 elements.forEach(el => {{
#                     if (window.getComputedStyle(el).display !== 'none') {{
#                         const rect = el.getBoundingClientRect();
#                         const area = rect.width * rect.height;
#                         if (area > maxArea) {{
#                             maxArea = area;
#                             bestElement = el;
#                         }}
#                     }}
#                 }});
#
#                 if (bestElement) return bestElement;
#             }}
#
#             // Fallback to body if no suitable container found
#             return document.body;
#         }}
#
#         // Apply height limit to the main content
#         const mainContent = findMainContent();
#         mainContent.style.maxHeight = '{self.max_height}px';
#         mainContent.style.overflowY = 'auto';
#         mainContent.style.overflowX = 'hidden';
#
#         // Prevent dynamic loading mechanisms
#         window.IntersectionObserver = function() {{
#             return {{
#                 observe: function() {{}},
#                 unobserve: function() {{}},
#                 disconnect: function() {{}}
#             }};
#         }};
#
#         // Block common infinite scroll requests
#         const originalFetch = window.fetch;
#         window.fetch = function(url, options) {{
#             const blockPatterns = [
#                 '?after=', '?before=', '?page=', '?offset=',
#                 '?cursor=', '?start=', '?from=', '?load_more=',
#                 '/api/loadMore', '/api/infinite', '/api/feed',
#                 'scroll', 'pagination', 'page', 'offset', 'next'
#             ];
#
#             if (blockPatterns.some(pattern => url.toLowerCase().includes(pattern))) {{
#                 return new Promise(resolve => resolve({{json: () => ({{items: []}})}}));
#             }}
#             return originalFetch(url, options);
#         }};
#
#         // Add scrollbar styling
#         const style = document.createElement('style');
#         style.textContent = `
#             ::-webkit-scrollbar {{
#                 width: 8px;
#             }}
#             ::-webkit-scrollbar-track {{
#                 background: #f1f1f1;
#             }}
#             ::-webkit-scrollbar-thumb {{
#                 background: #888;
#                 border-radius: 4px;
#             }}
#             ::-webkit-scrollbar-thumb:hover {{
#                 background: #555;
#             }}
#         `;
#         document.head.appendChild(style);
#         """
#         self.driver.execute_script(script)
#
#     def find_content_items(self):
#         """
#         Generic content detection based on common patterns
#         """
#         # Common patterns for content items
#         selectors = [
#             # Generic content patterns
#             "article",
#             "[class*='post']",
#             "[class*='item']",
#             "[class*='card']",
#             "[class*='entry']",
#             # Feed items
#             "[class*='feed-item']",
#             "[class*='timeline-item']",
#             # List items with content
#             "li[class*='content']",
#             "div[class*='content']",
#             # Data attribute patterns
#             "[data-testid*='post']",
#             "[data-testid*='item']",
#             "[data-testid*='card']",
#             # Common content containers
#             ".post-container",
#             ".content-container",
#             ".item-container"
#         ]
#
#         all_items = []
#         for selector in selectors:
#             items = self.driver.find_elements(By.CSS_SELECTOR, selector)
#             if items:
#                 # Filter out very small elements that might be UI components
#                 items = [item for item in items if item.size['height'] > 50]
#                 all_items.extend(items)
#
#         # Remove duplicates (elements that match multiple patterns)
#         unique_items = list({item.id: item for item in all_items}.values())
#         return unique_items
#
#     def extract_content(self, item):
#         """
#         Extract content from an item using common patterns
#         """
#         content = {}
#
#         # Common text content selectors
#         text_selectors = [
#             "h1", "h2", "h3", "h4", "h5", "h6",
#             "[class*='title']", "[class*='heading']",
#             "p", "[class*='text']", "[class*='description']"
#         ]
#
#         # Common link selectors
#         link_selectors = [
#             "a[href]", "[class*='link']"
#         ]
#
#         # Try to get text content
#         for selector in text_selectors:
#             try:
#                 elements = item.find_elements(By.CSS_SELECTOR, selector)
#                 if elements:
#                     content['text'] = [elem.text for elem in elements if elem.text.strip()]
#             except:
#                 continue
#
#         # Try to get links
#         for selector in link_selectors:
#             try:
#                 elements = item.find_elements(By.CSS_SELECTOR, selector)
#                 if elements:
#                     content['links'] = [elem.get_attribute('href') for elem in elements if elem.get_attribute('href')]
#             except:
#                 continue
#
#         return content
#
#     def scrape_static_page(self, url):
#         """
#         Scrape any dynamic website with height limit
#         """
#         try:
#             self.driver.get(url)
#             WebDriverWait(self.driver, 10).until(
#                 EC.presence_of_element_located((By.TAG_NAME, "body"))
#             )
#             self.enforce_static_height()
#             time.sleep(2)  # Allow for any initial content load
#
#             items = self.find_content_items()
#             return items
#         except Exception as e:
#             print(f"Error scraping page: {e}")
#             return []
#
#     def close(self):
#         self.driver.quit()
#
#
# def scrape_with_height_limit(url, max_height=2000):
#     scraper = GenericStaticScraper(max_height=max_height)
#     try:
#         print(f"Scraping {url} with height limit of {max_height}px")
#         items = scraper.scrape_static_page(url)
#         print(f"Found {len(items)} content items")
#
#         # Extract and display content from each item
#         for i, item in enumerate(items, 1):
#             content = scraper.extract_content(item)
#             if content:
#                 print(f"\nItem {i}:")
#                 if 'text' in content:
#                     print("Text content:", content['text'][:2])  # Show first 2 text elements
#                 if 'links' in content:
#                     print("Links found:", len(content['links']))
#
#         # Keep the browser window open for viewing
#         time.sleep(300)
#
#     finally:
#         scraper.close()