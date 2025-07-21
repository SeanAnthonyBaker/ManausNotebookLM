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
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_flask_app():
    """Test if the Flask application starts correctly"""
    print("🧪 Testing Flask Application...")
    
    # Test basic Flask app import
    try:
        from src.main import app
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

def test_api_endpoints():
    """Test API endpoints (requires running Flask server)"""
    base_url = "http://localhost:5000"
    
    print("\n🌐 Testing API Endpoints...")
    
    # Test status endpoint
    try:
        response = requests.get(f"{base_url}/api/status", timeout=5)
        print(f"✅ Status endpoint: {response.status_code}")
        print(f"   Response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Status endpoint failed: {e}")
        return False
    
    # Test open_notebooklm endpoint (should fail without Selenium)
    try:
        response = requests.post(f"{base_url}/api/open_notebooklm", 
                               json={"notebooklm_url": "https://notebooklm.google.com/"}, 
                               timeout=10)
        print(f"📝 Open NotebookLM endpoint: {response.status_code}")
        result = response.json()
        if "error" in result:
            print(f"   Expected error (no Selenium): {result['error'][:100]}...")
        else:
            print(f"   Unexpected success: {result}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Open NotebookLM endpoint failed: {e}")
    
    # Test close_browser endpoint
    try:
        response = requests.post(f"{base_url}/api/close_browser", timeout=5)
        print(f"🔒 Close browser endpoint: {response.status_code}")
        print(f"   Response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Close browser endpoint failed: {e}")
    
    return True

def test_web_interface():
    """Test if the web interface is accessible"""
    print("\n🌐 Testing Web Interface...")
    
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        if response.status_code == 200:
            print("✅ Web interface accessible")
            if "NotebookLM Automation API" in response.text:
                print("✅ Web interface content correct")
            else:
                print("⚠️  Web interface content unexpected")
        else:
            print(f"❌ Web interface returned {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Web interface failed: {e}")

def main():
    """Main test function"""
    print("🚀 NotebookLM Automation - Local Testing")
    print("=" * 50)
    
    # Test 1: Flask app import and basic functionality
    if not test_flask_app():
        print("\n❌ Basic Flask tests failed. Exiting.")
        return False
    
    print("\n✅ Basic Flask tests passed!")
    print("\n📋 To test API endpoints:")
    print("1. Start the Flask server in another terminal:")
    print("   cd /home/ubuntu/notebooklm-automation")
    print("   source venv/bin/activate")
    print("   python src/main.py")
    print("\n2. Run this script again with --api flag:")
    print("   python test_local.py --api")
    
    # If --api flag is provided, test API endpoints
    if "--api" in sys.argv:
        print("\n" + "=" * 50)
        test_api_endpoints()
        test_web_interface()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

