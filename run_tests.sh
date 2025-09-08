#!/bin/bash
# run_tests.sh - run pytest with optional args and pylint on production code

# Exit immediately if any command fails
set -e

# Arguments passed to the script will go to pytest
PYTEST_ARGS="$@"

echo "Running tests with pytest $PYTEST_ARGS..."
pytest tests/ $PYTEST_ARGS --disable-warnings

echo
echo "Running pylint on production code..."
pylint . --ignore=.venv --disable=C0114,C0115,C0116,W0511
