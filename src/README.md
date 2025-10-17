# Source Code Modules

This directory contains the modular implementation of CI Plumber.

## Modules

### `main.py`
Entry point for the application. Initializes CI Plumber and starts the run.

### `ci_plumber.py`
Main orchestrator class that coordinates all operations:
- Initializes all handlers
- Manages the main run loop
- Processes individual PRs

### `config_loader.py`
Configuration management:
- Loads YAML configuration from `cfg/config.yaml`
- Handles path resolution

### `logger_setup.py`
Logging infrastructure:
- `ColoredFormatter` - Adds colors and emojis to console output
- `setup_logging()` - Configures file and console logging

### `github_handler.py`
GitHub operations:
- Finding PRs with target label
- Managing labels
- Checking and updating branches
- Checking CI status
- Determining merge readiness
- Merging PRs

### `linter_fixer.py`
Linter auto-fix functionality:
- Cloning/updating local repository
- Running linter fix commands
- Committing and pushing fixes

### `chromatic_handler.py`
Chromatic test retry:
- Finding failed Chromatic checks
- Re-running failed workflows
- Requesting check re-runs

## Design Principles

- **Separation of Concerns**: Each module handles a specific domain
- **Single Responsibility**: Each class has one clear purpose
- **Dependency Injection**: Handlers receive dependencies (config, logger) from main orchestrator
- **Error Handling**: Each module handles its own errors and logs appropriately

