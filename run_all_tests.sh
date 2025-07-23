#!/bin/bash
# run_all_tests.sh – Run all project tests (frontend, backend, E2E)
# Usage: ./run_all_tests.sh
# Add every new test command here!

set -e

# Frontend unit/integration tests
cd frontend && npm test -- --watchAll=false --ci && cd ..

# Backend tests (uncomment when backend is ready)
# cd backend && pytest && cd ..

# E2E tests (uncomment when Playwright is set up)
# cd frontend && npx playwright test && cd ..

# Add new test commands above as features are added
