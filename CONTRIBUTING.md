# Contributing to AUI

Thank you for your interest in contributing to AUI! Every contribution matters — whether it's fixing a typo, reporting a bug, or building an entirely new automation backend. This guide will help you get started.

## Table of Contents

- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

## How to Contribute

1. **Fork** the repository and create your branch from `main`.
2. **Write code** — add tests for any new functionality.
3. **Ensure all checks pass** — lint, type-check, and test suites must be green.
4. **Open a Pull Request** with a clear description of your changes.

If you're unsure where to start, look for issues labeled [`good first issue`](../../labels/good%20first%20issue) or [`help wanted`](../../labels/help%20wanted).

## Development Setup

### Prerequisites

- **Python 3.10+** (3.10, 3.11, or 3.12)
- **Git**

### Getting Started

```bash
# Clone your fork
git clone https://github.com/<your-username>/aui.git
cd aui

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
.venv\Scripts\activate      # Windows

# Install the project in editable mode with development dependencies
pip install -e ".[dev]"
```

### Running the Test Suite

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=aui --cov-report=term-missing

# Run a specific test file
pytest tests/test_core.py
```

### Running Lint and Type Checks

```bash
# Lint
ruff check .

# Auto-fix lint violations
ruff check . --fix

# Format
ruff format .

# Type-check
mypy src/aui
```

## Code Style

AUI enforces consistent code quality through automated tooling. All contributions must pass these checks before merge.

### Ruff (Linting & Formatting)

We use [Ruff](https://docs.astral.sh/ruff/) for both linting and formatting with a line length of **120 characters**.

Key configuration (from `pyproject.toml`):

```toml
[tool.ruff]
line-length = 120
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "A", "SIM", "TCH"]
```

### mypy (Type Checking)

All code must pass [mypy](https://mypy.readthedocs.io/) in **strict mode**. Type annotations are required for all public functions, methods, and module-level variables.

```toml
[tool.mypy]
strict = true
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
```

### General Guidelines

- Write docstrings for all public modules, classes, and functions (Google style).
- Keep functions focused — if a function exceeds ~50 lines, consider refactoring.
- Prefer explicit over implicit. Avoid `Any` types unless absolutely necessary.
- Use `pathlib.Path` instead of string-based path manipulation.

## Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification. Each commit message should be structured as:

```
<type>(<scope>): <short summary>

<optional body>

<optional footer>
```

### Types

| Type       | Description                                        |
|------------|----------------------------------------------------|
| `feat`     | A new feature                                      |
| `fix`      | A bug fix                                          |
| `docs`     | Documentation-only changes                         |
| `style`    | Formatting, missing semicolons, etc. (no logic)    |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `perf`     | Performance improvement                            |
| `test`     | Adding or updating tests                           |
| `ci`       | Changes to CI configuration or scripts             |
| `chore`    | Maintenance tasks (dependency bumps, tooling)      |

### Examples

```
feat(core): add cross-process element caching

fix(win32): resolve handle leak on COM re-initialization

docs(readme): add Windows accessibility prerequisites
```

## Pull Request Process

1. **Update documentation** — if your change affects public APIs or behavior, update the relevant docs.
2. **Add or update tests** — all new functionality must include tests. Bug fixes should include a regression test.
3. **Ensure CI is green** — the full lint → type-check → test pipeline must pass on all supported Python versions.
4. **Write a clear PR description** — explain *what* changed, *why* it changed, and any trade-offs you made. Use the Pull Request template.
5. **Keep PRs focused** — avoid mixing unrelated changes. One logical change per PR.
6. **Respond to review feedback** — maintainers may request changes. Please address all comments before re-requesting review.

### Review Timeline

Maintainers aim to provide initial review within **5 business days**. Complex PRs may take longer. If you haven't heard back, feel free to leave a polite comment on the PR.

## Reporting Bugs

Found a bug? Please [open an issue](../../issues/new?template=bug_report.md) using the **Bug Report** template. A great bug report includes:

- **A clear, descriptive title** — e.g., "ElementNotFound raised when automating hidden Win32 combo box"
- **Steps to reproduce** — minimal, complete, and verifiable.
- **Expected vs. actual behavior** — what you expected and what happened instead.
- **Environment details** — OS, Python version, AUI version, and relevant system configuration.
- **Screenshots or logs** — if applicable, include screenshots, tracebacks, or debug logs.

Please search existing issues before filing a new one to avoid duplicates.

## Suggesting Features

Have an idea? We'd love to hear it. [Open an issue](../../issues/new?template=feature_request.md) using the **Feature Request** template and include:

- **Problem statement** — what limitation or pain point does this address?
- **Proposed solution** — how do you envision it working?
- **Alternatives considered** — what other approaches did you think about?
- **Use case** — a concrete scenario where this feature would be valuable.

Feature requests are discussed openly. Maintainers will label accepted proposals and guide implementation if you'd like to build it yourself.

---

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior through [GitHub Issues](../../issues).

---

Thank you for contributing to AUI. Your work helps make UI automation better for everyone.
