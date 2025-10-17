# Configuration Files

This directory contains configuration files for CI Plumber.

## Files

### `config.yaml` (gitignored)
Main configuration file containing:
- GitHub token (keep this secret!)
- Repository settings
- Label configuration
- Linter commands
- Logging settings

**Important**: This file is gitignored and contains sensitive data (GitHub token). Never commit this file to version control.

### `config.yaml.example`
Example configuration file with placeholders. Use this as a template to create your `config.yaml`.

## Initial Setup

1. Copy the example file:
   ```bash
   cp cfg/config.yaml.example cfg/config.yaml
   ```

2. Edit `cfg/config.yaml` and replace `PLACEHOLDER_TOKEN_HERE` with your actual GitHub token.

3. Customize other settings as needed (labels, paths, commands).

## Configuration Options

### GitHub Settings
- `token`: Personal Access Token with appropriate permissions
- `repo`: Target repository (e.g., "Dapulse/dapulse")

### Labels
- `trigger`: Label that triggers CI Plumber processing
- `auto_add`: Labels automatically added to PRs if missing
- `categories`: Label categories with prefix-based logic
  - `prefix`: Label prefix to check (e.g., "Monoreason:")
  - `default`: Default label to add if no label with this prefix exists

### Repository
- `local_path`: Path where repository will be cloned for linter fixes
- `max_commits_behind`: Maximum commits behind master before forcing branch update

### Linter
- `fix_command`: Command to run for linter auto-fix

### Logging
- `level`: Log level (DEBUG, INFO, WARNING, ERROR)
- `directory`: Directory for log files

