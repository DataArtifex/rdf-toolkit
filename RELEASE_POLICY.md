# Data Artifex Python Package Release Policy

## 1. Purpose

This document defines the mandatory release governance and automation standard for Data Artifex Python package repositories that publish to PyPI.

The goals are:

- Consistent quality gates before release.
- Secure and repeatable publishing.
- Clear ownership and traceability for every released version.

## 2. Scope

This policy applies to all Data Artifex repositories that:

- Build and distribute Python packages.
- Publish artifacts to PyPI.

If a repository is Python-based but does not publish to PyPI, the repository owner may adopt a reduced variant, but deviations must follow the exceptions process in Section 11.

## 3. Normative Language

The terms MUST, MUST NOT, SHALL, SHALL NOT, SHOULD, and MAY are used as defined by RFC-style policy language.

## 4. Branching And Governance Standard

### 4.1 Default Branch Model

- The default branch SHALL be main.
- main SHALL be the only long-lived branch unless a maintenance line is explicitly required.
- Feature work MUST be performed on short-lived branches and merged through pull requests.

### 4.2 Main Branch Protection

main MUST be protected with the following minimum controls:

- Pull request required before merge.
- At least one approving review required.
- Stale approvals dismissed when new commits are pushed.
- Required status checks must pass before merge.
- Branch must be up to date before merge.
- Direct pushes to main prohibited.

### 4.3 Emergency Bypass

- Admin bypass MAY be used only for urgent production-impacting events.
- Any bypass MUST be followed by a documented post-incident pull request note.
- The bypass rationale MUST be recorded in release notes or incident records.

## 5. Release Model

### 5.1 Versioning

- Releases MUST follow Semantic Versioning.
- Releases MUST be created from main.
- Release tags MUST use the format vX.Y.Z.
- Each repository MUST define a single source of truth for version (for example, src/<package>/__about__.py).

### 5.2 Release Notes And Changelog

- Every release MUST include a changelog entry.
- Changelog entries SHOULD be concise and user-relevant.
- Release notes MUST reference the exact tag and merged changes.

### 5.3 Release Branches

- A permanent release branch model is NOT required by default.
- release/* branches MAY be introduced only when concurrent maintenance is needed (for example, N and N-1 support).

## 6. CI And Quality Gates

Before a release can publish, required checks MUST pass.

Minimum required checks:

- Tests.
- Linting.
- Type checking.

Optional checks (recommended where applicable):

- Documentation build.
- Security scans.
- Packaging metadata checks in pre-release CI.

## 7. PyPI Publishing Automation Standard

### 7.1 Workflow Requirements

Repositories MUST implement a dedicated publish workflow that:

- Triggers on release tag or GitHub Release publication.
- Builds both sdist and wheel artifacts.
- Validates artifacts before publish.
- Publishes through trusted, non-interactive automation.

### 7.2 Trusted Publishing

- Publishing MUST use PyPI Trusted Publishing (OIDC).
- Long-lived PyPI API tokens SHOULD NOT be used.
- If tokens are temporarily required, they MUST be time-bounded and rotated.

### 7.3 Build Validation

- Artifact validation (for example, twine check) MUST run before publish.
- Failed validation MUST block publish.

### 7.4 TestPyPI Preflight

- New repositories SHOULD publish to TestPyPI before first production release.
- Repositories with major workflow changes SHOULD run a TestPyPI dry run.

## 8. Security And Operational Controls

- Workflows MUST use least-privilege permissions.
- Publish jobs SHOULD run in protected environments where reviewer approval is required.
- Manual local publishing to production PyPI SHOULD NOT occur.
- If break-glass manual publish is used, the action MUST be documented and reviewed post-release.

## 9. Standard Publish Workflow Template

Use this as a baseline and adapt package-specific test commands as needed.

```yaml
name: Publish Python Package

on:
  push:
    tags:
      - "v*.*.*"
  workflow_dispatch:
    inputs:
      target:
        description: "Publish target"
        required: true
        type: choice
        default: pypi
        options:
          - testpypi
          - pypi

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write

    # Optional but recommended for production controls.
    # environment: pypi

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install build tools
        run: |
          python -m pip install --upgrade pip
          pip install hatch twine

      - name: Run quality checks
        run: |
          # Replace with repository-standard commands.
          # Example:
          # uv run pytest -q tests
          # uv run ruff check src tests
          # uv run pyrefly check src tests
          echo "Run repository quality gates here"

      - name: Build artifacts
        run: hatch build

      - name: Validate artifacts
        run: twine check dist/*

      - name: Publish to TestPyPI
        if: github.event_name == 'workflow_dispatch' && inputs.target == 'testpypi'
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          repository-url: https://test.pypi.org/legacy/

      - name: Publish to PyPI
        if: github.event_name == 'push' || (github.event_name == 'workflow_dispatch' && inputs.target == 'pypi')
        uses: pypa/gh-action-pypi-publish@release/v1
```

## 10. Adoption Checklists

### 10.1 Branch Protection Checklist

- main protected.
- PR required for merge.
- Required checks configured.
- Up-to-date branch requirement enabled.
- Approval requirement enabled.
- Direct pushes blocked.

### 10.2 PyPI Trusted Publisher Checklist

- PyPI project created.
- Trusted Publisher configured in PyPI settings.
- GitHub repository owner/name matches configuration.
- Workflow filename and environment (if used) match configuration.
- First publish performed through CI, not local machine.

### 10.3 First Release Verification Checklist

- Tag created from main in vX.Y.Z format.
- CI checks passed.
- Publish workflow completed successfully.
- Package install tested in a clean environment.
- Import smoke test passed.
- Changelog and release notes published.

## 11. Exceptions Process

Any exception to this policy MUST:

- Be approved by the repository owner or designated maintainer.
- Include a written rationale.
- Include risk impact and mitigation notes.
- Define a target date to return to compliance.

## 12. Recommended Repository References

Each repository SHOULD link this policy from:

- README.
- AGENTS instructions or equivalent contributor guidance.
- Release workflow documentation.
