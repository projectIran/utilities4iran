# CONTRIBUTING PROTOCOL: Utilities4Iran

**Status:** ENFORCED
**Objective:** Maintain strict architectural integrity and operational security.

This repository operates under a Zero-Trust, highly modular architecture. We are building field-grade tools for hostile network environments. Sloppy code, vendored bloat, and unmanaged secrets are operational hazards. 

If you do not follow these mandates, your Pull Request will be rejected and closed without review.

## 1. Architectural Mandate
1. All modules must reside in `categories/<category>/<module>`. Monolithic scripts in the root directory are strictly forbidden.
2. Every module requires a `README.md`, `SECURITY.md`, and a `tests/` directory.
3. You **must** use the project scaffolding tool to create your utility's structure. Do not create folders manually:
   `node tools/create-utility4iran/bin/create-utility.js <category-name> <utility-name>`
4. Run `node .github/scripts/generate-catalog.js` to update the registry before pushing.

## 2. Dependency & Supply Chain Security
Vendored dependencies compromise our ability to audit code. 
* **NEVER** commit `node_modules`, `dist/`, `build/`, `__pycache__`, or virtual environments (`venv`). 
* The repository's automated CI/CD dependency guard (`dependency-guard.sh`) will actively scan your Git index. If it detects vendored blobs, your build will hard-fail.
* All dependencies must be resolved at runtime via standard package managers (`package.json`, `requirements.txt`).

## 3. Secret Management
* Hardcoded credentials (API keys, tokens, passwords) are an immediate disqualification.
* Standalone `.env` files must **never** be committed. They are blocked by the global `.gitignore`.
* Your code must be written to accept configuration via secure environment variables (e.g., `os.environ.get('API_KEY')`).

## 4. Pull Request Protocol
1. **Target Branch:** All PRs must target `main`.
2. **Context Required:** Your PR description must explicitly state what the tool does, which category it belongs to, and how it handles potential network failures (refer to `THREAT_MODEL.md`). "No description provided" will result in an auto-close.
3. **Automated Audits:** Your code must pass the `ai-gatekeeper` and `dependency-guard` status checks. Do not request a manual review until the CI pipeline is green.