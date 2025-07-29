from flask import Blueprint, jsonify, request, send_file
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import threading
import logging
import os
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

notebooklm_bp = Blueprint('notebooklm', __name__)

# --- Constants for Selenium Selectors ---
# Using constants makes the code cleaner and easier to update if the UI changes.

# Elements for checking if NotebookLM has loaded
NOTEBOOKLM_LOAD_INDICATORS = [
    (By.CSS_SELECTOR, '[data-testid="chat-input"]'),
    (By.CSS_SELECTOR, 'textarea[placeholder*="Ask"]'),
    (By.CSS_SELECTOR, '.chat-input'),
    (By.XPATH, "//textarea[contains(@placeholder, 'Ask')]")
]

# Elements for the chat input field
CHAT_INPUT_SELECTORS = [
    (By.CSS_SELECTOR, '[data-testid="chat-input"]'),
    (By.CSS_SELECTOR, 'textarea[placeholder*="Ask"]'),
    (By.CSS_SELECTOR, '.chat-input textarea'),
    (By.CSS_SELECTOR, 'textarea[aria-label*="Ask"]')
]

# Elements for the submit button
SUBMIT_BUTTON_SELECTORS = [
    (By.CSS_SELECTOR, 'button[data-testid="send-button"]'),
    (By.CSS_SELECTOR, 'button[aria-label*="Send"]')
]

RESPONSE_CONTENT_SELECTOR = (By.CSS_SELECTOR, '.message-content')

# Global variable to store the browser instance
browser_instance = None
browser_lock = threading.Lock()
initialization_thread = None

def start_browser_initialization_thread():
    """
    Starts the browser initialization in a background thread if not already running.
    This function is thread-safe.
    """
    global initialization_thread
    with browser_lock:
        if not (initialization_thread and initialization_thread.is_alive()):
            logger.info("Starting new browser initialization thread.")
            initialization_thread = threading.Thread(target=initialize_browser, daemon=True)
            initialization_thread.start()

def initialize_browser(max_retries=3, retry_delay=15):
    """
    Initializes the browser instance in the background with retries.
    This function is intended to be run in a separate thread on app startup.
    """
    global browser_instance
    url = os.environ.get('NOTEBOOKLM_BASE_URL', 'https://notebooklm.google.com/')

    for attempt in range(max_retries):
        logger.info(f"Browser initialization attempt {attempt + 1}/{max_retries}...")
        try:
            # Lock to prevent race conditions
            with browser_lock:
                if browser_instance:
                    logger.info("Browser is already initialized. Skipping.")
                    return

            # Create driver outside the lock
            driver = create_undetected_driver()
            logger.info(f"Driver created. Navigating to initial URL: {url}")
            driver.get(url)

            # Wait for the page to either load or redirect to the sign-in page.
            # This is more reliable than a fixed time.sleep().
            logger.info("Waiting for initial page to load...")
            WebDriverWait(driver, 20).until(
                EC.url_contains("notebooklm.google.com") or EC.url_contains("accounts.google.com")
            )

            current_url = driver.current_url
            if 'accounts.google.com' in current_url or 'signin' in current_url.lower():
                logger.warning("Redirected to Google sign-in page during initial startup. "
                               "Manual login via VNC may be required to proceed.")
            else:
                logger.info("Initial page loaded successfully. Browser is ready.")

            # Acquire lock again to set the global instance
            with browser_lock:
                browser_instance = driver

            logger.info("Browser initialization successful.")
            return  # Exit the loop on success

        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed to initialize browser: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("All browser initialization attempts failed.")


def create_undetected_driver():
    """Create a Chrome driver with options to bypass automation detection"""
    chrome_options = Options()

    # Use a persistent user profile, configurable via environment variable. This is crucial for staying logged in.
    user_data_dir = os.environ.get('CHROME_USER_DATA_DIR', '/data')
    chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
    # The '--profile-directory=Default' argument is no longer needed because the volume mount
    # now maps the GCS 'Default' profile contents directly into the user_data_dir.
    # chrome_options.add_argument('--profile-directory=Default')

    # Standard options for running in a container like selenium/standalone-chrome
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')

    # Options to appear more like a regular user. We are simplifying these to improve stability.
    # The most aggressive anti-detection flags can cause issues with new browser versions.
    # chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    default_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.7204.157 Safari/537.36'
    user_agent = os.environ.get('CHROME_USER_AGENT', default_user_agent)
    chrome_options.add_argument(f'user-agent={user_agent}')

    # Connect to remote Selenium server. Default to localhost for local development.
    selenium_hub_url = os.environ.get('SELENIUM_HUB_URL', 'http://localhost:4444/wd/hub')
    logger.info(f"Connecting to Selenium Hub at: {selenium_hub_url}")
    driver = webdriver.Remote(
        command_executor=selenium_hub_url,
        options=chrome_options
    )

    # Set a page load timeout to avoid hangs
    driver.set_page_load_timeout(60)

    # The script to hide the webdriver property is also a potential point of failure and has been removed for stability.
    # driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def find_element_by_priority(driver, selectors, condition=EC.presence_of_element_located, timeout=10):
    """
    Tries to find an element by iterating through a list of selectors.
    Returns the first element that matches any selector and the expected condition.
    
    :param driver: The Selenium WebDriver instance.
    :param selectors: A list of tuples, where each tuple is (By, value).
    :param condition: An expected condition from selenium.webdriver.support.expected_conditions.
    :param timeout: The maximum time to wait for the element.
    :return: The WebElement if found, otherwise None.
    """
    wait = WebDriverWait(driver, timeout)
    for by, value in selectors:
        try:
            return wait.until(condition((by, value)))
        except TimeoutException:
            logger.debug(f"Selector ({by}, '{value}') not found with condition {condition.__name__}. Trying next.")
            continue
    return None

