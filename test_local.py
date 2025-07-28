#!/usr/bin/env python3
"""
Local test script for NotebookLM Automation API
Tests the Flask application without Docker dependencies
"""

import sys
import os
import requests
import time
import json

# Add the src directory to Python path
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_flask_app():
    """Test if the Flask application starts correctly"""
    print("🧪 Testing Flask Application...")
    
    # Test basic Flask app import
    try:
        from main import app
        print("✅ Flask app imports successfully")
    except ImportError as e:
        print(f"❌ Failed to import Flask app: {e}")
        return False
    
    # Test app configuration
    try:
        with app.app_context():
            print("✅ Flask app context works")
    except Exception as e:
        print(f"❌ Flask app context error: {e}")
        return False
    
    return True

def run_live_tests():
    """Run tests against a live server, reporting all results."""
    base_url = "http://localhost:5000"
    successes = 0
    failures = 0

    print("🌐 Testing Live Server Endpoints...")

    def run_test(name, test_func, expected_status=200, check_json=None):
        nonlocal successes, failures
        print(f"▶️  Running: {name}")
        try:
            response = test_func()
            if response.status_code != expected_status:
                print(f"❌ FAILED: Expected status {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                failures += 1
                return None

            if check_json:
                json_data = response.json()
                if not check_json(json_data):
                    print("❌ FAILED: JSON content check failed.")
                    print(f"   Response JSON: {json.dumps(json_data, indent=2)}")
                    failures += 1
                    return None

            print("✅ PASSED")
            successes += 1
            return response.json() if "application/json" in response.headers.get("Content-Type", "") else response.text
        except requests.exceptions.RequestException as e:
            print(f"❌ FAILED with connection error: {e}")
            failures += 1
            return None

    # --- Test Sequence ---
    print("\n--- Step 1: Wait for Browser Initialization ---")
    print("Waiting up to 45 seconds for the background browser to start...")
    initialization_complete = False
    for i in range(15):
        time.sleep(3)
        try:
            status_res = requests.get(f"{base_url}/api/status", timeout=2).json()
            if status_res.get('browser_active'):
                print(f"✅ Browser is active! Status: {status_res.get('status')}")
                initialization_complete = True
                break
            else:
                print("   ... still waiting (browser_active is False)")
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            print(f"   ... error checking status: {e}")

    if not initialization_complete:
        print("❌ FAILED: Browser did not initialize in time. Cannot proceed with further tests.")
        failures += 1
    else:
        # Check the status again to see if login is required
        try:
            final_status_res = requests.get(f"{base_url}/api/status", timeout=2).json()
            if final_status_res.get('status') == 'authentication_required':
                print("\n❌ ACTION REQUIRED: Browser needs manual login.")
                print("   The browser inside the container has been redirected to a Google sign-in page.")
                print("\n   Please do the following:")
                print("   1. Connect to the container with a VNC viewer at: localhost:5900 (password: secret)")
                print("   2. Manually complete the Google login process in the browser window.")
                print("   3. Once logged in, stop this test (Ctrl+C) and the Flask server.")
                print("   4. The login session will be saved. Restart the Flask server and run this test again.")
                failures += 1
            else:
                # Only run these tests if login is not required
                successes += 1
                print("\n--- Step 2: Open NotebookLM URL ---")
                run_test(
                    "POST /api/open_notebooklm",
                    lambda: requests.post(f"{base_url}/api/open_notebooklm", json={"notebooklm_url": "https://notebooklm.google.com/"}, timeout=45),
                    check_json=lambda data: data.get('success') is True
                )
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            print(f"❌ FAILED: Could not get final browser status. Error: {e}")
            failures += 1

    print("\n--- Step 3: Close Browser ---")
    run_test(
        "POST /api/close_browser",
        lambda: requests.post(f"{base_url}/api/close_browser", timeout=10),
        check_json=lambda data: data.get('success') is True
    )

    print("-" * 50)
    print(f"Test Summary: {successes} passed, {failures} failed.")
    return failures == 0

def main():
    """Main test function"""
    print("🚀 NotebookLM Automation - Local Testing")
    print("=" * 50)
    
    # Test 1: Flask app import and basic functionality
    if not test_flask_app():
        print("""
❌ Basic Flask tests failed. Exiting.""")
        return False
    
    print("""
✅ Basic Flask tests passed!""")
    print("""
📋 To run the full application stack (Flask App + Selenium):

1. **(One-Time Setup) Authenticate with Google Cloud:**
   This allows the Selenium container to download the pre-authenticated Chrome profile.
   Run this command in your terminal and follow the browser prompts:
   `gcloud auth login`

2. **Start the Application:**
   - **On Windows:** Open a Command Prompt and run:
     `start.bat`
   - **On macOS/Linux:** Open a terminal and run:
     `./start.sh`

   This will build and start both the `app` and `selenium` services using docker-compose.
   The services will be available at:
   - Flask API: http://localhost:5000
   - VNC Viewer: http://localhost:7900 (password: secret)

3. **Run API & Web Tests (Terminal 3):**
   In a new terminal (with venv activated), run the tests:
   python test_local.py --api
""")
    
    # If --api flag is provided, test API endpoints
    if "--api" in sys.argv:
        print("""
""" + "=" * 50)
        run_live_tests()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
