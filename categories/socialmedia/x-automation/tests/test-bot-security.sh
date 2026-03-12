#!/usr/bin/env bash

set -u

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
MODULE_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
BOT_PATH="$MODULE_ROOT/src/bot.py"

PYTHON_BIN=$(command -v python3 2>/dev/null || command -v python 2>/dev/null)
STDOUT_LOG=$(mktemp /tmp/x-bot-security.stdout.XXXXXX)
STDERR_LOG=$(mktemp /tmp/x-bot-security.stderr.XXXXXX)
MATCH_LOG=$(mktemp /tmp/x-bot-security.grep.XXXXXX)

cleanup() {
    rm -f "$STDOUT_LOG" "$STDERR_LOG" "$MATCH_LOG"
}

trap cleanup EXIT HUP INT TERM

fail() {
    printf '[FAIL] %s\n' "$1" >&2
    exit 1
}

pass() {
    printf '[PASS] %s\n' "$1"
}

[ -f "$BOT_PATH" ] || fail "Bot script not found at $BOT_PATH"
[ -n "${PYTHON_BIN:-}" ] || fail "python3 or python is required to execute the bot"

if env -i "$PYTHON_BIN" "$BOT_PATH" --dry-run >"$STDOUT_LOG" 2>"$STDERR_LOG"; then
    fail "Bot unexpectedly succeeded without environment credentials"
else
    status=$?
fi

[ "$status" -ne 0 ] || fail "Bot returned a zero exit code in a stripped environment"
pass "Bot fails closed in a stripped environment"

if grep -F "Traceback" "$STDERR_LOG" >/dev/null 2>&1; then
    fail "Bot leaked a Python Traceback to stderr under missing-credential conditions"
fi
pass "Bot suppresses Python Traceback output during fail-safe exit"

if grep -nE 'api_key=|bearer_token=|AIza|ghp_' "$BOT_PATH" >"$MATCH_LOG" 2>/dev/null; then
    printf '[FAIL] Hardcoded secret indicators found in source:\n' >&2
    cat "$MATCH_LOG" >&2
    exit 1
fi
pass "Bot source contains no hardcoded secret indicators"

printf '[PASS] X-Bot security checks completed successfully\n'