#!/usr/bin/env python3
"""
snowflake-proxy: Manager for the Go-based snowflake-client Pluggable Transport.

Starts and supervises the snowflake-client subprocess. On SIGINT/SIGTERM the
underlying process is immediately terminated — no ghost processes, no tracebacks.
"""

import os
import shutil
import signal
import subprocess
import sys

DEFAULT_STUN = "stun:stun.l.google.com:19302"
DEFAULT_FRONT = "cdn.sstatic.net"

_child: subprocess.Popen | None = None


def _shutdown(signum, frame):  # noqa: ARG001
    if _child is not None and _child.poll() is None:
        _child.terminate()
        try:
            _child.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _child.kill()
    sys.exit(0)


def resolve_binary() -> str:
    explicit = os.environ.get("SNOWFLAKE_BIN", "").strip()
    if explicit:
        if os.path.isfile(explicit) and os.access(explicit, os.X_OK):
            return explicit
        print(
            f"[ERROR] SNOWFLAKE_BIN='{explicit}' is not an executable file.",
            file=sys.stderr,
        )
        sys.exit(1)

    found = shutil.which("snowflake-client")
    if found:
        return found

    print(
        "[ERROR] snowflake-client binary not found. "
        "Please install the Tor Snowflake client.",
        file=sys.stderr,
    )
    sys.exit(1)


def build_command(binary: str) -> list[str]:
    stun = os.environ.get("STUN_SERVER", DEFAULT_STUN).strip() or DEFAULT_STUN
    front = os.environ.get("FRONT_DOMAIN", DEFAULT_FRONT).strip() or DEFAULT_FRONT
    return [
        binary,
        "-url", "https://snowflake-broker.torproject.net/",
        "-front", front,
        "-ice", stun,
        "-log-to-state-dir",
    ]


def main() -> None:
    global _child

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    try:
        binary = resolve_binary()
        cmd = build_command(binary)

        print(f"[INFO] Starting snowflake-client: {' '.join(cmd)}", flush=True)

        _child = subprocess.Popen(
            cmd,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        exit_code = _child.wait()
        if exit_code != 0:
            print(
                f"[ERROR] snowflake-client exited with code {exit_code}.",
                file=sys.stderr,
            )
            sys.exit(exit_code)
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] Unexpected failure: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
