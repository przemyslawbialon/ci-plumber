# Development Setup Guide

Quick guide to development tools in the project.

## 🚀 Quick Start

```bash
# Install dev dependencies
source venv/bin/activate
pip install -r requirements-dev.txt

# Install pre-commit hooks
make install-hooks
```

## 🛠️ Tools

### Black (Formatter)
- **Max line length**: 100 characters
- **Config**: `pyproject.toml`
- Automatically formats code to a consistent style

### isort (Import Sorter)
- Sorts imports alphabetically
- Compatible with Black

### flake8 (Linter)
- Checks code for errors
- **Config**: `.flake8`

### pre-commit
- Automatically runs tools before commit
- **Config**: `.pre-commit-config.yaml`

## 📝 Commands

### Format code
```bash
make format
```
Formats all Python files.

### Check code (without changes)
```bash
make check
```
Checks if code is properly formatted.

### Test configuration
```bash
make test
```

### Clean cache
```bash
make clean
```

### Help
```bash
make help
```

## 🔄 Workflow

### 1. Before starting work
```bash
git pull
source venv/bin/activate
```

### 2. During work
Write code normally, don't worry about formatting.

### 3. Before commit
Pre-commit hooks automatically:
- ✅ Format code (Black)
- ✅ Sort imports (isort)  
- ✅ Check errors (flake8)
- ✅ Remove trailing whitespace
- ✅ Fix end of file

### 4. Commit
```bash
git add .
git commit -m "your message"
```

If pre-commit fixes something:
```bash
git add .
git commit -m "your message"
```

## ⚠️ Troubleshooting

### Pre-commit not working
```bash
# Reinstall hooks
make install-hooks
```

### Need to bypass pre-commit (emergency)
```bash
git commit --no-verify -m "emergency fix"
```
**Not recommended! Use only in exceptional situations.**

### Manually run pre-commit on all files
```bash
pre-commit run --all-files
```

## 📚 More Info

See `CONTRIBUTING.md` for full documentation.
