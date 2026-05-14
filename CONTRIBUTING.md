# Contributing to Toponymia Europaea

Thank you for your interest in contributing. This project is **open to everyone** — professional researchers, students, amateur historians, linguists, developers, and enthusiasts. Your background does not matter; the quality of your contribution does.

**The single non-negotiable rule:** Every contribution must be scientific, verifiable, testable, and provable. Claims without evidence are not accepted. Code without tests is not accepted. Data without references is not accepted.

---

## Branch Strategy

### Protected Main Branch

The `main` branch is **permanently protected**. No one — including maintainers — pushes directly to `main`.

| Rule | Setting |
|------|---------|
| Direct push to `main` | **Blocked** |
| Force push to `main` | **Blocked** |
| Deletion of `main` | **Blocked** |
| Required approvals before merge | **≥ 1 maintainer** |
| Required status checks | **All CI must pass** |
| Required review dismissal on new commits | **Yes** |
| Signed commits | **Required** |

### Branch Naming Convention

```
feature/   — New functionality (e.g., feature/add-basque-module)
data/      — New data, names, or sources (e.g., data/geonames-iceland-update)
fix/       — Bug fixes (e.g., fix/normalization-unicode-edge-case)
research/  — Research analyses and hypotheses (e.g., research/norse-hov-distribution)
docs/      — Documentation only (e.g., docs/improve-onboarding-guide)
refactor/  — Code restructuring without behaviour change
```

### Workflow

```
1. Fork the repository (external) or create a branch (maintainers)
2. Work on your branch — commit often, with signed commits
3. Open a Pull Request (PR) against main
4. Automated CI runs: lint, tests, validation
5. Peer review by ≥1 maintainer
6. Address review feedback
7. Maintainer approves and merges (squash or merge commit)
```

---

## Pull Request Requirements

Every PR must satisfy **all** of the following before it can be merged. There are no exceptions.

### Universal Requirements (All PRs)

| # | Requirement | Verification |
|---|-------------|--------------|
| 1 | All existing tests pass | CI: `pytest` green |
| 2 | No linting errors | CI: `ruff check` green |
| 3 | Signed commits only | CI: GPG/SSH signature check |
| 4 | PR description explains *what* and *why* | Human review |
| 5 | No unrelated changes bundled | Human review |
| 6 | License-compatible (CC BY-NC-SA 4.0) | Human review |

### Additional Requirements by Contribution Type

#### Data Contributions (new names, attestations, sources)

These follow the **Data Quality & Onboarding Process** strictly:

| # | Requirement | Evidence |
|---|-------------|----------|
| 7 | Every name has ≥1 verifiable primary reference | `source_id` NOT NULL, citation included |
| 8 | References are real and accessible | Reviewer spot-checks citations |
| 9 | Source reliability scored per hierarchy | Score justified in PR description |
| 10 | Language codes are correct (ISO 639-3) | Automated check |
| 11 | Geographic coordinates are plausible | Automated bounds check |
| 12 | Temporal dating is sourced | Year range has citation |
| 13 | No duplicate of existing record | Automated dedup check |
| 14 | Data enters as `candidate` status | Never directly as `published` |

#### Research Contributions (interpretations, hypotheses, analyses)

| # | Requirement | Evidence |
|---|-------------|----------|
| 7 | Specific, testable claim stated | Written in PR and in `claim` field |
| 8 | Method documented and reproducible | Method description + config |
| 9 | All consulted sources cited | Full bibliography in PR |
| 10 | Confidence honestly assessed | Probability score with justification |
| 11 | Alternative explanations acknowledged | Documented in PR |
| 12 | Statistical tests pass synthetic validation | Power ≥ 0.8, FPR ≤ 0.10 |
| 13 | Preregistered if hypothesis-testing | Filed in `analysis/preregistered/` BEFORE running test |
| 14 | Reproducibility confirmed | Another reviewer can re-run and get same result |

#### Code Contributions (modules, connectors, tests, pipelines)

| # | Requirement | Evidence |
|---|-------------|----------|
| 7 | New tests cover the new code | Coverage on changed files |
| 8 | Tests are meaningful (not just `assert True`) | Human review |
| 9 | Public interfaces have type hints | `mypy` or manual check |
| 10 | Follows existing architecture patterns | Subclasses correct base class |
| 11 | No security vulnerabilities introduced | Automated + human review |
| 12 | Dependencies justified and license-compatible | Documented if new dep added |

#### Documentation Contributions

| # | Requirement | Evidence |
|---|-------------|----------|
| 7 | Factual claims have citations | References included |
| 8 | No unsourced etymological claims | Every etymology traced to source |
| 9 | Consistent with existing docs | No contradictions introduced |

---

## Review Process

### Who Can Review

- **Maintainers** have merge authority
- **Domain experts** (invited or self-identified) can provide advisory reviews
- Anyone can comment on any PR — scientific discourse is encouraged

### Review Checklist (for reviewers)

