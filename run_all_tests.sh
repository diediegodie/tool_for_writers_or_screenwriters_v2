#!/bin/bash
# run_all_tests.sh - Single entry point for all project tests (GUI, backend, future E2E, etc.)
# Usage: ./run_all_tests.sh
# Reason: Ensures all contributors and LLMs use a single, up-to-date entry point for testing.

set -e

echo "All tests completed."
echo "Running all GUI and backend tests..."
PYTHONPATH=. pytest tests/ --maxfail=1 --disable-warnings -v -m 'not smoke'
echo "Running smoke tests (non-GUI QApplication)..."
PYTHONPATH=. pytest tests/smoke/ --maxfail=1 --disable-warnings -v -m smoke
echo "All tests completed."
