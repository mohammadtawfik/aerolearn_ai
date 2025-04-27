"""
auto_patch_all_tests.py

Force-inserts the universal sys.path project root patch at the top of every test file in /tests,
if not already present. Makes your import environment robust for single-file, CLI, IDE, Pytest, and CI runs.

USAGE:
    python tools/auto_patch_all_tests.py

This should be re-run after adding any new test files!
"""
import os

PATCH_MARKER = "# --- UNIVERSAL PROJECT ROOT IMPORT PATCH ---"
PATCH_LINES = [
    PATCH_MARKER,
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

def patch_exists(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        for _ in range(10):  # Check top 10 lines only for speed
            line = f.readline()
            if PATCH_MARKER in line:
                return True
    return False

def insert_patch(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.readlines()
    # Find correct insertion point after shebang or encoding line
    insert_idx = 0
    while insert_idx < len(content):
        line = content[insert_idx]
        if line.startswith("#!"):
            insert_idx += 1
        elif "coding" in line:
            insert_idx += 1
        else:
            break
    new_content = content[:insert_idx] + [l + "\n" for l in PATCH_LINES] + content[insert_idx:]
    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(new_content)

def patch_all_test_files(tests_root):
    n_patched = 0
    n_skipped = 0
    patched_files = []
    skipped_files = []
    for root, dirs, files in os.walk(tests_root):
        for fname in files:
            if fname.endswith(".py"):
                fpath = os.path.join(root, fname)
                if patch_exists(fpath):
                    n_skipped += 1
                    skipped_files.append(fpath)
                else:
                    insert_patch(fpath)
                    n_patched += 1
                    patched_files.append(fpath)
    return n_patched, n_skipped, patched_files, skipped_files

if __name__ == "__main__":
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tests_root = os.path.join(repo_root, "tests")
    n_patched, n_skipped, patched, skipped = patch_all_test_files(tests_root)
    print(f"Auto-patching complete for all test files in: {tests_root}")
    print(f"  Patched files: {n_patched}")
    print(f"  Skipped (already patched): {n_skipped}")
    if n_patched > 0:
        print("  Files patched:")
        for f in patched: print("   ", f)
    print("Done.")