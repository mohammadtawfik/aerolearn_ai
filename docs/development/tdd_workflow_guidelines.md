# AeroLearn AI: Test-Driven Development (TDD) Working Instructions

This document defines essential instructions and protocols for contributors, following a strict TDD workflow. It must be read and followed for every new feature, bugfix, or enhancement in this project.

---

## TDD-First Approach Required

**All new contributions MUST follow test-driven development (TDD) practices.**

## Startup Protocol for New Conversations/Development Tasks

**For all new features or workflow sessions:**

1. **Study All Reference Details**
    - Read and understand _every detail_ in `/code_summary.md`, which outlines the full project structure, dependencies, and key class/file purposes.
    - Consult the current status and requirements in `/docs/development/day19_plan.md` for immediate to-do items or missing functionality descriptions.

2. **Test-First Implementation**
    - Start by implementing comprehensive tests for every feature, bugfix, or integration described in the current plan:
        - **Unit Tests:** Cover all new logic and edge cases.
        - **Integration Tests:** Implement all required integration points.
        - **Location:** Save all tests in the correct `/tests/` subdirectory according to the current project structure as detailed in `/code_summary.md`.
        - **Explicit Test File Guidance:** When creating or updating a file, always state in both the prompt and code comment exactly where it must be saved in the repo based on the project structure.

3. **Implementation After Testing**
    - Once tests are complete, implement the code to satisfy those tests.
    - Fetch and study all existing code and related documentation from the project (as needed) to ensure updates fit into the system and do not duplicate prior work.

4. **Documentation**
    - When referencing system behavior, API specs, or integration requirements, consult the documentation files that have already been created and are present in the project tree.

5. **Project Structure Adherence**
    - When proposing a new file (test, code, or documentation), always:
        - State clearly in both the prompt and the file header where the file is to be saved, grounded in the current `/code_summary.md` layout.

    - Place all new modules, models, helpers, and docs in their correct logical folders in adherence with the established repository organization.

    - Never introduce unexplained new folders or ad-hoc placements—justify and ground every file addition or change in the global structure.

6. **Fetch Required Files**
    - ALL required source, test, or documentation files already exist in the project tree. Fetch, read, and build upon them as necessary before proposing changes.

---

## Key Reminders

- **No implementation should start without a corresponding test committed first.**
- **Always announce in the prompt—and in file comments—where each file (test, source, doc) will be placed, referencing the code summary/project tree.**
- **Explore and reference all related documentation and specs already present in the project.**
- **Maintain strict, clear communication about file structure, intentions, and reasoning for every change to ensure maintainability and discoverability.**

---

_Disclaimer: All contributors are expected to follow this workflow. PRs or development not adhering to these steps will be rejected._