# Security Policy

## Threat Model

This module handles user-provided post text and metadata before publication scheduling.

## Risks and Mitigations

- Malicious or unsafe text content:
  validate and moderate content before posting through platform APIs.
- Timing abuse:
  validate schedule windows in higher-level orchestration services.
- Sensitive information leakage:
  avoid passing secrets/tokens in post text payloads.

## Reporting

Report vulnerabilities privately via the repository security disclosure process.
