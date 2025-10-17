# CI Plumber

Automated Pull Request management system for Dapulse/dapulse repository. This tool automatically processes PRs labeled with `ci-plumber-to-merge`, fixes common issues, and merges them when ready.

## Features

- **Automatic Label Management**: Adds missing labels (`Monoreason: Large effort`, `workdays: Mon-Fri`)
- **Branch Synchronization**: Updates branches that are too far behind master (>100 commits)
- **Linter Auto-Fix**: Clones the repo, runs `npm run eslint:changed:master`, commits and pushes fixes
- **Chromatic Retry**: Automatically retries failed Chromatic tests
- **Auto-Merge**: Merges PRs when all checks pass and approvals are in place
- **Comprehensive Logging**: Detailed logs for all operations

## Quick Start

### Automatic Installation

The `MONDAY_PATH` environment variable should already be set by your Monday.com profile. Verify it's set:

```bash
echo $MONDAY_PATH
```

If not set for any reason, export it temporarily:
```bash
export MONDAY_PATH="/Users/Przemyslawb/Development"
```

Run the installation script:

```bash
cd $MONDAY_PATH/ci-plumber
./install.sh
```

The installation script will:
- Use `$MONDAY_PATH` to configure all paths dynamically
- Create a virtual environment
- Install Python dependencies
- Generate launchd plist with correct paths
- Set up the launchd service for hourly execution
- Test the configuration

**Note**: If `MONDAY_PATH` is not set, the script will prompt you for the path.

**Important**: After installation, edit `config.yaml` and add your GitHub Personal Access Token.

## Manual Setup

### 1. Verify Environment Variable

Ensure `MONDAY_PATH` is set (should be done by Monday.com profile):

```bash
echo $MONDAY_PATH
```

### 2. Create Virtual Environment and Install Dependencies

```bash
cd $MONDAY_PATH/ci-plumber
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure GitHub Token

Edit `config.yaml` and replace `PLACEHOLDER_TOKEN_HERE` with your GitHub Personal Access Token.

The token needs the following permissions:
- `repo` (full control of private repositories)
- `workflow` (update GitHub Action workflows)

To create a token:
1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with required permissions
3. Copy the token and paste it into `config.yaml`

### 4. Test Configuration

```bash
source venv/bin/activate
python test_config.py
```

This will verify your GitHub token and repository access.

### 5. Test Manual Run

```bash
source venv/bin/activate
python ci_plumber.py
```

Check the logs in `logs/ci-plumber-YYYY-MM-DD.log` to verify everything works.

### 6. Generate and Install launchd Service (Hourly Automation)

```bash
sed "s|{{PROJECT_PATH}}|$MONDAY_PATH/ci-plumber|g" com.ciplumber.plist.template > com.ciplumber.plist
cp com.ciplumber.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.ciplumber.plist
```

To verify it's loaded:
```bash
launchctl list | grep ciplumber
```

### 7. Manage the Service

**Stop the service:**
```bash
launchctl unload ~/Library/LaunchAgents/com.ciplumber.plist
```

**Start the service:**
```bash
launchctl load ~/Library/LaunchAgents/com.ciplumber.plist
```

**Run manually:**
```bash
./venv/bin/python ci_plumber.py
```

**View logs:**
```bash
tail -f logs/ci-plumber-$(date +%Y-%m-%d).log
```

## Configuration

Edit `config.yaml` to customize:

- **Repository settings**: Target repo, local clone path
- **Label configuration**: Required labels to auto-add
- **Linter command**: Command to fix linting issues
- **Branch distance threshold**: Maximum commits behind master before forcing update

## How It Works

1. **Discovery**: Finds all open PRs with label `ci-plumber-to-merge`
2. **Label Check**: Ensures required labels are present
3. **Branch Update**: Updates branch if too far behind master
4. **CI Analysis**: Checks for linter and Chromatic failures
5. **Auto-Fix**: 
   - Linter failures: Clones repo, runs fix command, commits & pushes
   - Chromatic failures: Retries the workflow
6. **Merge**: When all checks pass and PR is approved, automatically merges

## Troubleshooting

### MONDAY_PATH not set
If `MONDAY_PATH` is not set by your Monday.com profile, regenerate the plist file after setting it:
```bash
cd $MONDAY_PATH/ci-plumber
sed "s|{{PROJECT_PATH}}|$MONDAY_PATH/ci-plumber|g" com.ciplumber.plist.template > com.ciplumber.plist
cp com.ciplumber.plist ~/Library/LaunchAgents/
launchctl unload ~/Library/LaunchAgents/com.ciplumber.plist 2>/dev/null || true
launchctl load ~/Library/LaunchAgents/com.ciplumber.plist
```

### Service not running
```bash
launchctl list | grep ciplumber
```

If not listed, reload:
```bash
launchctl load ~/Library/LaunchAgents/com.ciplumber.plist
```

### Check launchd logs
```bash
cat logs/launchd-stdout.log
cat logs/launchd-stderr.log
```

### Permission issues
Ensure the GitHub token has correct permissions and hasn't expired.

### NPM/Node not found
Update the `PATH` in `com.ciplumber.plist.template` to include your Node.js installation path, then regenerate the plist file.

### Virtual environment issues
If you need to recreate the virtual environment:
```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Logs

All operations are logged to `logs/ci-plumber-YYYY-MM-DD.log` with:
- Timestamp for each operation
- PR numbers and titles being processed
- Actions taken (label additions, branch updates, fixes applied)
- Success/failure status
- Error details when issues occur

