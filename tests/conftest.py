# --- UNIVERSAL PROJECT ROOT IMPORT PATCH ---
import os
import sys
import pytest

def _find_project_root():
    here = os.path.abspath(os.path.dirname(__file__))
    root = here
    while root and not (os.path.isdir(os.path.join(root, "app")) and os.path.isdir(os.path.join(root, "tests"))):
        parent = os.path.dirname(root)
        if parent == root: break
        root = parent
    return root

def _add_project_root_to_syspath():
    root = _find_project_root()
    if root and root not in sys.path:
        sys.path.insert(0, root)
_add_project_root_to_syspath()
# --- END PATCH ---

# Define mandatory documentation files (relative to project root)
DOCS_MANDATORY = [
    "docs/doc_index.md",
    "docs/architecture/architecture_overview.md",
    "docs/development/sprint_plan.md",
    "docs/architecture/service_health_protocol.md",
    "docs/architecture/dependency_tracking_protocol.md"
]

@pytest.fixture(autouse=True, scope="session")
def docs_awareness():
    """Fail test run if key docs are missing; print/log doc context."""
    project_root = _find_project_root()
    missing = []
    loaded = []
    for f in DOCS_MANDATORY:
        abs_f = os.path.join(project_root, f)
        if not os.path.exists(abs_f):
            missing.append(f)
        else:
            loaded.append(f)
    if missing:
        raise RuntimeError(f"Critical documentation missing for test run: {missing}\n"
                           f"(cwd={os.getcwd()}, proj_root={project_root})")
    print(f"[DOCS PRE-LOAD] Loaded docs for TDD/dev cycle:\n" + "\n".join(f"- {doc}" for doc in loaded))
