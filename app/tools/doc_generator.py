
"""
AeroLearn AI Documentation Generator
------------------------------------
Implements: Day 20 Plan, Task 3.7.4 ('Documentation Generator')
Location: /app/tools/doc_generator.py

Features:
- Component interface documentation extraction (from /app/core/, /integrations/, etc.)
- Integration point & protocol documentation compilation (/docs/architecture/*protocol.md, /docs/api/*protocol.md)
- API reference collation (/docs/api/*.md)
- Completeness/cross-reference check using /docs/doc_index.md
- Site output: Markdown, saved to /docs/generated/index.md (+ README, errors)
- Logs missing, extraneous, and undocumented items

This module can be used as both a library (for tests) and a CLI tool.
"""

import os
import re
import ast
from typing import List, Tuple, Set

DOCS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../docs/"))
CODE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
GENERATED_ROOT = os.path.join(DOCS_ROOT, "generated")
if not os.path.exists(GENERATED_ROOT):
    os.makedirs(GENERATED_ROOT, exist_ok=True)

class DocGenerator:
    def __init__(self, docs_root: str = DOCS_ROOT, code_root: str = CODE_ROOT, output_root: str = GENERATED_ROOT):
        self.docs_root = docs_root
        self.code_root = code_root
        self.output_root = output_root

        self.index_docs = self.load_doc_index()
        self.protocol_docs = self.find_protocol_docs()
        self.api_docs = self.find_api_docs()
        self.component_interfaces = []

        self.unmatched_docs: Set[str] = set()
        self.missing_docs: Set[str] = set()
        self.errors: List[str] = []

    def load_doc_index(self) -> List[str]:
        "Load the list of documentation files from /docs/doc_index.md."
        doc_index_path = os.path.join(self.docs_root, "doc_index.md")
        index_files = set()
        if os.path.isfile(doc_index_path):
            with open(doc_index_path, "r", encoding="utf-8") as f:
                for line in f:
                    match = re.search(r"\| `([^`]+)` \|", line)
                    if match:
                        index_files.add(match.group(1).replace("\\", "/"))
        return sorted(index_files)

    def find_protocol_docs(self) -> List[str]:
        "Locate all *protocol.md files under /docs/architecture and /docs/api."
        protos = []
        for folder in ("architecture", "api"):
            proto_dir = os.path.join(self.docs_root, folder)
            if not os.path.isdir(proto_dir):
                continue
            for root, _, files in os.walk(proto_dir):
                for f in files:
                    if f.endswith("protocol.md"):
                        protos.append(os.path.relpath(os.path.join(root, f), self.docs_root).replace("\\", "/"))
        return sorted(protos)

    def find_api_docs(self) -> List[str]:
        "Find all top-level API .md docs in /docs/api (excluding protocol files)."
        api_dir = os.path.join(self.docs_root, "api")
        api_docs = []
        if os.path.isdir(api_dir):
            for fname in os.listdir(api_dir):
                if fname.endswith(".md") and "protocol" not in fname:
                    api_docs.append(f"api/{fname}")
        return sorted(api_docs)

    def extract_component_interfaces(self) -> List[Tuple[str, str, str]]:
        """
        Extract (rel_file, name, docstring) for each top-level class/function in /app/core and /integrations.
        Reports undoc'd nodes to self.errors.
        """
        roots = [
            os.path.join(self.code_root, "app/core"),
            os.path.join(self.code_root, "integrations"),
        ]
        interfaces = []
        for code_root in roots:
            for dirpath, _, files in os.walk(code_root):
                for fname in files:
                    if fname.endswith(".py") and not fname.startswith("test_"):
                        src_file = os.path.join(dirpath, fname)
                        rel_file = os.path.relpath(src_file, self.code_root).replace("\\", "/")
                        with open(src_file, "r", encoding="utf-8") as f:
                            try:
                                tree = ast.parse(f.read(), filename=src_file)
                                for node in ast.iter_child_nodes(tree):
                                    if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                                        doc = ast.get_docstring(node)
                                        name = node.name
                                        if doc:
                                            interfaces.append((rel_file, name, doc))
                                        else:
                                            self.errors.append(f"Undocumented: {rel_file}::{name}")
                            except Exception as e:
                                self.errors.append(f"Parse error in {rel_file}: {e}")
        self.component_interfaces = interfaces
        return interfaces

    def check_completeness(self) -> Tuple[Set[str], Set[str]]:
        """
        Returns (missing_docs, unmatched_docs):
        - missing_docs: Listed in doc_index.md but not found in scan.
        - unmatched_docs: Found in scan but not in doc_index.md
        """
        scanned = set(self.protocol_docs + self.api_docs)
        index = set(self.index_docs)
        self.missing_docs = index - scanned
        self.unmatched_docs = scanned - index
        return self.missing_docs, self.unmatched_docs

    def generate_site(self):
        "Generate Markdown documentation: interfaces, protocols, APIs, and completeness cross-reference."
        self.extract_component_interfaces()
        missing, unmatched = self.check_completeness()
        output_index_md = os.path.join(self.output_root, "index.md")
        with open(output_index_md, "w", encoding="utf-8") as f:
            f.write("# AeroLearn AI Generated Documentation Site\n\n")
            f.write("## Component Interface Summary\n\n")
            for rel, name, doc in self.component_interfaces:
                f.write(f"### `{rel}` — `{name}`\n\n")
                f.write(f"{doc}\n\n")
            f.write("\n---\n\n## Protocol Documentation\n\n")
            for proto in self.protocol_docs:
                f.write(f"- [{proto}]({os.path.join('../', proto)})\n")
            f.write("\n---\n\n## API Documentation\n\n")
            for api in self.api_docs:
                f.write(f"- [{api}]({os.path.join('../', api)})\n")
            f.write("\n---\n\n## Documentation Index Crosscheck\n")
            if missing:
                f.write("\n### ❗ Missing in Scan (Listed in doc_index.md, not found in scan):\n")
                for m in missing:
                    f.write(f"- {m}\n")
            if unmatched:
                f.write("\n### ⚠️ Unmatched in Index (Found in scan/output, not listed in doc_index.md):\n")
                for n in unmatched:
                    f.write(f"- {n}\n")
            if self.errors:
                f.write("\n### Errors and Undocumented Sections:\n")
                for err in self.errors:
                    f.write(f"- {err}\n")
        # Process log
        with open(os.path.join(self.output_root, "README.md"), "w", encoding="utf-8") as readme:
            readme.write("# Documentation Generation Process\n\n")
            readme.write("This folder is auto-generated by the documentation generator tool.\n")
            readme.write("Main process is described in `/app/tools/doc_generator.py` and conforms to day20_plan.md 3.7.4 tasks.\n")
            readme.write("Protocols, APIs, and component interfaces are cross-linked; index is checked against `/docs/doc_index.md`.\n")
            readme.write("Errors are reported and flagged in the generated index.\n")
        return output_index_md

    def run(self):
        "Orchestrate extraction, cross-referencing, site generation, and return status."
        self.generate_site()
        return True

if __name__ == "__main__":
    gen = DocGenerator()
    gen.run()
    print(f"Documentation site generated in: {GENERATED_ROOT}")

