.PHONY: format check install-hooks test clean

format:
	@echo "🎨 Formatting code with Black..."
	@black src/ test_config.py ci_plumber.py
	@echo "📦 Sorting imports with isort..."
	@isort src/ test_config.py ci_plumber.py
	@echo "✅ Formatting complete!"

check:
	@echo "🔍 Checking code formatting..."
	@black --check src/ test_config.py ci_plumber.py
	@isort --check src/ test_config.py ci_plumber.py
	@flake8 src/ test_config.py ci_plumber.py
	@echo "✅ All checks passed!"

install-hooks:
	pre-commit install
	@echo "✅ Pre-commit hooks installed!"

test:
	python test_config.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

help:
	@echo "Available commands:"
	@echo "  make format        - Format code with black and isort"
	@echo "  make check         - Check code formatting without changes"
	@echo "  make install-hooks - Install pre-commit hooks"
	@echo "  make test          - Run configuration tests"
	@echo "  make clean         - Remove Python cache files"