@notebooklm_bp.route('/open_notebooklm', methods=['POST'])
def open_notebooklm():
    """
    Endpoint 1: Opens a specific NotebookLM in headless Chrome browser
    Expects JSON: {"notebooklm_url": "https://notebooklm.google.com/notebook/..."}
    """
    global browser_instance

    data = request.get_json()
    if not data or 'notebooklm_url' not in data:
        return jsonify({'error': 'notebooklm_url is required'}), 400

    notebooklm_url = data['notebooklm_url']
    logger.info(f"Attempting to open NotebookLM URL: {notebooklm_url}")

    with browser_lock:
        if not browser_instance:
            logger.error("Browser is not initialized. The background initialization may have failed.")
            return jsonify({
                'error': 'Browser not initialized. Check service logs for errors.',
                'status': 'not_initialized'
            }), 503  # Service Unavailable

        # Core browser interaction logic
        return _perform_open_notebook(notebooklm_url)

def _perform_open_notebook(url):
    """Helper function to contain the browser navigation and validation logic."""
    assert browser_instance is not None, "Browser instance must be initialized before calling this function."
    try:
        # Navigate to the NotebookLM URL
        browser_instance.get(url)

        # Wait for page to load and check if we're on the correct page
        wait = WebDriverWait(browser_instance, 30)

        # Check if we're redirected to Google sign-in page
        current_url = browser_instance.current_url
        if 'accounts.google.com' in current_url or 'signin' in current_url.lower():
            logger.warning("Redirected to Google sign-in page")
            return jsonify({
                'error': 'Redirected to Google sign-in page. Authentication required. Please log in using VNC.',
                'current_url': current_url,
                'status': 'authentication_required'
            }), 401

        # Wait for NotebookLM interface to load
        load_indicator = find_element_by_priority(browser_instance, NOTEBOOKLM_LOAD_INDICATORS, timeout=30)
        if not load_indicator:
            raise TimeoutException("Could not find any of the specified NotebookLM load indicators.")

        logger.info("NotebookLM interface loaded successfully")
        return jsonify({
            'success': True,
            'message': 'NotebookLM opened successfully',
            'current_url': browser_instance.current_url,
        })
    except TimeoutException:
        logger.warning("NotebookLM interface not detected, but page loaded")
        return jsonify({
            'success': True,
            'message': 'Page loaded but NotebookLM interface not fully detected',
            'current_url': browser_instance.current_url,
            'status': 'partial_load'
        })
    except Exception as e:
        logger.error(f"Error opening NotebookLM: {str(e)}")
        return jsonify({'error': f'Failed to open NotebookLM: {str(e)}'}), 500

@notebooklm_bp.route('/query_notebooklm', methods=['POST'])
def query_notebooklm():
    """
    Endpoint 2: Queries NotebookLM and waits for complete response
    Expects JSON: {"query": "Your question here"}
    """
    global browser_instance
    
    if not browser_instance:
        return jsonify({'error': 'Browser not initialized. Call /open_notebooklm first.'}), 400
    
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({'error': 'query is required'}), 400
    
    query = data.get('query')
    # Allow the user to specify a timeout, with a default of 120 seconds.
    timeout = int(data.get('timeout', 120))
    logger.info(f"Submitting query: '{query}' with a timeout of {timeout} seconds.")
    
    try:
        with browser_lock:
            # Find the input field
            input_element = find_element_by_priority(browser_instance, CHAT_INPUT_SELECTORS, condition=EC.element_to_be_clickable, timeout=30)
            if not input_element:
                return jsonify({'error': 'Could not find chat input field'}), 500
            
            # Clear and enter the query
            input_element.clear()
            input_element.send_keys(query)
            
            # Submit the query
            submit_button = find_element_by_priority(browser_instance, SUBMIT_BUTTON_SELECTORS, condition=EC.element_to_be_clickable, timeout=5)
            if submit_button:
                submit_button.click()
            else:
                # Fallback to pressing Enter if button not found/clickable
                from selenium.webdriver.common.keys import Keys
                input_element.send_keys(Keys.RETURN)
            
            logger.info("Query submitted, waiting for response...")
            
            # Wait for the response to finish by checking if the submit button is active again.
            response_wait = WebDriverWait(browser_instance, timeout)
            response_wait.until(EC.element_to_be_clickable(SUBMIT_BUTTON_SELECTORS[0]))
            logger.info("Content generation completed (send button is active).")

            # Extract the response content
            response_elements = browser_instance.find_elements(*RESPONSE_CONTENT_SELECTOR)
            response_content = response_elements[-1].text if response_elements else None
            
            if response_content:
                logger.info(f"Extracted response content (length: {len(response_content)}).")
            else:
                logger.warning("Could not find any response content elements.")
            
            return jsonify({
                'success': True,
                'message': 'Query completed successfully',
                'query': query,
                'response_content': response_content,
                'content_length': len(response_content) if response_content else 0
            })

    except TimeoutException:
        logger.warning("Timed out waiting for response to complete. Extracting whatever content is available.")
        # Even on timeout, try to grab the content that has been generated so far.
        response_elements = browser_instance.find_elements(*RESPONSE_CONTENT_SELECTOR)
        response_content = response_elements[-1].text if response_elements else "Response timed out, no content extracted."
        return jsonify({
            'success': False,
            'message': 'Query timed out, partial content may be available.',
            'query': query,
            'response_content': response_content,
            'content_length': len(response_content) if response_content else 0,
            'status': 'timeout'
        }), 206 # Partial Content
    except Exception as e:
        logger.error(f"An unexpected error occurred during query: {str(e)}", exc_info=True)
        return jsonify({'error': f'Failed to query NotebookLM: {str(e)}'}), 500

