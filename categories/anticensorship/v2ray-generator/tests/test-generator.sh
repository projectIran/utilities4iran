#!/usr/bin/env bash

set -u

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
MODULE_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
GENERATOR_PATH="$MODULE_ROOT/src/generator.py"
PYTHON_BIN=${PYTHON_BIN:-$(command -v python3 2>/dev/null || command -v python 2>/dev/null)}

MISSING_STDOUT=$(mktemp /tmp/v2ray-generator-missing.stdout.XXXXXX)
MISSING_STDERR=$(mktemp /tmp/v2ray-generator-missing.stderr.XXXXXX)
SUCCESS_STDOUT=$(mktemp /tmp/v2ray-generator-success.stdout.XXXXXX)
SUCCESS_STDERR=$(mktemp /tmp/v2ray-generator-success.stderr.XXXXXX)

cleanup() {
    rm -f "$MISSING_STDOUT" "$MISSING_STDERR" "$SUCCESS_STDOUT" "$SUCCESS_STDERR"
}

trap cleanup EXIT HUP INT TERM

fail() {
    printf '[FAIL] %s\n' "$1" >&2
    exit 1
}

pass() {
    printf '[PASS] %s\n' "$1"
}

[ -f "$GENERATOR_PATH" ] || fail "Generator not found at $GENERATOR_PATH"
[ -n "${PYTHON_BIN:-}" ] || fail "python3 or python is required"

if env -i "$PYTHON_BIN" "$GENERATOR_PATH" >"$MISSING_STDOUT" 2>"$MISSING_STDERR"; then
    fail "Generator unexpectedly succeeded without required environment variables"
else
    missing_status=$?
fi

[ "$missing_status" -eq 1 ] || fail "Generator returned $missing_status instead of 1 when env vars were missing"
grep -F 'Missing required environment variable' "$MISSING_STDERR" >/dev/null 2>&1 || fail "Generator did not print a clean missing-env error"
grep -F 'Traceback' "$MISSING_STDERR" >/dev/null 2>&1 && fail "Generator leaked a Python traceback on missing env vars"
pass "Generator fails safely when required environment variables are missing"

if ! env -i \
    V2RAY_UUID='11111111-2222-4333-8444-555555555555' \
    V2RAY_SERVER_IP='203.0.113.10' \
    V2RAY_SNI_DOMAIN='edge.example.org' \
    "$PYTHON_BIN" "$GENERATOR_PATH" >"$SUCCESS_STDOUT" 2>"$SUCCESS_STDERR"; then
    fail "Generator failed with mocked environment variables"
fi

[ ! -s "$SUCCESS_STDERR" ] || fail "Generator wrote unexpected stderr output during successful execution"

JSON_PATH="$SUCCESS_STDOUT" EXPECTED_UUID='11111111-2222-4333-8444-555555555555' EXPECTED_IP='203.0.113.10' EXPECTED_SNI='edge.example.org' "$PYTHON_BIN" - <<'PY'
import json
import os
import sys

with open(os.environ["JSON_PATH"], "r", encoding="utf-8") as handle:
    config = json.load(handle)

outbound = config["outbounds"][0]
server = outbound["settings"]["vnext"][0]
user = server["users"][0]
stream = outbound["streamSettings"]

assert outbound["protocol"] == "vless"
assert server["address"] == os.environ["EXPECTED_IP"]
assert server["port"] == 443
assert user["id"] == os.environ["EXPECTED_UUID"]
assert user["encryption"] == "none"
assert stream["network"] == "ws"
assert stream["security"] == "tls"
assert stream["tlsSettings"]["serverName"] == os.environ["EXPECTED_SNI"]
assert stream["wsSettings"]["headers"]["Host"] == os.environ["EXPECTED_SNI"]
assert stream["wsSettings"]["path"] == "/ws"
PY

pass "Generator succeeds with mocked environment variables and emits valid JSON"
printf '[PASS] V2Ray generator test suite completed successfully\n'