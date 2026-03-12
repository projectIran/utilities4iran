#!/usr/bin/env bash

set -u

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
MODULE_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
MAIN_PATH="$MODULE_ROOT/src/main.py"
PYTHON_BIN=${PYTHON_BIN:-$(command -v python3 2>/dev/null || command -v python 2>/dev/null)}
TMP_DIR=$(mktemp -d /tmp/doh-forwarder-test.XXXXXX)
STDOUT_LOG="$TMP_DIR/stdout.log"
STDERR_LOG="$TMP_DIR/stderr.log"

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

[ -f "$MAIN_PATH" ] || fail "DoH forwarder not found at $MAIN_PATH"
[ -n "${PYTHON_BIN:-}" ] || fail "python3 or python is required"

cat > "$TMP_DIR/sitecustomize.py" <<'PY'
from urllib.error import URLError
import urllib.request


def _network_down(*args, **kwargs):
    raise URLError("simulated network outage")


urllib.request.urlopen = _network_down
PY

if env -i \
    PYTHONPATH="$TMP_DIR" \
    DOH_PROVIDER=cloudflare \
    "$PYTHON_BIN" "$MAIN_PATH" example.org >"$STDOUT_LOG" 2>"$STDERR_LOG"; then
    fail "DoH forwarder unexpectedly succeeded while the network was simulated as down"
else
    status=$?
fi

[ "$status" -eq 1 ] || fail "DoH forwarder returned $status instead of exit code 1"
grep -F 'Error: DNS-over-HTTPS network request failed.' "$STDERR_LOG" >/dev/null 2>&1 || fail "DoH forwarder did not emit the expected fail-safe error"
grep -F 'Traceback' "$STDERR_LOG" >/dev/null 2>&1 && fail "DoH forwarder leaked a Python traceback"
pass "DoH forwarder exits with code 1 when the network is simulated as down"