@notebooklm_bp.route('/close_browser', methods=['POST'])
def close_browser():
    """
    Endpoint 3: Closes the Chrome driver
    """
    global browser_instance
    
    try:
        with browser_lock:
            if browser_instance:
                logger.info("Closing browser instance")
                browser_instance.quit()
                browser_instance = None
                return jsonify({
                    'success': True,
                    'message': 'Browser closed successfully'
                })
            else:
                return jsonify({
                    'success': True,
                    'message': 'No browser instance to close'
                })
    
    except Exception as e:
        logger.error(f"Error closing browser: {str(e)}")
        return jsonify({'error': f'Failed to close browser: {str(e)}'}), 500

@notebooklm_bp.route('/status', methods=['GET'])
def get_status():
    """
    Additional endpoint to check the status of the browser instance.
    This provides a health check for the Selenium integration.
    """
    global browser_instance
    
    with browser_lock:
        if not browser_instance:
            return jsonify({
                'browser_active': False,
                'status': 'not_initialized'
            })
        
        try:
            # A simple way to check if the browser is still responsive
            current_url = browser_instance.current_url
            title = browser_instance.title # Another lightweight check
            
            status = 'ready'
            if 'accounts.google.com' in current_url or 'signin' in current_url.lower():
                status = 'authentication_required'
            
            return jsonify({
                'browser_active': True,
                'current_url': current_url,
                'page_title': title,
                'status': status
            })
        except Exception as e:
            # This exception block catches errors if the browser has crashed or is unresponsive.
            logger.error(f"Browser instance is unresponsive, marking as inactive. Error: {e}")
            browser_instance = None # Clean up the dead instance
            start_browser_initialization_thread() # Attempt to self-heal by restarting initialization
            return jsonify({
                'browser_active': False,
                'status': 'inactive',
                'error': f"Browser was unresponsive and has been cleaned up. Details: {str(e)}"
            }), 503 # Service Unavailable

@notebooklm_bp.route('/screenshot', methods=['GET'])
def get_screenshot():
    """
    Additional endpoint to capture a screenshot of the current browser page for debugging.
    """
    global browser_instance
    
    with browser_lock:
        if not browser_instance:
            return jsonify({'error': 'Browser not initialized.'}), 400
        
        try:
            # Get screenshot as PNG
            png_data = browser_instance.get_screenshot_as_png()
            
            # Return the image file
            return send_file(
                io.BytesIO(png_data),
                mimetype='image/png'
            )
        except Exception as e:
            logger.error(f"Error taking screenshot: {str(e)}")
            return jsonify({'error': f'Failed to take screenshot: {str(e)}'}), 500

@notebooklm_bp.route('/page_title', methods=['GET'])
def get_page_title():
    """
    Returns the title of the currently active page in the browser.
    """
    global browser_instance
    
    with browser_lock:
        if not browser_instance:
            return jsonify({'error': 'Browser not initialized.'}), 400
        
        try:
            title = browser_instance.title
            logger.info(f"Retrieved page title: '{title}'")
            return jsonify({
                'success': True,
                'page_title': title
            })
        except Exception as e:
            logger.error(f"Browser instance is unresponsive while getting title, marking as inactive. Error: {e}")
            browser_instance = None # Clean up the dead instance
            start_browser_initialization_thread() # Attempt to self-heal by restarting initialization
            return jsonify({
                'browser_active': False,
                'status': 'inactive',
                'error': f"Browser was unresponsive while getting title. Details: {str(e)}"
            }), 503 # Service Unavailable
