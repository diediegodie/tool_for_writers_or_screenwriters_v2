#!/bin/bash
# run_all_tests.sh - Single entry point for all project tests (GUI, backend, future E2E, etc.)
# Usage: ./run_all_tests.sh
# Reason: Ensures all contributors and LLMs use a single, up-to-date entry point for testing.

set -e

# Run GUI (PySide6) tests
echo "Running GUI tests..."
PYTHONPATH=. pytest tests/gui/

# Run backend tests (uncomment when backend is ready)
# echo "Running backend tests..."
# PYTHONPATH=. pytest tests/backend/

# Run E2E or other test suites (add as needed)
# echo "Running E2E tests..."
# npx playwright test

# Add new test commands above as features are added

echo "All tests completed."
