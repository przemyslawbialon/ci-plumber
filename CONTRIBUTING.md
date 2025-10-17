# Contributing to CI Plumber

## Development Setup

### 1. Install Development Dependencies

```bash
pip install -r requirements-dev.txt
```

### 2. Install Pre-commit Hooks

Pre-commit hooks will automatically format your code before each commit:

```bash
make install-hooks
# or
pre-commit install
```

## Code Style

This project uses:
- **Black** for code formatting (line length: 100)
- **isort** for import sorting
- **flake8** for linting

### Format Code Manually

```bash
make format
```

### Check Code Style

```bash
make check
```

### Pre-commit Hooks

Once installed, pre-commit will automatically run on `git commit`:
- Format code with Black
- Sort imports with isort
- Check code with flake8
- Remove trailing whitespace
- Fix end of files
- Check YAML syntax

If any hook fails, the commit will be aborted. Fix the issues and commit again.

### Skip Hooks (Not Recommended)

Only in emergency situations:
```bash
git commit --no-verify -m "your message"
```

## Testing

```bash
make test
```

## Common Tasks

```bash
make help          # Show all available commands
make format        # Format all Python files
make check         # Check without modifying files
make clean         # Remove cache files
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run `make format` to format code
5. Run `make check` to verify
6. Run `make test` to test
7. Commit (pre-commit hooks will run automatically)
8. Push and create a Pull Request

