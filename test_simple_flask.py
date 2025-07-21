#!/usr/bin/env python3
"""
Simplified Flask test without Selenium dependencies
"""

from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        'browser_active': False,
        'status': 'test_mode',
        'message': 'Flask app is working correctly'
    })

@app.route('/api/open_notebooklm', methods=['POST'])
def open_notebooklm():
    return jsonify({
        'success': False,
        'error': 'Selenium not available in test mode',
        'status': 'test_mode'
    })

@app.route('/api/query_notebooklm', methods=['POST'])
def query_notebooklm():
    return jsonify({
        'success': False,
        'error': 'Selenium not available in test mode',
        'status': 'test_mode'
    })

@app.route('/api/close_browser', methods=['POST'])
def close_browser():
    return jsonify({
        'success': True,
        'message': 'No browser to close in test mode',
        'status': 'test_mode'
    })

@app.route('/')
def index():
    return '''
    <html>
    <head><title>NotebookLM Automation Test</title></head>
    <body>
        <h1>NotebookLM Automation API - Test Mode</h1>
        <p>Flask application is running correctly!</p>
        <ul>
            <li><a href="/api/status">Status Endpoint</a></li>
        </ul>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("🚀 Starting simplified Flask test server...")
    app.run(host='0.0.0.0', port=5001, debug=True)

