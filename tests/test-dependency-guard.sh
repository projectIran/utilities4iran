#!/bin/bash

# ==============================================================================
# TACTICAL TEST SUITE: dependency-guard.sh
# Objective: Prove the CI/CD guard breaks the build on operational violations.
# ==============================================================================

GUARD_SCRIPT="$(pwd)/scripts/dependency-guard.sh"
TEST_DIR="/tmp/utilities4iran-guard-test"

# Ensure the guard script actually exists before testing
if [ ! -f "$GUARD_SCRIPT" ]; then
    echo "[FATAL] Guard script not found at $GUARD_SCRIPT"
    exit 1
fi

echo "========================================"
echo "Initiating Dependency Guard Stress Test"
echo "========================================"

# Setup isolated sandbox
rm -rf "$TEST_DIR"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR" || exit 1
git init --quiet
git config user.email "test@tactical.local"
git config user.name "Test Runner"

# Function to evaluate tests
run_test() {
    local test_name=$1
    local expected_exit=$2
    local file_to_stage=$3

    # Stage the file
    mkdir -p "$(dirname "$file_to_stage")"
    touch "$file_to_stage"
    git add "$file_to_stage"

    # Run the guard
    "$GUARD_SCRIPT" > /dev/null 2>&1
    local actual_exit=$?

    # Clean the index for the next test
    git rm -r --cached . > /dev/null 2>&1
    rm -rf "$file_to_stage"

    if [ "$actual_exit" -eq "$expected_exit" ]; then
        echo "[PASS] $test_name"
    else
        echo "[FAIL] $test_name (Expected exit $expected_exit, got $actual_exit)"
        echo "--> PERIMETER BREACH DETECTED. FIX THE GUARD SCRIPT."
        rm -rf "$TEST_DIR"
        exit 1
    fi
}

# ------------------------------------------------------------------------------
# THE ATTACK VECTORS
# ------------------------------------------------------------------------------

# Test 1: Valid Baseline (Should Pass)
run_test "Valid Source Code (src/main.py)" 0 "src/main.py"

# Test 2: Node Bloat (Should Fail)
run_test "Vendored Payload (node_modules/hack.js)" 1 "node_modules/hack.js"

# Test 3: Environment Leak (Should Fail)
run_test "Secret Leak (.env.production)" 1 ".env.production"

# Test 4: Compiled Python Blob (Should Fail)
run_test "Python Cache Blob (__pycache__/core.pyc)" 1 "categories/bot/__pycache__/core.pyc"

# Test 5: Build Artifact (Should Fail)
run_test "Compiled Binary (dist/bundle.js)" 1 "dist/bundle.js"

# ------------------------------------------------------------------------------
# TEARDOWN
# ------------------------------------------------------------------------------
rm -rf "$TEST_DIR"
echo "========================================"
echo "ALL TESTS PASSED. PERIMETER SECURE."
echo "========================================"
exit 0