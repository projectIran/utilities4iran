# Contributing Quickstart

This repository is built to let you ship a new tool fast without inventing structure from scratch. The architecture is not paperwork. It is a power tool: it gives every module a known location, a known security surface, and a known test entrypoint so you can spend your time on the logic that matters.

For the deeper rules, see [ARCHITECTURE.md](./ARCHITECTURE.md) and [../THREAT_MODEL.md](../THREAT_MODEL.md).

## 3-Minute Tool Deployment

Use this path when you need to get a new module live quickly.

1. Run the scaffold CLI.

```bash
node tools/create-utility4iran/bin/cli.js
```

You can also use positional arguments when you already know the category, name, description, and language.

```bash
node tools/create-utility4iran/bin/cli.js anticensorship doh-forwarder "Encrypted DNS-over-HTTPS forwarder" Python
```

2. Paste or implement your logic inside `src/`.

The scaffold gives you the standard module envelope immediately:

- `README.md`
- `SECURITY.md`
- `src/`
- `tests/`

3. Execute the local security test in `tests/`.

Examples:

```bash
./categories/anticensorship/doh-forwarder/tests/test-doh.sh
./categories/socialmedia/x-automation/tests/test-bot-security.sh
```

That is the shortest correct path from idea to reviewable tool: scaffold, implement, verify.

## Guard Duty

The repository assumes that vendored dependencies, compiled outputs, and leaked secrets are not harmless clutter. They are supply-chain risk.

The first line of defense is [.gitignore](../.gitignore). The second line of defense is [../scripts/dependency-guard.sh](../scripts/dependency-guard.sh), which scans the tracked Git index and fails hard if blocked material is present. GitHub Actions enforces that same check in CI.

If you try to add `node_modules/`, you will hit the guardrail.

Example:

```bash
git add -f node_modules/example/index.js
scripts/dependency-guard.sh
```

Expected result:

```text
[dependency-guard] SEVERE: blocked files are tracked in the Git index.
[dependency-guard] This repository is in violation of dependency/security policy.
 - node_modules/example/index.js [vendored dependency/environment]
```

The outcome is intentional:

- Local guard runs tell you immediately that the index is dirty.
- The GitHub Action blocks the pull request if the violation is pushed.
- Review time stays focused on source code, not on auditing dependency blobs or leaked credentials.

## Why This Feels Fast

The category-based layout is a speed multiplier.

- You do not waste time deciding where a tool belongs. It lives in `categories/<domain>/<name>`.
- You do not waste time inventing boilerplate. The CLI creates the baseline files for you.
- You do not waste review cycles debating whether a module has docs, tests, or security notes. The structure already requires them.
- You do not lose time chasing accidental bloat in pull requests. The dependency guard removes that class of mistake early.

In practice, this means the architecture clears a lane for shipping. It narrows choices on purpose so delivery gets faster, reviews get sharper, and mistakes get caught before they become operational problems.

## Working Rule

When in doubt, use the scaffold, keep the logic inside the module boundary, run the test in `tests/`, and let the guardrails do their job.