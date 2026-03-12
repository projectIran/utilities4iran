#!/bin/bash
set -e

echo "🔍 Phase 1: Security Audit"
./scripts/dependency-guard.sh

echo "🔍 Phase 2: Bot-to-Generator Handshake"
export PYTHON_BIN=$(pwd)/.venv/bin/python
BOT_OUTPUT=$($PYTHON_BIN categories/anticensorship/bridge-me-bot/src/main.py --cli 2>/dev/null)

if [[ $BOT_OUTPUT == vless://* ]]; then
    echo "✅ Handshake Success: Bridge generated."
else
    echo "❌ Handshake Failed: Output malformed."
    exit 1
fi

echo "🔍 Phase 3: Fail-Safe Stress Test"
# Temporarily move the generator to simulate a failure
mv categories/anticensorship/v2ray-generator/src/generator.py categories/anticensorship/v2ray-generator/src/generator.py.bak

FAIL_OUTPUT=$($PYTHON_BIN categories/anticensorship/bridge-me-bot/src/main.py --cli 2>&1 || true)

# Ensure we move it back even if the check fails
mv categories/anticensorship/v2ray-generator/src/generator.py.bak categories/anticensorship/v2ray-generator/src/generator.py

if [[ $FAIL_OUTPUT == *"[ERROR]"* ]]; then
    echo "✅ Fail-Safe Verified: Clean error caught."
else
    echo "❌ Fail-Safe Failed: Traceback or unexpected output leaked."
    exit 1
fi

echo "🚀 AUDIT COMPLETE: PR #6 is field-ready."
