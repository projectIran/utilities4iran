# Guidelines

This directory contains contributor-facing guidelines for module quality, safety, and consistency.

## Minimum Module Standard

Each module should include:

- `src/` with focused implementation
- `tests/` with meaningful assertions
- `README.md` with at least one usage example
- `SECURITY.md` describing risks and assumptions

## Documentation Rules

- Keep examples executable and realistic.
- Document expected inputs and failure behavior.
- Note any side effects and external dependencies.

## Security Rules

- Treat all input as untrusted.
- Never hardcode secrets.
- Avoid dynamic execution patterns with untrusted content.
- Include invalid-input tests for exposed functions.
