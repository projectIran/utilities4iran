# Security Policy

## Threat Model

This module handles user-provided message content and metadata before alerts are distributed through downstream systems.

## Risks and Mitigations

- Injection through alert text:
  sanitize and escape content in downstream channels before rendering.
- Duplicate message storms:
  use `deduplicateAlerts` with a suitable time window.
- Untrusted metadata:
  validate metadata shape before integration with external systems.

## Reporting

Do not disclose vulnerabilities publicly. Use the repository security contact process.
