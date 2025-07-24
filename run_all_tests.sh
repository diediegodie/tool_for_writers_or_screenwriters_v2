#!/bin/bash
# Run all tests (backend and GUI)

set -e

echo "Running all GUI and backend tests except the smoke test..."
PYTHONPATH=. pytest tests/backend --maxfail=2 -v

echo "Running GUI tests (with xvfb for headless/Wayland compatibility)..."
PYTHONPATH=. xvfb-run -a pytest tests/gui --maxfail=2 -v

echo "Running smoke test (QApplication entry point) separately..."
PYTHONPATH=. pytest tests/smoke --maxfail=2 -v
echo "All tests completed."
