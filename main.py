import os
import threading
import signal
import logging
from flask import Flask, send_from_directory
from flask_cors import CORS
from models import db
from user import user_bp
from notebooklm import notebooklm_bp, browser_instance, browser_lock, start_browser_initialization_thread

# Configure logging for the application
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Load secret key from environment variable for better security
SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'a-default-insecure-secret-key-for-dev')
if SECRET_KEY == 'a-default-insecure-secret-key-for-dev' and os.environ.get('FLASK_ENV') == 'production':
    logging.warning("SECURITY WARNING: Using default insecure secret key in production. Set the FLASK_SECRET_KEY environment variable.")
app.config['SECRET_KEY'] = SECRET_KEY

# Enable CORS for all routes
CORS(app)

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(notebooklm_bp, url_prefix='/api')

# Ensure the database directory exists
db_path = os.path.join(os.path.dirname(__file__), 'database')
os.makedirs(db_path, exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(db_path, 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context(): # Creates tables if they don't exist
    db.create_all()

# Graceful shutdown handler
def graceful_shutdown(signum, frame):
    """Ensures the browser is closed cleanly on app termination."""
    logging.info("Shutdown signal received. Closing browser instance...")
    with browser_lock:
        if browser_instance:
            try:
                browser_instance.quit()
                logging.info("Browser instance closed successfully.")
            except Exception as e:
                logging.error(f"Error during browser cleanup: {e}")
    exit(0)

signal.signal(signal.SIGINT, graceful_shutdown)
signal.signal(signal.SIGTERM, graceful_shutdown)

# Start browser initialization in a background thread
start_browser_initialization_thread()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    # If a specific file is requested and it exists in the static folder, serve it.
    if path and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        # Otherwise, serve the main index.html file for any other route.
        # This is common for Single Page Applications (SPAs).
        return send_from_directory(static_folder_path, 'index.html')


if __name__ == '__main__':
    # Use the PORT environment variable if it's set, otherwise default to 5000
    port = int(os.environ.get('PORT', 5000))
    # The debug flag should be False in a production environment
    debug = os.environ.get('FLASK_ENV') != 'production'
    logging.info(f"Starting server on host 0.0.0.0, port {port}, debug={debug}")
    app.run(host='0.0.0.0', port=port, debug=debug)
