from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import time
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DynamicWebScraper:
    # def __init__(self, headless=False):
    #     options = webdriver.ChromeOptions()
    #     if headless:
    #         options.add_argument('--headless')
    #     self.driver = webdriver.Chrome(options=options)
    #     self.wait = WebDriverWait(self.driver, 10)

    def __init__(self, debugger_address=None):
        """
        Initializes the scraper.

        Args:
            debugger_address: Address of the Chrome debugger session (e.g., "127.0.0.1:9222").
        """
        self.debugger_address = debugger_address
        self.driver = None

    def connect_to_debugger(self):
        """Connects to an existing Chrome debugging session."""
        if not self.debugger_address:
            raise ValueError("No debugger address provided for connecting to Chrome debugger.")

        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", self.debugger_address)
        self.driver = webdriver.Chrome(options=chrome_options)
        logger.info(f"Connected to Chrome debugger at {self.debugger_address}")

    def disable_dynamic_loading(self):
        """Disables dynamic loading by intercepting scroll events"""
        disable_script = """
        // Store original scroll position
        window._lastScrollPosition = window.scrollY;

        // Disable scroll-based loading
        window._originalFetch = window.fetch;
        window.fetch = function(url, options) {
            if (url.includes('?after=') || url.includes('?pagination=')) {
                return new Promise((resolve) => resolve({ json: () => ({ items: [] })}));
            }
            return window._originalFetch(url, options);
        };

        // Disable intersection observer
        window._disabledIntersectionObserver = window.IntersectionObserver;
        window.IntersectionObserver = function() {
            return {
                observe: function() {},
                disconnect: function() {}
            };
        };

        // Block scroll events
        document.addEventListener('scroll', function(e) {
            window.scrollTo(0, window._lastScrollPosition);
        }, true);
        """
        self.driver.execute_script(disable_script)

    def limit_content_height(self, max_height_pixels=5000):
        """
        Limit scrolling on the Reddit feed container (<shreddit-feed>).
        """
        time.sleep(5)
        limit_script = f"""
        (function() {{
            // Locate the shreddit-feed element
            const feedElement = document.querySelector('shreddit-feed');
            if (feedElement) {{
                // Apply maximum height and hide overflow
                feedElement.style.maxHeight = '{max_height_pixels}px';
                feedElement.style.overflow = 'hidden';

                // Prevent scrolling via mouse wheel or touch
                feedElement.addEventListener('wheel', (event) => {{
                    event.preventDefault();
                }}, {{"passive": false}});

                // Prevent scrolling via keyboard keys
                document.addEventListener('keydown', (event) => {{
                    const scrollableKeys = ['ArrowUp', 'ArrowDown', 'PageUp', 'PageDown', 'Home', 'End'];
                    if (scrollableKeys.includes(event.key)) {{
                        event.preventDefault();
                    }}
                }});

                console.log("Scrolling limited on shreddit-feed to", {max_height_pixels}, "pixels.");
            }} else {{
                console.warn("shreddit-feed element not found. No limits applied.");
            }}
        }})();
        """
        self.driver.execute_script(limit_script)

    def limit_content_height_prev(self, max_height_pixels=5000):
        """Limits the maximum height of the content area"""
        limit_script = f"""
        // Find main content container
        function findMainContent() {{
            // Common content container selectors
            const selectors = [
                'main',
                '#content',
                '#main-content',
                '[role="main"]',
                '.content-area'
            ];

            for (let selector of selectors) {{
                const element = document.querySelector(selector);
                if (element) return element;
            }}

            return document.body;
        }}

        const mainContent = findMainContent();
        mainContent.style.maxHeight = '{max_height_pixels}px';
        mainContent.style.overflow = 'hidden';
        """
        self.driver.execute_script(limit_script)

    def scroll_with_limits(self,
                           max_items=5,
                           max_scroll_time=3,
                           max_scroll_distance=10):
        """
        Scrolls the page with various limiting conditions
        Returns True if limit was reached, False if natural end
        """
        start_time = time.time()
        initial_height = self.driver.execute_script("return window.scrollY")
        items_found = 0

        while True:
            # Check time limit
            if time.time() - start_time > max_scroll_time:
                logger.info("Reached maximum scroll time limit")
                return True

            # Check scroll distance limit
            current_scroll = self.driver.execute_script("return window.scrollY")
            if current_scroll - initial_height > max_scroll_distance:
                logger.info("Reached maximum scroll distance")
                return True

            # Check items limit
            items_found = len(self.find_content_items())
            if items_found >= max_items:
                logger.info(f"Reached maximum items limit: {items_found}")
                return True

            # Scroll and check if we've reached the bottom
            last_height = self.driver.execute_script("return document.documentElement.scrollHeight")
            self.driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(2)

            new_height = self.driver.execute_script("return document.documentElement.scrollHeight")
            if new_height == last_height:
                logger.info("Reached natural end of page")
                return False

    def find_content_items(self):
        """Finds content items based on the website type"""
        selectors = {
            'youtube': '//ytd-video-renderer',
            'reddit': '//div[contains(@class, "Post")]',
            'twitter': '//article',
            'default': '//article|//div[contains(@class, "post")]|//div[contains(@class, "item")]'
        }

        # Determine website type from URL
        current_url = self.driver.current_url.lower()
        site_type = 'default'
        for key in selectors.keys():
            if key in current_url:
                site_type = key
                break

        try:
            items = self.driver.find_elements(By.XPATH, selectors[site_type])
            return items
        except Exception as e:
            logger.error(f"Error finding items: {e}")
            return []

    def scrape_with_control(self, url, method='disable_loading', **kwargs):
        """
        Main scraping method with different control strategies

        Args:
            url: Website URL to scrape
            method: Control method ('disable_loading', 'limit_height', 'scroll_limits')
            **kwargs: Additional arguments for the chosen method
        """
        try:
            logger.info(f"Starting scrape of {url} using {method} method")
            # Connect to Chrome debugger if necessary
            if self.debugger_address:
                self.connect_to_debugger()

            # Navigate to URL if provided
            if url:
                self.driver.get(url)
                time.sleep(5)  # Let initial content load

            if method == 'disable_loading':
                self.disable_dynamic_loading()
                time.sleep(2)
                items = self.find_content_items()

            elif method == 'limit_height':
                max_height = kwargs.get('max_height', 5000)
                self.limit_content_height(max_height)
                time.sleep(2)
                items = self.find_content_items()

            elif method == 'scroll_limits':
                reached_limit = self.scroll_with_limits(
                    max_items=kwargs.get('max_items', 5),
                    max_scroll_time=kwargs.get('max_scroll_time', 300),
                    max_scroll_distance=kwargs.get('max_scroll_distance', 10000)
                )
                items = self.find_content_items()

            logger.info(f"Found {len(items)} items")
            return items

        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            return []

    def cleanup(self):
        """Closes the browser"""
        self.driver.quit()


# Example usage
# def dynamic_pause():
#     #scraper = DynamicWebScraper()
#     scraper = DynamicWebScraper(debugger_address="127.0.0.1:9222")
#     try:
#         # Example 1: Using disable_loading method - NOT GOOD - It prevents scrolling even though content is present below. Tab press goes down
#         # items = scraper.scrape_with_control(
#         #     "https://www.reddit.com/r/Python/",
#         #     method='disable_loading'
#         # )
#
#         # Example 2: Using height limit
#         items = scraper.scrape_with_control(
#             None,
#             method='limit_height',
#             max_height=2000
#         )
#
#         # Example 3: Using scroll limits -  NOT WORKING
#         # items = scraper.scrape_with_control(
#         #     "https://www.reddit.com/r/Python/",
#         #     method='scroll_limits',
#         #     max_items=30,
#         #     max_scroll_time=120,
#         #     max_scroll_distance=5000
#         # )
#
#         find_actionability_issues()
#         time.sleep(520)
#
#     finally:
#         scraper.cleanup()
