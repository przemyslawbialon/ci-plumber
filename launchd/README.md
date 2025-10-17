# launchd Service Files

This directory contains macOS launchd service configuration files.

## Files

### `com.ciplumber.plist.template`
Template file with placeholder `{{PROJECT_PATH}}` that gets replaced during installation.

### `com.ciplumber.plist` (generated, gitignored)
Generated plist file with actual paths. This file is created by `install.sh` and should not be committed to git.

## Usage

The plist file is automatically generated and installed by `install.sh`. 

For manual installation:
```bash
# Generate plist with correct paths
sed "s|{{PROJECT_PATH}}|/your/path/to/ci-plumber|g" launchd/com.ciplumber.plist.template > launchd/com.ciplumber.plist

# Copy to LaunchAgents
cp launchd/com.ciplumber.plist ~/Library/LaunchAgents/

# Load the service
launchctl load ~/Library/LaunchAgents/com.ciplumber.plist
```

## Service Configuration

The service runs every hour (3600 seconds) and executes:
- Python from virtual environment: `{PROJECT_PATH}/venv/bin/python`
- Main script: `{PROJECT_PATH}/ci_plumber.py`
- Working directory: `{PROJECT_PATH}`
- Logs: `{PROJECT_PATH}/logs/launchd-stdout.log` and `launchd-stderr.log`

