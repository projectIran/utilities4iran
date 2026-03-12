#!/usr/bin/env bash
# test-snowflake.sh — Validate snowflake-proxy fail-safe behavior when the
# snowflake-client binary is absent from the environment.

set -u

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
MODULE_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
MAIN="$MODULE_ROOT/src/main.py"
PYTHON_BIN=${PYTHON_BIN:-$(command -v python3 2>/dev/null || command -v python 2>/dev/null)}
TMP_DIR=$(mktemp -d /tmp/snowflake-proxy-test.XXXXXX)

cleanup() { rm -rf "$TMP_DIR"; }
trap cleanup EXIT HUP INT TERM

fail() { printf '[FAIL] %s\n' "$1" >&2; exit 1; }
pass() { printf '[PASS] %s\n' "$1"; }

[ -f "$MAIN" ]           || fail "main.py not found at $MAIN"
[ -n "${PYTHON_BIN:-}" ] || fail "python3 is required"

STDOUT_LOG="$TMP_DIR/stdout.log"
STDERR_LOG="$TMP_DIR/stderr.log"

# Run with a stripped PATH and no SNOWFLAKE_BIN so the binary lookup fails.
env -i \
    PATH="/usr/bin:/bin" \
    HOME="$TMP_DIR" \
    "$PYTHON_BIN" "$MAIN" >"$STDOUT_LOG" 2>"$STDERR_LOG"
STATUS=$?

[ "$STATUS" -eq 1 ] || fail "Expected exit code 1 when binary is missing, got $STATUS"
pass "Script exits with code 1 when snowflake-client binary is not found"

grep -F 'snowflake-client binary not found' "$STDERR_LOG" >/dev/null 2>&1 \
    || fail "Expected clean [ERROR] message not found in stderr"
pass "Script emits the correct [ERROR] message for missing binary"

grep -qF 'Traceback' "$STDERR_LOG" \
    && fail "Script leaked a Python Traceback to stderr"
pass "Script suppresses Python Tracebacks on failure"

# Verify SNOWFLAKE_BIN pointing at a non-executable path also fails cleanly.
FAKE_BIN="$TMP_DIR/snowflake-client-fake"
touch "$FAKE_BIN"   # exists but not executable

STDERR2="$TMP_DIR/stderr2.log"
env -i \
    PATH="/usr/bin:/bin" \
    HOME="$TMP_DIR" \
    SNOWFLAKE_BIN="$FAKE_BIN" \
    "$PYTHON_BIN" "$MAIN" >"$TMP_DIR/stdout2.log" 2>"$STDERR2"
STATUS2=$?

[ "$STATUS2" -eq 1 ] || fail "Expected exit code 1 for non-executable SNOWFLAKE_BIN, got $STATUS2"
grep -F 'is not an executable file' "$STDERR2" >/dev/null 2>&1 \
    || fail "Expected non-executable SNOWFLAKE_BIN error message not found"
grep -qF 'Traceback' "$STDERR2" \
    && fail "Script leaked a Python Traceback for non-executable SNOWFLAKE_BIN"
pass "Script exits cleanly when SNOWFLAKE_BIN is not executable"

printf '[PASS] snowflake-proxy test suite completed successfully\n'
