from flask import Blueprint, jsonify, request
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

notebooklm_bp = Blueprint('notebooklm', __name__)

# Global variable to store the browser instance
browser_instance = None
browser_lock = threading.Lock()

def create_undetected_driver():
    """Create a Chrome driver with options to bypass automation detection"""
    chrome_options = Options()
    
    # Basic options for headless operation
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    # Options to bypass automation detection
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-plugins')
    chrome_options.add_argument('--disable-images')
    chrome_options.add_argument('--disable-javascript')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Connect to remote Selenium server (Docker container)
    driver = webdriver.Remote(
        command_executor='http://selenium-chrome:4444/wd/hub',
        options=chrome_options
    )
    
    # Execute script to remove automation indicators
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

@notebooklm_bp.route('/open_notebooklm', methods=['POST'])
def open_notebooklm():
    """
    Endpoint 1: Opens a specific NotebookLM in headless Chrome browser
    Expects JSON: {"notebooklm_url": "https://notebooklm.google.com/notebook/..."}
    """
    global browser_instance
    
    try:
        data = request.get_json()
        if not data or 'notebooklm_url' not in data:
            return jsonify({'error': 'notebooklm_url is required'}), 400
        
        notebooklm_url = data['notebooklm_url']
        
        with browser_lock:
            # Close existing browser if any
            if browser_instance:
                try:
                    browser_instance.quit()
                except:
                    pass
                browser_instance = None
            
            # Create new browser instance
            logger.info("Creating new Chrome driver instance")
            browser_instance = create_undetected_driver()
            
            # Navigate to the NotebookLM URL
            logger.info(f"Navigating to: {notebooklm_url}")
            browser_instance.get(notebooklm_url)
            
            # Wait for page to load and check if we're on the correct page
            wait = WebDriverWait(browser_instance, 30)
            
            # Check if we're redirected to Google sign-in page
            current_url = browser_instance.current_url
            if 'accounts.google.com' in current_url or 'signin' in current_url.lower():
                logger.warning("Redirected to Google sign-in page")
                return jsonify({
                    'error': 'Redirected to Google sign-in page. Authentication required.',
                    'current_url': current_url,
                    'status': 'authentication_required'
                }), 401
            
            # Wait for NotebookLM interface to load
            try:
                # Look for common NotebookLM elements
                wait.until(EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="chat-input"]')),
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea[placeholder*="Ask"]')),
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.chat-input')),
                    EC.presence_of_element_located((By.XPATH, "//textarea[contains(@placeholder, 'Ask')]"))
                ))
                
                logger.info("NotebookLM interface loaded successfully")
                return jsonify({
                    'success': True,
                    'message': 'NotebookLM opened successfully',
                    'current_url': browser_instance.current_url,
                    'status': 'ready'
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
    
    try:
        if not browser_instance:
            return jsonify({'error': 'Browser not initialized. Call /open_notebooklm first.'}), 400
        
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'query is required'}), 400
        
        query = data['query']
        logger.info(f"Submitting query: {query}")
        
        with browser_lock:
            wait = WebDriverWait(browser_instance, 30)
            
            # Find the input field
            input_selectors = [
                '[data-testid="chat-input"]',
                'textarea[placeholder*="Ask"]',
                '.chat-input textarea',
                'textarea[aria-label*="Ask"]',
                'input[placeholder*="Ask"]'
            ]
            
            input_element = None
            for selector in input_selectors:
                try:
                    input_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    break
                except TimeoutException:
                    continue
            
            if not input_element:
                return jsonify({'error': 'Could not find input field'}), 500
            
            # Clear and enter the query
            input_element.clear()
            input_element.send_keys(query)
            
            # Submit the query (look for submit button or press Enter)
            submit_selectors = [
                'button[data-testid="send-button"]',
                'button[aria-label*="Send"]',
                'button[type="submit"]',
                '.send-button'
            ]
            
            submitted = False
            for selector in submit_selectors:
                try:
                    submit_button = browser_instance.find_element(By.CSS_SELECTOR, selector)
                    if submit_button.is_enabled():
                        submit_button.click()
                        submitted = True
                        break
                except NoSuchElementException:
                    continue
            
            if not submitted:
                # Try pressing Enter
                from selenium.webdriver.common.keys import Keys
                input_element.send_keys(Keys.RETURN)
            
            logger.info("Query submitted, waiting for response...")
            
            # Wait for response to start generating
            time.sleep(2)
            
            # Monitor for content generation completion
            stable_count = 0
            max_wait_time = 60  # Maximum 60 seconds
            check_interval = 2  # Check every 2 seconds
            required_stable_checks = 5  # 10 seconds of stability (5 checks * 2 seconds)
            
            last_content_length = 0
            
            for i in range(max_wait_time // check_interval):
                try:
                    # Look for response content areas
                    response_selectors = [
                        '.response-content',
                        '.chat-message:last-child',
                        '[data-testid="response"]',
                        '.message-content:last-child'
                    ]
                    
                    current_content_length = 0
                    for selector in response_selectors:
                        try:
                            elements = browser_instance.find_elements(By.CSS_SELECTOR, selector)
                            if elements:
                                current_content_length = len(elements[-1].text)
                                break
                        except:
                            continue
                    
                    # Check if content has stopped changing
                    if current_content_length == last_content_length and current_content_length > 0:
                        stable_count += 1
                        logger.info(f"Content stable for {stable_count * check_interval} seconds")
                    else:
                        stable_count = 0
                        last_content_length = current_content_length
                        logger.info(f"Content still generating... (length: {current_content_length})")
                    
                    # If content has been stable for required time, break
                    if stable_count >= required_stable_checks:
                        logger.info("Content generation completed")
                        break
                    
                    time.sleep(check_interval)
                    
                except Exception as e:
                    logger.warning(f"Error monitoring content: {str(e)}")
                    time.sleep(check_interval)
            
            # Look for and click the copy button
            copy_selectors = [
                'button[aria-label*="Copy"]',
                'button[title*="Copy"]',
                '.copy-button',
                'button[data-testid="copy-button"]',
                'button:has(svg[data-icon="copy"])',
                'button:contains("Copy")'
            ]
            
            copied_content = None
            for selector in copy_selectors:
                try:
                    copy_buttons = browser_instance.find_elements(By.CSS_SELECTOR, selector)
                    if copy_buttons:
                        # Click the last (most recent) copy button
                        copy_button = copy_buttons[-1]
                        browser_instance.execute_script("arguments[0].click();", copy_button)
                        logger.info("Copy button clicked")
                        
                        # Try to get the copied content from clipboard (if possible)
                        # Note: Direct clipboard access is limited in headless mode
                        time.sleep(1)
                        break
                except Exception as e:
                    logger.warning(f"Could not click copy button with selector {selector}: {str(e)}")
                    continue
            
            # Get the response content directly from the page
            try:
                response_elements = browser_instance.find_elements(By.CSS_SELECTOR, 
                    '.response-content, .chat-message:last-child, [data-testid="response"], .message-content:last-child')
                if response_elements:
                    copied_content = response_elements[-1].text
            except Exception as e:
                logger.warning(f"Could not extract response content: {str(e)}")
            
            return jsonify({
                'success': True,
                'message': 'Query completed successfully',
                'query': query,
                'response_content': copied_content,
                'content_length': len(copied_content) if copied_content else 0,
                'generation_time_seconds': max_wait_time if stable_count < required_stable_checks else (max_wait_time // check_interval - stable_count + required_stable_checks) * check_interval
            })
    
    except Exception as e:
        logger.error(f"Error querying NotebookLM: {str(e)}")
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
    Additional endpoint to check the status of the browser instance
    """
    global browser_instance
    
    try:
        with browser_lock:
            if browser_instance:
                try:
                    current_url = browser_instance.current_url
                    return jsonify({
                        'browser_active': True,
                        'current_url': current_url,
                        'status': 'ready'
                    })
                except Exception as e:
                    # Browser might be closed or unresponsive
                    browser_instance = None
                    return jsonify({
                        'browser_active': False,
                        'status': 'inactive',
                        'error': str(e)
                    })
            else:
                return jsonify({
                    'browser_active': False,
                    'status': 'not_initialized'
                })
    
    except Exception as e:
        return jsonify({'error': f'Failed to get status: {str(e)}'}), 500

