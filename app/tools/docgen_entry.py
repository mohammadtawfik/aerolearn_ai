"""
CLI Entrypoint for DocGenerator.

Usage:
    python app/tools/docgen_entry.py

This wraps app/tools/doc_generator.py for command-line usage, supporting:
- Manual developer execution
- CI/CD pipeline integration
- Scripted documentation generation

The generator creates HTML documentation from source code comments.
"""

import sys
import os
# Ensure the tools directory is in the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from doc_generator import DocGenerator

def main():
    """Run the documentation generator.
    
    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    try:
        gen = DocGenerator()
        gen.run()
        print("Documentation site generated at: docs/generated/")
        return 0
    except Exception as e:
        print(f"Error generating documentation: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
