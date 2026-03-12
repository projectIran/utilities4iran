# utilities4iran

Reusable utility modules for the Project Iran ecosystem, organized by category.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Security](https://img.shields.io/badge/security-critical-red.svg)](SECURITY.md)

## About

`utilities4iran` is a multi-module repository where each module is intended to be standalone, testable, and security-reviewed.

Security is the first priority. Treat all input as untrusted, avoid secrets in code, and follow the reporting flow in `SECURITY.md`.

## Repository Structure

```text
categories/
  communication/
    alert-systems/
    encrypted-messaging/
  monitoring/
    data-analytics/
    surveillance-detection/
  socialmedia/
    instagram-automation/
    multi-platform-sync/
    x-automation/

docs/
  index.html
  GUIDELINES/
  TEMPLATES/

tools/
  create-utility4iran/
```

Each module should include:

- `src/` source code
- `tests/` automated tests
- `README.md` usage and examples
- `SECURITY.md` module-specific risks

## Current Implemented Modules

- `categories/communication/alert-systems`
- `categories/socialmedia/x-automation`

## Getting Started

### Clone

```bash
git clone https://github.com/projectIran/utilities4iran.git
cd utilities4iran
```

### Run Example Module Tests

```bash
node --test categories/communication/alert-systems/tests/alertSystem.test.js
node --test categories/socialmedia/x-automation/tests/postPlanner.test.js
```

## Scaffolding CLI

Create a new module under `categories/`:

```bash
node tools/create-utility4iran/bin/cli.js
```

The CLI now supports selecting an existing category or creating a new one.

## Automation

- Auto-catalog workflow updates `docs/index.html` from modules in `categories/**`.
- AI PR gatekeeper runs on pull requests that touch `categories/**`.

If `GEMINI_API_KEY` is configured in repository secrets, the gatekeeper can post AI-assisted security feedback on PRs.

## Contributing

Start with `CONTRIBUTING.md`. Minimum PR expectations:

- Add or update tests
- Include security notes for new module behavior
- Keep code readable and non-obfuscated
- Update documentation for behavior changes

## License

MIT. See `LICENSE`.
