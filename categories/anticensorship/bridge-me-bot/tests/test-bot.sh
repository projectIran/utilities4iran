#!/usr/bin/env bash

set -u

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
MODULE_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
MAIN_PATH="$MODULE_ROOT/src/main.py"
PYTHON_BIN=${PYTHON_BIN:-$(command -v python3 2>/dev/null || command -v python 2>/dev/null)}
TMP_DIR=$(mktemp -d /tmp/bridge-me-bot-test.XXXXXX)

cleanup() {
    rm -rf "$TMP_DIR"
}

trap cleanup EXIT HUP INT TERM

fail() {
    printf '[FAIL] %s\n' "$1" >&2
    exit 1
}

pass() {
    printf '[PASS] %s\n' "$1"
}

[ -f "$MAIN_PATH" ] || fail "main.py not found at $MAIN_PATH"
[ -n "${PYTHON_BIN:-}" ] || fail "python3 or python is required"

SUCCESS_STDOUT="$TMP_DIR/success.stdout"
SUCCESS_STDERR="$TMP_DIR/success.stderr"

env -i \
    V2RAY_UUID='11111111-2222-4333-8444-555555555555' \
    V2RAY_SERVER_IP='203.0.113.10' \
    V2RAY_SNI_DOMAIN='edge.example.org' \
    "$PYTHON_BIN" "$MAIN_PATH" --cli >"$SUCCESS_STDOUT" 2>"$SUCCESS_STDERR"
STATUS=$?

[ "$STATUS" -eq 0 ] || fail "CLI mode failed, expected exit 0 got $STATUS"
[ ! -s "$SUCCESS_STDERR" ] || fail "CLI mode wrote unexpected stderr output"

FIRST_LINE=$(head -n 1 "$SUCCESS_STDOUT")
case "$FIRST_LINE" in
    vless://*)
        pass "CLI mode returns a bridge string that starts with vless://"
        ;;
    *)
        fail "CLI mode output did not start with vless://"
        ;;
esac

MISSING_STDOUT="$TMP_DIR/missing.stdout"
MISSING_STDERR="$TMP_DIR/missing.stderr"

env -i \
    V2RAY_UUID='11111111-2222-4333-8444-555555555555' \
    V2RAY_SERVER_IP='203.0.113.10' \
    V2RAY_SNI_DOMAIN='edge.example.org' \
    V2RAY_GENERATOR_PATH="$TMP_DIR/does-not-exist.py" \
    "$PYTHON_BIN" "$MAIN_PATH" --cli >"$MISSING_STDOUT" 2>"$MISSING_STDERR"
STATUS2=$?

[ "$STATUS2" -eq 1 ] || fail "Missing generator case expected exit 1 got $STATUS2"
grep -Fx '[ERROR] Unable to generate bridge at this time' "$MISSING_STDERR" >/dev/null 2>&1 \
    || fail "Missing generator case did not return the required clean error"
grep -F 'Traceback' "$MISSING_STDERR" >/dev/null 2>&1 \
    && fail "Missing generator case leaked a traceback"
pass "Missing generator error is handled cleanly without traceback"

printf '[PASS] bridge-me-bot test suite completed successfully\n'
