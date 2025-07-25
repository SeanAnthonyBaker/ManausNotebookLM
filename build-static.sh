#!/bin/bash

# This script minifies CSS and JavaScript files for production.

# Exit immediately if a command exits with a non-zero status.
set -e

# Define source and destination directories
STATIC_DIR="static"
DIST_DIR="static/dist"

# Create the destination directory if it doesn't exist
mkdir -p "$DIST_DIR"

# Minify CSS
echo "Minifying CSS..."
cleancss -o "$DIST_DIR/style.min.css" "$STATIC_DIR/style.css"

# Minify JavaScript
echo "Minifying JavaScript..."
uglifyjs "$STATIC_DIR/script.js" -o "$DIST_DIR/script.min.js" -c -m

echo "✅ Frontend assets have been minified."
