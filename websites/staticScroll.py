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
