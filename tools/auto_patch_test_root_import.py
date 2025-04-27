"""
auto_patch_test_root_import.py

AeroLearn AI — Utility to Insert Universal Project Root Import Patch in All Test Files

Usage:
    python tools/auto_patch_test_root_import.py

- Recursively scans all *.py files under /tests
- For each file, checks for presence of universal sys.path patch
- If missing, inserts the patch at the true top of the file (lines are preserved)
- Idempotent: Will *not* add the patch if already present
- Prints summary (files patched, files skipped)

To add this for new tests: re-run this script as needed!
"""

import os
import sys

TESTS_ROOT = os.path.join(os.path.dirname(__file__), '..', 'tests')

PATCH_LINES = [
    "# --- UNIVERSAL PROJECT ROOT IMPORT PATCH ---",
    "import os",
    "import sys",
    "",
    "def _add_project_root_to_syspath():",
    "    here = os.path.abspath(os.path.dirname(__file__))",
    "    root = here",
    "    while root and not (os.path.isdir(os.path.join(root, \"app\")) and os.path.isdir(os.path.join(root, \"tests\"))):",
    "        parent = os.path.dirname(root)",
    "        if parent == root: break",
    "        root = parent",
    "    if root not in sys.path:",
    "        sys.path.insert(0, root)",
    "_add_project_root_to_syspath()",
    "# --- END PATCH ---",
    "",
]

def patch_exists_in_content(content):
    return "# --- UNIVERSAL PROJECT ROOT IMPORT PATCH ---" in content

def process_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    if patch_exists_in_content(content):
        return False  # Already patched
    # Insert before any other code, after shebang and encoding lines if present
    lines = content.splitlines()
    insert_at = 0
    while insert_at < len(lines):
        line = lines[insert_at]
        if line.startswith("#!"):      # shebang
            insert_at += 1
        elif "coding" in line:         # encoding/pep263
            insert_at += 1
        else:
            break
    new_lines = lines[:insert_at] + PATCH_LINES + lines[insert_at:]
    with open(filepath, "w", encoding="utf-8") as f:
        f.write('\n'.join(new_lines) + '\n')
    return True

def main():
    files_patched = []
    files_skipped = []
    for root, dirs, files in os.walk(TESTS_ROOT):
        for fname in files:
            if fname.endswith(".py"):
                fpath = os.path.join(root, fname)
                if process_file(fpath):
                    files_patched.append(fpath)
                else:
                    files_skipped.append(fpath)
    print(f"Patch insertion complete.")
    print(f"- Patched: {len(files_patched)} files")
    print(f"- Skipped (already patched): {len(files_skipped)} files")

if __name__ == "__main__":
    main()