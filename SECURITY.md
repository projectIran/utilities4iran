# Security Policy

## Scope

This repository contains reusable utilities that may process sensitive or high-risk information. Security issues are treated as critical.

## Reporting a Vulnerability

Do not open a public issue for security vulnerabilities.

Use private disclosure through one of these channels:

- GitHub private vulnerability reporting (preferred)
- Maintainer security contact process for Project Iran

When reporting, include:

- Affected file/module and branch/commit
- Clear reproduction steps
- Impact assessment and possible exploitability
- Suggested mitigation if available

## Response Expectations

- Initial triage acknowledgment target: 72 hours
- Status updates provided during investigation
- Fix timeline depends on severity and exploitability

## Contributor Requirements

- Never commit credentials, tokens, or private keys
- Validate and sanitize untrusted input
- Avoid dangerous dynamic execution patterns (`eval`, `Function`, shell exec with untrusted input)
- Keep dependencies current and review advisories

## Safe Contribution Baseline

For new modules and major feature changes, include:

- A module `SECURITY.md` with threat notes
- Tests for failure paths and invalid input
- Documentation of security assumptions and limitations
