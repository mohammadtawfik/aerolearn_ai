# AI/Developer Documentation Awareness Protocol

## Purpose

To guarantee TDD compliance and awareness of the latest architectural, API, and workflow documentation, this protocol **must be followed for all new code, tests, or design work**.

---

## Checklist For Every TDD/Development/PR Cycle

1. **Generate or Update Documentation Index**
    - Run `/tools/doc_indexer.py` to scan `/docs` for all `.md` files.
    - Review `/docs/doc_index.md` for all current documents.

2. **Explicit Documentation Loading**
    - Before writing or modifying any code/tests:
        - Load (into editor, review in code/AI context) the following:
          - `/docs/architecture/architecture_overview.md`
          - `/docs/development/dayXX_plan.md` (for today's cycle)
          - `/docs/architecture/health_monitoring.md` (or protocol file)
          - `/docs/architecture/dependency_tracking_protocol.md`
          - Any project-/feature-specific docs named in `/docs/doc_index.md`

3. **Pre-Run Verification (Manual or Automated)**
    - Confirm and log all docs loaded/parsed, including their timestamp and paths.
    - If using CI, fail run if any required docs missing or not linked to a commit/PR.

4. **Test Awareness**
    - Ensure `/tests/conftest.py` includes the pre-load fixture: tests will fail if required docs are missing or unread.

5. **PR/Review Checklist**
    - Attach (or reference) the doc index and loaded doc list at the top of PRs and reviews.

---

## CI/Tooling Recommendations

- CI must invoke `/tools/doc_indexer.py` and test doc fixture before allowing build/test pipeline to run.
- On PR: check for references (links or "Docs loaded: ...") in PR summary/comments.

---

## Enforcement

- Any development cycle or CI run skipping this protocol is considered incomplete.
- If docs change, rerun the indexer and reload all docs.

---

## For Developers & AI Assistants

- If you start a new dev/test session or are prompted to "review the docs," follow every step above before proceeding with requirements or tests.

---

_Last revised: [today's date]_