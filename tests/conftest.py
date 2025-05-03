# --- UNIVERSAL PROJECT ROOT IMPORT PATCH ---
import os
import sys
import pytest

def _add_project_root_to_syspath():
    here = os.path.abspath(os.path.dirname(__file__))
    root = here
    while root and not (os.path.isdir(os.path.join(root, "app")) and os.path.isdir(os.path.join(root, "tests"))):
        parent = os.path.dirname(root)
        if parent == root: break
        root = parent
    if root not in sys.path:
        sys.path.insert(0, root)
_add_project_root_to_syspath()
# --- END PATCH ---

# conftest.py for AeroLearn AI: Ensures 'app' in sys.path for all tests

import sys
import os

def _ensure_app_on_syspath():
    # Find the real project root (the one containing 'app' and 'tests')
    here = os.path.dirname(os.path.realpath(__file__))
    root = here
    while root and not (os.path.isdir(os.path.join(root, "app")) and os.path.isdir(os.path.join(root, "tests"))):
        parent = os.path.dirname(root)
        if parent == root: break
        root = parent
    if root and root not in sys.path:
        sys.path.insert(0, root)
_ensure_app_on_syspath()

# Define mandatory documentation files that must exist
DOCS_MANDATORY = [
    "docs/doc_index.md",
    "docs/architecture/architecture_overview.md",
    "docs/development/sprint_plan.md",
    "docs/architecture/service_health_protocol.md",
    "docs/architecture/dependency_tracking_protocol.md"
]

@pytest.fixture(autouse=True, scope="session")
def docs_awareness():
    """Fail test run if key docs are missing, and print/log doc context."""
    missing = []
    loaded = []
    for f in DOCS_MANDATORY:
        if not os.path.exists(f):
            missing.append(f)
        else:
            loaded.append(f)
    if missing:
        raise RuntimeError(f"Critical documentation missing for test run: {missing}")
    print(f"[DOCS PRE-LOAD] Loaded docs for TDD/dev cycle:\n" + "\n".join(f"- {f}" for f in loaded))