```markdown
## Review Checklist

- [ ] PR description is clear and complete
- [ ] All CI checks pass
- [ ] I have read the changed/added code in full
- [ ] References are real (I spot-checked ≥1 citation)
- [ ] Claims are verifiable — I could reproduce or falsify them
- [ ] No logical errors in methodology
- [ ] No security concerns
- [ ] Consistent with project standards
- [ ] I approve this for merge
```

### Review Standards

Reviewers must evaluate contributions against these criteria:

1. **Is it true?** — Does the evidence support the claim? Are the references real and correctly cited?
2. **Is it testable?** — Could this be falsified? Is there a conceivable observation that would disprove it?
3. **Is it reproducible?** — Could another researcher, given the same inputs, reach the same conclusion?
4. **Is it honest?** — Are uncertainties acknowledged? Is confidence appropriate, not inflated?
5. **Is it attributed?** — Are all sources credited? Is prior work acknowledged?

### Rejection Reasons

PRs will be rejected (with explanation) for any of:

- Claims without supporting references
- Fabricated or inaccessible citations
- Untestable assertions presented as findings
- Missing tests for new code
- Data that cannot be independently verified
- Inflated confidence scores without justification
- Methodological errors that compromise results
- Violations of the statistical framework (no synthetic validation)
- License incompatibility

Rejection is **not personal**. Contributors are always welcome to revise and resubmit.

---

## Contribution Types in Detail

### 1. Add a Language Module

If you have expertise in a language with toponymic tradition:

1. Create `src/toponymia/languages/your_language.py`
2. Subclass `BaseLanguageModule`
3. Implement `segment()`, `classify()`, and `etymologize()`
4. Add known toponymic elements with scholarly references for each
5. Write tests in `tests/test_languages/test_your_language.py`
6. Document your sources in the module docstring

**Reference**: `src/toponymia/languages/old_norse.py` is the reference implementation.

**Key rule**: Every suffix, prefix, and etymological claim in your module must cite a published source. No "I know this because I speak the language" — that's a starting point, not evidence.

### 2. Add a Data Source Connector

To connect a new place name data source:

1. Create `src/toponymia/connectors/your_source.py`
2. Subclass `BaseConnector`
3. Implement `fetch()` and `validate()`
4. Document the source's license, coverage, reliability tier, and format
5. Write tests in `tests/test_connectors/test_your_source.py`
6. Ensure ingested records enter at `candidate` status

### 3. Add a Statistical Test

To add a new statistical test:

1. Create a module in `src/toponymia/statistics/`
2. Subclass `BaseTest`
3. Implement `run()` and `validate_synthetic()`
4. **Mandatory**: Test must pass synthetic validation (power ≥ 0.8, FPR ≤ 0.10)
5. Write tests in `tests/test_statistics/`
6. Document the null hypothesis, assumptions, and limitations

### 4. Submit Name Data

Anyone can submit place name data:

1. Prepare records with full source citations
2. Include: name form, language, coordinates, temporal range, source
3. Every single name must have a verifiable reference
4. Open a PR with data in the prescribed format
5. Records will enter at `candidate` stage and progress through the onboarding pipeline

### 5. Propose Research

To contribute an analytical finding or interpretation:

1. **Preregister** your hypothesis (if testing a specific claim)
2. Document your method completely
3. Run analysis using the framework's statistical tools
4. Report all results — including null results
5. Open a PR with interpretation records and full supporting evidence

### 6. Report Issues

No formal requirements — just be specific:
- Data quality problems (with evidence of the error)
- Statistical methodology concerns (with explanation)
- Software bugs (with reproduction steps)
- Feature requests (with use case)

---

## Development Setup

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/ToponymiaEuropaea.git
cd ToponymiaEuropaea

# Install dependencies
uv sync --extra dev

# Install pre-commit hooks (enforces standards before commit)
pre-commit install

# Run tests to verify setup
uv run pytest tests/

# Run linter
uv run ruff check src/ tests/
```

## Code Standards

- **Python**: PEP 8, enforced by Ruff
- **Type hints**: Required for all public functions
- **Tests**: Required for all new code (pytest)
- **Documentation**: Docstrings for all public interfaces
- **Commits**: Signed (GPG or SSH), descriptive messages

## Commit Message Format

```
<type>(<scope>): <short description>

<body — what and why, not how>

Refs: <issue numbers, source citations if relevant>
Signed-off-by: Your Name <email>
```

Types: `feat`, `fix`, `data`, `research`, `docs`, `test`, `refactor`, `ci`

---

## Scientific Integrity Pledge

By submitting a contribution, you affirm that:

1. All references cited are real, accessible, and correctly represented
2. All data is authentic and not fabricated
3. All methods are honestly described
4. All results are truthfully reported (including negative results)
5. All prior work is properly attributed
6. You have the right to contribute this work under CC BY-NC-SA 4.0

Violation of this pledge results in retraction of the contribution and potential exclusion from future contributions.

## Code of Conduct

- Be respectful of cultural sensitivities around place names
- Acknowledge indigenous and minority language rights
- Present politically sensitive topics (renaming, assimilation) with appropriate context
- Welcome contributions from all backgrounds and expertise levels

## Contact

Open an issue on GitHub for questions, or email the maintainer for sensitive topics.
