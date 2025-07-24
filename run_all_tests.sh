#!/bin/bash
# run_all_tests.sh - Single entry point for all project tests (GUI, backend, future E2E, etc.)
# Usage: ./run_all_tests.sh
# Reason: Ensures all contributors and LLMs use a single, up-to-date entry point for testing.

set -e

echo "Running all GUI and backend tests except the smoke test..."
PYTHONPATH=. pytest tests/gui tests/backend tests/gui/test_kanban_board_logic.py --ignore=tests/smoke/test_main_smoke.py --maxfail=1 --disable-warnings -v
echo "Running smoke test (QApplication entry point) separately..."
PYTHONPATH=. pytest tests/smoke/test_main_smoke.py --maxfail=1 --disable-warnings -v
echo "All tests completed."
