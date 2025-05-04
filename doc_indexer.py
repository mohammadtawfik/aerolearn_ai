import os
from datetime import datetime

DOCS_ROOT = "docs"
INDEX_FILE = os.path.join(DOCS_ROOT, "doc_index.md")

def scan_docs_tree(root_dir):
    docs = []
    for base, dirs, files in os.walk(root_dir):
        for f in files:
            if f.endswith(".md"):
                full_path = os.path.join(base, f)
                # Basic doc title: first non-empty, non-comment line
                with open(full_path, encoding="utf-8") as fp:
                    for line in fp:
                        line = line.strip()
                        if line and not line.startswith("#!"):
                            title = line.replace("#", "").strip(': -')
                            break
                    else:
                        title = f
                lastmod = datetime.fromtimestamp(os.path.getmtime(full_path))
                docs.append((full_path, title, lastmod))
    return docs

def write_index(docs, outfile):
    outdir = os.path.dirname(outfile)
    if not os.path.exists(outdir):
        os.makedirs(outdir, exist_ok=True)
    with open(outfile, "w", encoding="utf-8") as out:
        out.write("# Documentation Index\n\n")
        out.write("| Path | Title | Last Modified |\n")
        out.write("|------|-------|---------------|\n")
        for path, title, lastmod in sorted(docs, key=lambda x: x[0]):
            out.write(f"| `{path}` | {title} | {lastmod.strftime('%Y-%m-%d %H:%M:%S')} |\n")
        out.write("\n*Auto-generated, do not edit by hand.*\n")

def main():
    docs = scan_docs_tree(DOCS_ROOT)
    write_index(docs, INDEX_FILE)
    print(f"Documentation index written to {INDEX_FILE}")

if __name__ == "__main__":
    main()
