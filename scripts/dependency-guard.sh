#!/usr/bin/env bash

set -euo pipefail

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "[dependency-guard] ERROR: not inside a Git repository." >&2
  exit 2
fi

violations=()

while IFS= read -r -d '' path; do
  case "$path" in
    node_modules/*|*/node_modules/*|venv/*|*/venv/*|.venv/*|*/.venv/*|env/*|*/env/*|ENV/*|*/ENV/*|__pycache__/*|*/__pycache__/*|site-packages/*|*/site-packages/*)
      violations+=("$path [vendored dependency/environment]")
      ;;
    dist/*|*/dist/*|build/*|*/build/*|coverage/*|*/coverage/*|htmlcov/*|*/htmlcov/*|*.egg-info|*.egg-info/*|*/.eggs/*|pip-wheel-metadata/*|*/pip-wheel-metadata/*)
      violations+=("$path [build artifact]")
      ;;
    .env|.env.*|*/.env|*/.env.*)
      violations+=("$path [environment file]")
      ;;
    *.pem|*.key|*.p12|*.pfx|*.jks|*.crt|*.cer|*.der|id_rsa|*/id_rsa|id_dsa|*/id_dsa)
      violations+=("$path [sensitive key/certificate]")
      ;;
  esac
done < <(git ls-files -z)

if ((${#violations[@]} > 0)); then
  echo ""
  echo "[dependency-guard] SEVERE: blocked files are tracked in the Git index."
  echo "[dependency-guard] This repository is in violation of dependency/security policy."
  echo ""

  printf '%s\n' "${violations[@]}" | LC_ALL=C sort -u | sed 's/^/ - /'

  echo ""
  echo "[dependency-guard] Remove these from the index before merge:"
  echo "  git rm -r --cached <path>"
  echo ""
  exit 1
fi

echo "[dependency-guard] PASS: no blocked dependency/build/env/secrets files are tracked."
