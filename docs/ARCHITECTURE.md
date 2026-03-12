# Architecture

## Overview

`utilities4iran` is organized as a category-based monorepo. Every utility lives under `categories/<domain>/<name>` and is treated as a self-contained module with its own source, tests, README, and security notes. This structure is intentional: it reduces naming conflicts, constrains operational risk, and keeps security review localized to the module that changed.

The engineering baseline for every module is defined by the repository threat model: [../THREAT_MODEL.md](../THREAT_MODEL.md).

## Category-Based Modularization

All utilities are placed under a domain directory first and a module directory second:

```text
categories/
  communication/
    alert-systems/
  socialmedia/
    x-automation/
  anticensorship/
    v2ray-generator/
```

This design solves two architectural problems.

First, it prevents directory collisions. A flat module root eventually produces ambiguous names such as `generator`, `validator`, or `proxy`, especially in a repository where different operational domains evolve in parallel. Requiring `categories/<domain>/<name>` gives each module a stable namespace and makes ownership and intent obvious from the path alone.

Second, it limits the blast radius of security defects. A module-specific issue should remain isolated to one subtree instead of contaminating unrelated tooling. Reviewers can inspect a single directory and its local documentation without having to infer whether a change silently affected another domain. This also improves CI targeting, documentation generation, and incident triage because category boundaries map directly to repository boundaries.

The practical rule is simple: new work does not go into shared ad hoc folders. It is introduced as a discrete module under the appropriate category.

## Dependency Guard Protocol

The repository enforces a tracked-file policy through [../scripts/dependency-guard.sh](../scripts/dependency-guard.sh). The script audits the active Git index using `git ls-files` and fails if blocked material has been committed or staged into version control.

The policy specifically rejects:

- Vendored dependencies such as `node_modules/`, virtual environments, `__pycache__/`, and similar environment directories.
- Build artifacts such as `dist/`, `build/`, `coverage/`, wheel metadata, and compiled package outputs.
- Environment files and sensitive material such as `.env*`, key files, certificate files, and private credential artifacts.

This protocol exists to stop supply chain bloat before it lands in the repository. Tracking vendored dependencies or compiled binaries inflates review surface area, obscures provenance, and makes malicious payload insertion easier to hide. Tracking environment files or key material creates a direct secret-exposure path.

Enforcement is not advisory. GitHub Actions runs [../.github/workflows/dependency-guard.yml](../.github/workflows/dependency-guard.yml) on every pull request and every push to `main`, makes the guard script executable, and executes it as a required CI step. If the script exits with code `1`, the workflow fails and the change must not be merged.

## Scaffolding Law

All new modules must be created via the native project CLI: [../tools/create-utility4iran/bin/cli.js](../tools/create-utility4iran/bin/cli.js).

This is a repository law, not a convenience suggestion. The scaffold guarantees that each module starts with the same minimum control surface:

- `README.md` for usage and operator-facing documentation
- `SECURITY.md` for module-specific risks and reporting expectations
- `src/` for implementation
- `tests/` for verification artifacts

Standardized scaffolding reduces structural drift across domains. That matters for security because inconsistent module layouts create review blind spots, missing documentation, and incomplete tests. By forcing creation through the CLI, the repository ensures that even a new module begins with the same baseline contract as every other module.

The scaffold also preserves predictable paths for automation. Catalog generation, targeted review, module discovery, and contributor workflows all depend on the repository being able to assume a consistent directory layout.

## Threat Model Authority

Runtime behavior is governed by [../THREAT_MODEL.md](../THREAT_MODEL.md). That document is the authoritative engineering standard for how code in this repository must behave under hostile conditions.

Its mandates drive the architecture described above:

- Category isolation helps contain defects and simplify review in a hostile environment.
- Dependency guard enforcement supports the no-secrets and low-trust supply chain posture.
- Mandatory scaffolding ensures that documentation and tests exist before runtime code expands.

When architecture, implementation convenience, and operational safety conflict, the threat model wins.