#!/usr/bin/env bash
# test-scrubber.sh — Verify that metadata-scrubber strips EXIF/GPS markers.
# Uses only Python stdlib + Pillow; no external network access required.

set -u

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
MODULE_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
SCRUBBER="$MODULE_ROOT/src/main.py"
PYTHON_BIN=${PYTHON_BIN:-$(command -v python3 2>/dev/null || command -v python 2>/dev/null)}
TMP_DIR=$(mktemp -d /tmp/metadata-scrubber-test.XXXXXX)

cleanup() { rm -rf "$TMP_DIR"; }
trap cleanup EXIT HUP INT TERM

fail() { printf '[FAIL] %s\n' "$1" >&2; exit 1; }
pass() { printf '[PASS] %s\n' "$1"; }

[ -f "$SCRUBBER" ]        || fail "Scrubber not found at $SCRUBBER"
[ -n "${PYTHON_BIN:-}" ]  || fail "python3 is required"

FIXTURE="$TMP_DIR/test-with-exif.jpg"

# ── Create a minimal JPEG that contains a GPS EXIF block ──────────────────────
"$PYTHON_BIN" - "$FIXTURE" <<'PY'
import sys
from PIL import Image
import piexif

img = Image.new("RGB", (16, 16), color=(100, 149, 237))

# Build a minimal EXIF payload with a GPS block and a Camera model string.
exif_dict = {
    "0th": {
        piexif.ImageIFD.Make: b"TestCamera",
        piexif.ImageIFD.Model: b"GPS-Device",
    },
    "GPS": {
        piexif.GPSIFD.GPSLatitudeRef: b"N",
        piexif.GPSIFD.GPSLatitude: ((35, 1), (41, 1), (0, 1)),
        piexif.GPSIFD.GPSLongitudeRef: b"E",
        piexif.GPSIFD.GPSLongitude: ((51, 1), (25, 1), (0, 1)),
    },
    "Exif": {},
    "1st": {},
    "thumbnail": None,
}
exif_bytes = piexif.dump(exif_dict)
img.save(sys.argv[1], format="JPEG", quality=95, exif=exif_bytes)
print(f"Fixture written: {sys.argv[1]}")
PY

[ -f "$FIXTURE" ] || fail "Could not create JPEG fixture with EXIF"

# Confirm the fixture actually carries the markers before scrubbing.
if ! strings "$FIXTURE" | grep -qiE 'GPS|Camera|TestCamera'; then
    fail "Fixture does not contain expected EXIF markers before scrubbing"
fi
pass "Fixture contains EXIF/GPS markers before scrubbing"

# ── Run the scrubber ──────────────────────────────────────────────────────────
"$PYTHON_BIN" "$SCRUBBER" "$FIXTURE" >"$TMP_DIR/stdout.log" 2>"$TMP_DIR/stderr.log"
STATUS=$?

[ "$STATUS" -eq 0 ] || fail "Scrubber exited with code $STATUS (expected 0)"
pass "Scrubber exits with code 0 on a valid JPEG"

grep -qi "Traceback" "$TMP_DIR/stderr.log" && fail "Scrubber leaked a Python Traceback"
pass "Scrubber suppresses Python Tracebacks"

# ── Binary check: EXIF markers must be absent from the scrubbed file ──────────
if strings "$FIXTURE" | grep -qiE 'TestCamera|GPS-Device|GPSLatitude'; then
    fail "Scrubbed file still contains EXIF/GPS markers"
fi
pass "Scrubbed file contains no GPS or Camera EXIF markers"

# ── Zero-trace: no temp files left in the module tree ─────────────────────────
LEFTOVER=$(find "$MODULE_ROOT" -name "*.tmp" -o -name "*.bak" 2>/dev/null | head -1)
[ -z "$LEFTOVER" ] || fail "Scrubber left behind temp file: $LEFTOVER"
pass "No temporary files left behind"

printf '[PASS] metadata-scrubber test suite completed successfully\n'
