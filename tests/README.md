# AeroLearn AI Testing Directory Structure and Policy

## Overview

Our test structure is designed for clear discovery, simple maintenance, and compatibility with modern IDEs, pytest, and CI/CD pipelines.

## Directory Layout

- `/tests` — All automated and manual tests for the codebase.
    - `/unit` — Unit tests by feature area.
        - `/core` — For core backend (algorithms, services, ...).
        - `/ui` — For user interfaces (PyQt widgets, logic).
    - `/integration` — Integration and scenario/workflow tests.
    - `/models`, `/fixtures` — Model and test data helpers.

## Guidelines

- **One-to-One Rule**: For each non-trivial module under `/app/`, there should be at least one test module under `/tests/unit/` or `/tests/integration/`.
- **Namespace Packages**: Minimal `__init__.py` files are present in every folder for Python namespace and discovery.
- **Imports**: Always use full project imports (e.g., `from app.core.upload.upload_service import UploadService`). The test sys.path or pytest.ini will ensure these work.
- **Working Directory**: All tests must be run with the project root as the working directory.
- **sys.path Patch**: Each test file should include a sys.path patch at the very top to ensure imports work regardless of how the test is invoked.

## Running Tests

Always run pytest from the project root (`aerolearn_ai/`) to ensure the `app` package is discoverable:

```bash
# Run all tests
pytest

# Run tests for a specific module
pytest tests/unit/core/upload
```

For coverage:
```bash
pytest --cov=app
```

## Critical Note for All Testers

Some IDEs (notably PyCharm) and direct test invocations set the Python working directory to the test's folder, *not* the project root.
This can cause persistent `ModuleNotFoundError: No module named 'app'` or similar—even with `pytest.ini` or `conftest.py`.

### Required sys.path Patch

Every test file should start with this sys.path patch **before all other imports**:

```python
import os
import sys
# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
# Now app imports will work
from app.your_module import YourClass
```

### Working Directory Settings

- **Command Line**: Always run from project root:
  ```
  cd /path/to/aerolearn_ai
  pytest
  ```

- **PyCharm/VSCode**: 
  - Set "Working directory" to project root in run configurations
  - Right-click on test directory and select "Run tests in..." but verify working directory is correct

### Why This Matters

Python's import system relies on `sys.path`. Tests in deep directories cannot import `app.` modules unless:
1. The working directory is the project root, OR
2. The test file patches `sys.path` at the very top

Both CI/CD pipelines and local development must follow these practices for consistent results.

## Troubleshooting

- If you see _ModuleNotFoundError: No module named 'app'_, check your current directory and ensure imports use the full dotted path.
- If running via IDE, make sure "working directory" is set to project root.
- Do *not* try to run the test file as a script unless you have the working directory at the project root.
- Verify the sys.path patch is at the top of your test file, before any other imports.

## Key Files

- **pytest.ini** — Settings for pytest root.
- **.coveragerc** — Coverage.py config for `app/` code.
- **unit/core/upload/test_upload_service.py** — Example for UploadService.
- **unit/core/upload/README.md** — Per-feature test notes.

## Best Practices

- Keep tests close to code design/feature granularity.
- Write tests for **every bug/fix/feature**, not just initial development.
- Use fixtures and patching for resource management.
- Place new unit tests for `app/` code under `/tests/unit/` by feature area.
- Keep minimal `__init__.py` files in every test directory branch for discoverability and namespace support.

## New Test Files

- Add a new directory branch with an `__init__.py` for proper discovery.
- Document special test dependencies or strategies in module-level README.md as needed.
- Follow the naming convention: `test_[module_name].py` for test files.
- **Always include the sys.path patch** at the top of each test file before any other imports.

## Developer Onboarding

1. Familiarize yourself with the test structure before writing new code.
2. Run the test suite to ensure your environment is properly set up.
3. When adding new features, write tests first (TDD approach) or alongside development.
4. Review test coverage reports to identify gaps in test coverage.

---
