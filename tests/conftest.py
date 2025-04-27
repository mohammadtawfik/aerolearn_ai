# --- UNIVERSAL PROJECT ROOT IMPORT PATCH ---
import os
import sys

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
