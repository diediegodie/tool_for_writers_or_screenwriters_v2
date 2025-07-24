#!/bin/bash
# Unified test runner for ALL tests (backend, GUI, integration, smoke)
# Always use this script to run tests. Do NOT run pytest directly.
# See docs/TESTING_STANDARD.md for details and rationale.

set -e

echo "[run_all_tests.sh] Running all backend and GUI tests except the smoke test..."
PYTHONPATH=. pytest tests/ --maxfail=1 --disable-warnings -v --ignore=tests/smoke/test_main_smoke.py

echo "[run_all_tests.sh] Running smoke test (QApplication entry point) in isolation..."
PYTHONPATH=. pytest tests/smoke/test_main_smoke.py --maxfail=1 --disable-warnings -v

echo "[run_all_tests.sh] All tests completed."
