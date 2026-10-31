# Security Policy

## Supported versions

Only the latest `main` is supported.

## Reporting a vulnerability

Please report vulnerabilities privately: use
[GitHub security advisories](https://github.com/Prekzursil/tss/security/advisories/new)
("Report a vulnerability"). Do not open a public issue for security problems.

You should receive a response within 72 hours. Please do not disclose the
issue publicly before a fix is released.

## Scope

This repository is course deliverable code (a pure-stdlib pricing module, a
deck generator, and experiment runners). There is no production service, no
network surface, and no user data. Reports are still welcome and will be
fixed or documented.

## Automated checks

- **CodeQL** runs on every push to `main`, every PR, and weekly (`.github/workflows/codeql.yml`).
- **gitleaks / opengrep / osv-scanner** run on every push and PR via the
  [quality-zero-platform](https://github.com/Prekzursil/quality-zero-platform) lean gate.
- **Dependabot** tracks GitHub Actions and pip dependencies weekly.
