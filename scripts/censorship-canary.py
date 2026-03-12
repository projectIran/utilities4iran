#!/usr/bin/env python3
"""
Censorship Canary: Monitors network accessibility and generates status alerts.

This script checks various indicators of network disruption or censorship and
writes real-time status to docs/status.json for the Tactical Utility Registry UI.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime


def check_dns():
    """Check if DNS resolution is working."""
    try:
        result = subprocess.run(
            ['nslookup', 'google.com'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


def check_http_connectivity():
    """Check HTTP connectivity to a test endpoint."""
    try:
        result = subprocess.run(
            ['curl', '-s', '-m', '5', 'http://example.com'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False


def check_https_connectivity():
    """Check HTTPS connectivity to a test endpoint."""
    try:
        result = subprocess.run(
            ['curl', '-s', '-m', '5', 'https://example.com'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False


def detect_censorship():
    """Perform censorship detection checks."""
    dns_ok = check_dns()
    http_ok = check_http_connectivity()
    https_ok = check_https_connectivity()

    # Determine alert status based on connectivity
    # Alert if any critical service is down
    alert = not (dns_ok and http_ok and https_ok)

    return {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'dns_online': dns_ok,
        'http_online': http_ok,
        'https_online': https_ok,
        'alert': alert,
        'reason': 'Network disruption detected' if alert else 'All systems operational'
    }


def write_status(status_data):
    """Write status to docs/status.json."""
    repo_root = Path(__file__).parent.parent
    status_file = repo_root / 'docs' / 'status.json'

    # Ensure docs directory exists
    status_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(status_file, 'w') as f:
            json.dump(status_data, f, indent=2)
        print(f'[INFO] Status written to {status_file}')
        return True
    except Exception as e:
        print(f'[ERROR] Failed to write status file: {e}', file=sys.stderr)
        return False


def main():
    """Main entry point."""
    try:
        status = detect_censorship()
        success = write_status(status)

        if success:
            print(f'[ALERT] {status["reason"]}')
            if status['alert']:
                print('[CRITICAL] Emergency bridges are recommended.')
                return 1
            return 0
        return 1

    except Exception as e:
        print(f'[ERROR] Canary check failed: {e}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
