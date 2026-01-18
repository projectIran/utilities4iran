# utilities
contribute via pulling your utilities that hep others to push the movement


# Project Iran - Utilities

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)
[![Security](https://img.shields.io/badge/security-critical-red.svg)](SECURITY.md)

Welcome to the **utilities** repository of Project Iran. This repository contains standalone utility modules that support the broader Project Iran ecosystem.

## 📋 Table of Contents

- [About](#about)
- [Repository Structure](#repository-structure)
- [Getting Started](#getting-started)
- [Contributing](#contributing)
- [Security Policy](#security-policy)
- [Best Practices](#best-practices)
- [Pull Request Process](#pull-request-process)
- [Code of Conduct](#code-of-conduct)
- [License](#license)

## 🎯 About

This utilities repository is part of Project Iran, an open-source initiative. Each sub-repository within utilities is designed to be **standalone** and independently functional, allowing developers to use individual modules without dependencies on other parts of the project.

---

> 🚨 <span style="color:red;">**DISCLAIMER**</span>
> 
> <span style="color:red;">**Be careful, Your Security and Users' Security is most important**</span>
> 
> <span style="color:red;">Security is a critical concern in this project. Always review code carefully, keep dependencies updated, follow security best practices, and report vulnerabilities responsibly.</span>

---

## 📁 Repository Structure

```
utilities/
├── module-1/          # Standalone utility module
│   ├── src/
│   ├── tests/
│   ├── README.md
│   └── package.json
├── module-2/          # Standalone utility module
│   ├── src/
│   ├── tests/
│   ├── README.md
│   └── package.json
└── ...
```

Each sub-repository contains:
- **Source code** (`src/`)
- **Tests** (`tests/`)
- **Documentation** (`README.md`)
- **Dependencies** (package manager configuration)

## 🚀 Getting Started

### Prerequisites

- Node.js (v16 or higher) / Python (3.8+) / [Specify your requirements]
- Git
- Package manager (npm, yarn, pip, etc.)

### Installation

Clone the repository:

```bash
git clone https://github.com/[organization]/project-iran-utilities.git
cd project-iran-utilities
```

Navigate to the specific utility module you want to use:

```bash
cd module-name
npm install  # or pip install -r requirements.txt
```

### Usage

Each module is standalone. Refer to the individual module's README for specific usage instructions.

## 🤝 Contributing

We welcome contributions from the community! Please read our contributing guidelines carefully before submitting any pull requests.

### Quick Start for Contributors

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Write or update tests
5. Ensure all tests pass
6. Run security checks
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to your branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## 🔒 Security Policy

### Critical Security Requirements

**⚠️ ZERO TOLERANCE POLICY**

Any contribution found to contain the following will result in **permanent ban** from the project:

- **Backdoors** - Any intentional security vulnerability or hidden access mechanism
- **Critical security issues** - Including but not limited to:
  - Remote code execution vulnerabilities
  - SQL injection vulnerabilities
  - Authentication bypasses
  - Privilege escalation exploits
  - Data exfiltration mechanisms
  - Malicious code or logic bombs
  - Intentional dependency vulnerabilities

### Reporting Security Vulnerabilities

If you discover a security vulnerability, please follow responsible disclosure:

1. **DO NOT** open a public issue
2. Email security@[organization].com with details
3. Allow up to 90 days for patching before public disclosure
4. We will credit you in our security advisories (unless you prefer anonymity)

## ✅ Best Practices

All contributors must adhere to the following best practices:

### Code Quality

- **Write clean, readable code** following the project's style guide
- **Document your code** with clear comments and docstrings
- **Follow naming conventions** consistent with the existing codebase
- **Keep functions small and focused** (single responsibility principle)
- **Avoid code duplication** (DRY principle)

### Testing

- **Write comprehensive tests** for all new features
- **Maintain minimum 80% code coverage**
- **Include unit tests, integration tests, and edge cases**
- **All tests must pass** before submitting a PR
- **Test both success and failure scenarios**

### Security

- **Never commit secrets, API keys, or credentials**
- **Use environment variables** for configuration
- **Validate and sanitize all inputs**
- **Keep dependencies up-to-date**
- **Run security scanners** before submitting (npm audit, safety, etc.)
- **Follow OWASP security guidelines**

### Documentation

- **Update README files** when adding features
- **Document API changes** with examples
- **Include inline comments** for complex logic
- **Provide usage examples** in documentation
- **Keep documentation in sync with code**

### Version Control

- **Write meaningful commit messages** (use conventional commits)
- **Keep commits atomic** (one logical change per commit)
- **Rebase and squash** commits when appropriate
- **Don't commit commented-out code**
- **Don't commit build artifacts or dependencies**

### Dependencies

- **Minimize external dependencies**
- **Use only well-maintained, reputable packages**
- **Pin dependency versions** in production
- **Document why each dependency is needed**
- **Regularly audit and update dependencies**

### Performance

- **Optimize for performance** without sacrificing readability
- **Avoid premature optimization**
- **Profile code** for performance bottlenecks
- **Consider memory usage** and scalability

## 🔄 Pull Request Process

### Before Submitting

1. **Fork the repository** and create your branch from `main`
2. **Follow the coding standards** outlined in CONTRIBUTING.md
3. **Write or update tests** for your changes
4. **Run the full test suite** and ensure all tests pass
5. **Run security checks** (linters, SAST tools, dependency audits)
6. **Update documentation** as needed
7. **Ensure your code is properly formatted**

### PR Requirements

Your pull request must include:

- **Clear description** of what changes were made and why
- **Issue reference** if applicable (e.g., "Fixes #123")
- **Test results** demonstrating your changes work
- **Documentation updates** if you changed functionality
- **Changelog entry** if applicable

### Review Process

1. **Submit your PR** with a comprehensive description
2. **Organization admins will review** your submission
3. **Address feedback** promptly and professionally
4. **Make requested changes** and update your PR
5. **Approval required** from at least one admin before merge
6. **CI/CD checks must pass** (tests, linting, security scans)

### What Reviewers Look For

- Code quality and adherence to best practices
- Comprehensive test coverage
- Security considerations
- Documentation completeness
- Performance implications
- Backward compatibility

## 📜 Code of Conduct

### Our Standards

- **Be respectful** and inclusive
- **Be collaborative** and helpful
- **Be professional** in all interactions
- **Focus on what's best** for the community
- **Show empathy** towards other contributors

### Unacceptable Behavior

- Harassment or discriminatory language
- Trolling or inflammatory comments
- Personal attacks
- Publishing others' private information
- Any form of malicious conduct

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Thank you to all contributors who help make Project Iran better!


---

**Note**: By contributing to this project, you agree to abide by its terms and our security policy. We take security seriously and maintain a zero-tolerance policy for malicious contributions.
