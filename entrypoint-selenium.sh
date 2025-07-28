#!/bin/bash
set -e

# Path to the read-only gcloud credentials mounted from the host
GCLOUD_RO_CREDS_DIR="/gcloud_creds_ro"
GCLOUD_WRITABLE_CONFIG_DIR="/home/seluser/.config/gcloud"

# The directory where the Chrome profile is stored inside the container.
PROFILE_DIR="/data"

echo "Custom Selenium Entrypoint: Checking for Chrome profile..."

# Only download the profile if the target directory is empty.
# This allows a local bind mount during development to override the download.
if [ -z "$(ls -A $PROFILE_DIR 2>/dev/null)" ]; then
  echo "$PROFILE_DIR is empty. Attempting to download profile from GCS."
  
  if [ -z "$CHROME_PROFILE_GCS_PATH" ]; then
    echo "WARNING: CHROME_PROFILE_GCS_PATH is not set. Browser will start with a fresh profile."
  else
    # First, check that the gcloud credentials directory was mounted successfully from the host.
    if [ ! -d "$GCLOUD_RO_CREDS_DIR" ] || [ -z "$(ls -A $GCLOUD_RO_CREDS_DIR 2>/dev/null)" ]; then
      echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
      echo "ERROR: gcloud credentials not found or empty in the container at $GCLOUD_RO_CREDS_DIR."
      echo "This is likely because the host directory specified by GCLOUD_CONFIG_PATH in your .env file is missing, empty, or could not be mounted."
      echo "Please check the following on your host machine:"
      echo "1. Your project root has a '.env' file with the line: GCLOUD_CONFIG_PATH=./.gcloud"
      echo "2. Your project root has a directory named '.gcloud' containing your credential files (like 'credentials.db')."
      echo "3. You are using 'start.bat' to launch the application, which verifies this setup."
      echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
      exit 1
    fi

    # gcloud needs a writable config directory. We copy the read-only credentials
    # from the host mount to a writable location inside the container.
    echo "Setting up writable gcloud config directory..."
    mkdir -p "$GCLOUD_WRITABLE_CONFIG_DIR"
    cp -rL "$GCLOUD_RO_CREDS_DIR/." "$GCLOUD_WRITABLE_CONFIG_DIR/"

    echo "Verifying gcloud authentication..."
    # The gcloud command will now use the default config path, which is now writable.
    gcloud auth list --quiet || {
      echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
      echo "ERROR: 'gcloud auth list' failed. The provided credentials may be invalid or expired."
      echo "Please run 'gcloud auth login' on your host machine and copy the updated credentials to the '.gcloud' directory."
      echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
      exit 1
    }
    echo "Downloading profile from $CHROME_PROFILE_GCS_PATH to $PROFILE_DIR..."
    gcloud storage cp -r "${CHROME_PROFILE_GCS_PATH}/*" "$PROFILE_DIR/" --quiet || {
      echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
      echo "ERROR: Failed to download Chrome profile from GCS path: $CHROME_PROFILE_GCS_PATH"
      echo "Please verify that the GCS path is correct and that your authenticated user has 'Storage Object Viewer' permissions on the bucket."
      echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
      exit 1
    }
    echo "Profile download complete."
    echo "Listing downloaded profile contents:"
    ls -la $PROFILE_DIR
  fi
else
  echo "$PROFILE_DIR is not empty. Skipping GCS download (assuming local volume mount)."
fi

echo "Starting original Selenium entrypoint..."
exec /opt/bin/entry_point.sh