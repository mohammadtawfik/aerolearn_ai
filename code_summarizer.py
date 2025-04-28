#!/usr/bin/env python3

"""
CodeSummarizer: A tool to create concise summaries of Python codebases
for maintaining context in AI assistant conversations.

This script:
1. Scans a project directory for Python files
2. Extracts key information (imports, classes, functions, docstrings)
3. Creates a structured summary
4. Optionally enhances the summary using DeepSeek API
"""

import os
import ast
import re
import json
import argparse
from typing import Dict, List, Optional, Set, Tuple, Union
import requests
from concurrent.futures import ThreadPoolExecutor

# ANSI colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class CodeSummarizer:
    def __init__(self, 
                 project_path: str, 
                 output_path: str = None,
                 deepseek_api_key: str = None,
                 max_files: int = None,
                 exclude_patterns: List[str] = None,
                 max_threads: int = 10):
        """
        Initialize the CodeSummarizer.
        
        Args:
            project_path: Path to the project directory
            output_path: Path to save the summary (default: project_path/code_summary.md)
            deepseek_api_key: Optional API key for DeepSeek
            max_files: Maximum number of files to process (None for all)
            exclude_patterns: List of regex patterns to exclude files/directories
            max_threads: Maximum number of threads for parallel processing
        """
        self.project_path = os.path.abspath(project_path)
        self.output_path = output_path or os.path.join(self.project_path, "code_summary.md")
        self.deepseek_api_key = deepseek_api_key
        self.max_files = max_files
        self.exclude_patterns = exclude_patterns or [
            r"__pycache__", 
            r"\.git", 
            r"\.venv", 
            r"env", 
            r"venv", 
            r"\.pytest_cache", 
            r"\.tox", 
            r"\.idea",
            r"\.vscode",
            r"node_modules",
            r"dist",
            r"build",
            r"\.egg-info"
        ]
        self.max_threads = max_threads
        self.file_count = 0
        self.imports_cache = {}
        self.dependencies = {}

    def scan_project(self) -> Dict:
        """Scan the project and build a representation of the codebase."""
        print(f"{Colors.HEADER}Scanning project at {self.project_path}{Colors.ENDC}")
        
        python_files = self._find_python_files()
        project_info = {
            "project_name": os.path.basename(self.project_path),
            "file_count": len(python_files),
            "directory_structure": self._get_directory_structure(),
            "files": {}
        }
        
        # Process files in parallel
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            file_infos = list(executor.map(self._process_file, python_files))
        
        # Add processed files to project info
        for file_path, file_info in zip(python_files, file_infos):
            if file_info:  # Only add if file was successfully processed
                rel_path = os.path.relpath(file_path, self.project_path)
                project_info["files"][rel_path] = file_info
        
        # Build dependency graph
        self._build_dependency_graph(project_info)
        
        return project_info

    def _find_python_files(self) -> List[str]:
        """Find all Python files in the project directory."""
        python_files = []
        
        for root, dirs, files in os.walk(self.project_path):
            # Apply exclusion patterns to directories
            dirs[:] = [d for d in dirs if not any(re.search(pattern, d) for pattern in self.exclude_patterns)]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    # Apply exclusion patterns to files
                    if not any(re.search(pattern, file_path) for pattern in self.exclude_patterns):
                        python_files.append(file_path)
                        
                        if self.max_files and len(python_files) >= self.max_files:
                            return python_files
        
        return python_files

    def _get_directory_structure(self) -> Dict:
        """Generate a nested dictionary representing the directory structure."""
        structure = {}
        
        for root, dirs, files in os.walk(self.project_path):
            # Apply exclusion patterns
            dirs[:] = [d for d in dirs if not any(re.search(pattern, d) for pattern in self.exclude_patterns)]
            
            # Skip excluded directories
            if any(re.search(pattern, root) for pattern in self.exclude_patterns):
                continue
            
            # Get relative path
            rel_path = os.path.relpath(root, self.project_path)
            if rel_path == '.':
                current = structure
            else:
                # Navigate to the correct position in the structure
                current = structure
                for part in rel_path.split(os.sep):
                    if part not in current:
                        current[part] = {}
                    current = current[part]
            
            # Add files and directories
            for dir_name in dirs:
                if dir_name not in current:
                    current[dir_name] = {}
            
            for file in files:
                if file.endswith('.py'):
                    current[file] = None
        
        return structure

    def _process_file(self, file_path: str) -> Optional[Dict]:
        """Extract information from a Python file."""
        rel_path = os.path.relpath(file_path, self.project_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            # Parse the file
            tree = ast.parse(file_content)
            
            # Extract imports
            imports = self._extract_imports(tree)
            self.imports_cache[rel_path] = imports
            
            # Extract classes and functions
            classes = self._extract_classes(tree)
            functions = self._extract_functions(tree, module_level=True)
            
            # Extract module docstring
            module_docstring = ast.get_docstring(tree)
            
            file_info = {
                "imports": imports,
                "classes": classes,
                "functions": functions,
                "module_docstring": module_docstring
            }
            
            self.file_count += 1
            print(f"{Colors.GREEN}Processed {self.file_count}: {rel_path}{Colors.ENDC}")
            
            return file_info
            
        except Exception as e:
            print(f"{Colors.FAIL}Error processing {rel_path}: {str(e)}{Colors.ENDC}")
            return None

    def _extract_imports(self, tree: ast.Module) -> List[Dict]:
        """Extract all imports from an AST."""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append({
                        "type": "import",
                        "name": name.name,
                        "alias": name.asname
                    })
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for name in node.names:
                    imports.append({
                        "type": "import_from",
                        "module": module,
                        "name": name.name,
                        "alias": name.asname
                    })
        
        return imports

    def _extract_classes(self, tree: ast.Module) -> List[Dict]:
        """Extract all classes from an AST."""
        classes = []
        
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                # Get base classes
                bases = [self._get_name(base) for base in node.bases]
                
                # Get docstring
                docstring = ast.get_docstring(node)
                
                # Get methods
                methods = self._extract_functions(node)
                
                # Get class variables
                class_vars = []
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                # Try to get the value
                                value = None
                                if isinstance(item.value, ast.Constant):
                                    value = item.value.value
                                elif isinstance(item.value, ast.Str):  # For Python < 3.8
                                    value = item.value.s
                                
                                class_vars.append({
                                    "name": target.id,
                                    "value": str(value) if value is not None else None
                                })
                
                classes.append({
                    "name": node.name,
                    "bases": bases,
                    "docstring": docstring,
                    "methods": methods,
                    "class_variables": class_vars
                })
        
        return classes

    def _extract_functions(self, node: Union[ast.Module, ast.ClassDef], module_level: bool = False) -> List[Dict]:
        """Extract all functions from an AST node (module or class)."""
        functions = []
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                # Skip if this is a class method but we're looking for module-level functions
                if module_level and isinstance(node, ast.ClassDef):
                    continue
                    
                # Get docstring
                docstring = ast.get_docstring(item)
                
                # Get parameters
                params = []
                for arg in item.args.args:
                    params.append(arg.arg)
                
                # Check for decorators
                decorators = []
                for decorator in item.decorator_list:
                    if isinstance(decorator, ast.Name):
                        decorators.append(decorator.id)
                    elif isinstance(decorator, ast.Attribute):
                        decorators.append(self._get_name(decorator))
                    elif isinstance(decorator, ast.Call):
                        decorators.append(self._get_name(decorator.func))
                
                functions.append({
                    "name": item.name,
                    "parameters": params,
                    "docstring": docstring,
                    "decorators": decorators
                })
        
        return functions

    def _get_name(self, node: ast.AST) -> str:
        """Get the full name of an AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Call):
            return self._get_name(node.func)
        return "unknown"

    def _build_dependency_graph(self, project_info: Dict):
        """Build a dependency graph between files."""
        dependency_graph = {}
        
        # Build a mapping of module names to files
        module_to_file = {}
        for file_path in project_info["files"]:
            # Convert file path to potential module name
            module_name = file_path.replace('/', '.').replace('\\', '.').replace('.py', '')
            module_to_file[module_name] = file_path
            
            # Handle __init__.py files
            if file_path.endswith('__init__.py'):
                # The directory itself can be imported
                package_name = os.path.dirname(file_path).replace('/', '.').replace('\\', '.')
                module_to_file[package_name] = file_path
        
        # Find dependencies
        for file_path, file_info in project_info["files"].items():
            dependencies = set()
            
            for import_info in file_info.get("imports", []):
                if import_info["type"] == "import":
                    # Try to find this module in our project
                    module_name = import_info["name"]
                    if module_name in module_to_file:
                        dependencies.add(module_to_file[module_name])
                    # Check for submodules
                    for potential_module in module_to_file:
                        if potential_module.startswith(module_name + '.'):
                            dependencies.add(module_to_file[potential_module])
                
                elif import_info["type"] == "import_from":
                    # Try to find this module in our project
                    module_name = import_info["module"]
                    if module_name in module_to_file:
                        dependencies.add(module_to_file[module_name])
            
            dependency_graph[file_path] = list(dependencies)
        
        # Add dependency graph to project info
        project_info["dependencies"] = dependency_graph

    def generate_summary(self, project_info: Dict) -> str:
        """Generate a markdown summary of the project."""
        print(f"{Colors.BLUE}Generating summary...{Colors.ENDC}")
        
        summary = []
        summary.append(f"# Project Summary: {project_info['project_name']}\n")
        summary.append(f"*Generated on {os.path.basename(self.output_path)}*\n")
        summary.append(f"Total Python files: {project_info['file_count']}\n")
        
        # Table of contents
        summary.append("## Table of Contents\n")
        summary.append("1. [Project Structure](#project-structure)")
        summary.append("2. [Key Files](#key-files)")
        summary.append("3. [Dependencies](#dependencies)")
        summary.append("4. [Detailed Code Analysis](#detailed-code-analysis)\n")
        
        # Project structure
        summary.append("## Project Structure\n")
        summary.append("```")
        summary.append(self._format_directory_structure(project_info["directory_structure"]))
        summary.append("```\n")
        
        # Key files - identify important files based on number of dependencies
        summary.append("## Key Files\n")
        key_files = self._identify_key_files(project_info)
        for file_path, importance in key_files[:10]:  # Top 10 most important files
            rel_path = file_path
            file_info = project_info["files"].get(rel_path, {})
            docstring = file_info.get("module_docstring", "")
            docstring_short = docstring[:150] + "..." if docstring and len(docstring) > 150 else docstring
            
            summary.append(f"### {rel_path}\n")
            if docstring_short:
                summary.append(f"{docstring_short}\n")
            
            # Count number of classes and functions
            classes_count = len(file_info.get("classes", []))
            functions_count = len(file_info.get("functions", []))
            summary.append(f"- Classes: {classes_count}")
            summary.append(f"- Functions: {functions_count}")
            summary.append(f"- Dependency Score: {importance:.2f}\n")
        
        # Dependencies visualization
        summary.append("## Dependencies\n")
        summary.append("Key file relationships (files with most dependencies):\n")
        
        # Create a simplified dependency graph for the top files
        top_files = [file for file, _ in key_files[:10]]
        for file_path in top_files:
            deps = project_info["dependencies"].get(file_path, [])
            deps_in_top = [d for d in deps if d in top_files]
            if deps_in_top:
                summary.append(f"- **{file_path}** depends on: {', '.join(deps_in_top)}")
        
        summary.append("\n")
        
        # Detailed code analysis
        summary.append("## Detailed Code Analysis\n")
        
        # Sort files by importance
        sorted_files = [file for file, _ in key_files]
        
        for file_path in sorted_files:
            if file_path in project_info["files"]:
                file_info = project_info["files"][file_path]
                
                summary.append(f"### {file_path}\n")
                
                # Module docstring
                if file_info.get("module_docstring"):
                    summary.append("**Description:**\n")
                    summary.append(f"{file_info['module_docstring']}\n")
                
                # Classes
                if file_info.get("classes"):
                    summary.append("**Classes:**\n")
                    for class_info in file_info["classes"]:
                        summary.append(f"- `{class_info['name']}`")
                        if class_info["bases"]:
                            summary.append(f" (inherits from: {', '.join(class_info['bases'])})")
                        summary.append("\n")
                        
                        if class_info.get("docstring"):
                            docstring_lines = class_info["docstring"].split("\n")
                            summary.append(f"  {docstring_lines[0]}\n")
                        
                        if class_info.get("methods"):
                            method_names = [f"`{m['name']}()`" for m in class_info["methods"]]
                            if len(method_names) > 5:
                                method_names = method_names[:5] + [f"... ({len(class_info['methods']) - 5} more)"]
                            summary.append(f"  Methods: {', '.join(method_names)}\n")
                
                # Functions
                if file_info.get("functions"):
                    summary.append("**Functions:**\n")
                    for func_info in file_info["functions"]:
                        params = ", ".join(func_info["parameters"])
                        summary.append(f"- `{func_info['name']}({params})`\n")
                        
                        if func_info.get("docstring"):
                            docstring_lines = func_info["docstring"].split("\n")
                            summary.append(f"  {docstring_lines[0]}\n")
                
                summary.append("\n")
        
        return "\n".join(summary)

    def _format_directory_structure(self, structure: Dict, prefix: str = "") -> str:
        """Format the directory structure as a string."""
        lines = []
        items = list(structure.items())
        
        for i, (name, substructure) in enumerate(items):
            is_last = i == len(items) - 1
            
            # Current item
            line_prefix = prefix + ("└── " if is_last else "├── ")
            lines.append(f"{line_prefix}{name}")
            
            # Recursively process subdirectories
            if substructure is not None:  # It's a directory
                new_prefix = prefix + ("    " if is_last else "│   ")
                substructure_str = self._format_directory_structure(substructure, new_prefix)
                lines.append(substructure_str)
        
        return "\n".join(lines)

    def _identify_key_files(self, project_info: Dict) -> List[Tuple[str, float]]:
        """Identify key files based on dependencies and code complexity."""
        importance_scores = {}
        
        # Calculate in-degree for each file (how many files depend on it)
        in_degree = {}
        for file_path in project_info["files"]:
            in_degree[file_path] = 0
        
        for file_path, deps in project_info["dependencies"].items():
            for dep in deps:
                if dep in in_degree:
                    in_degree[dep] += 1
        
        # Calculate complexity score based on number of classes and functions
        for file_path, file_info in project_info["files"].items():
            class_count = len(file_info.get("classes", []))
            function_count = len(file_info.get("functions", []))
            
            # Method count across all classes
            method_count = sum(len(cls.get("methods", [])) for cls in file_info.get("classes", []))
            
            # Calculate complexity
            complexity = class_count * 3 + function_count + method_count
            
            # Calculate importance score
            # Weight in-degree more highly as it indicates architectural importance
            importance = (in_degree.get(file_path, 0) * 3) + complexity
            
            importance_scores[file_path] = importance
        
        # Sort by importance score
        sorted_files = sorted(importance_scores.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_files

    def save_summary(self, summary: str) -> None:
        """Save the summary to a file."""
        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"{Colors.GREEN}Summary saved to {self.output_path}{Colors.ENDC}")

    def enhance_with_deepseek(self, project_info: Dict, summary: str) -> str:
        """Enhance the summary using DeepSeek API."""
        if not self.deepseek_api_key:
            print(f"{Colors.WARNING}No DeepSeek API key provided. Skipping enhancement.{Colors.ENDC}")
            return summary
        
        print(f"{Colors.BLUE}Enhancing summary with DeepSeek API...{Colors.ENDC}")
        
        try:
            # Prepare the request
            url = "https://api.deepseek.com/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.deepseek_api_key}"
            }
            
            # Create a concise representation of the project to send to the API
            project_summary = {
                "project_name": project_info["project_name"],
                "file_count": project_info["file_count"],
                "key_files": self._identify_key_files(project_info)[:10],
                # Include top 10 files with full details
                "top_files": {
                    file_path: project_info["files"][file_path]
                    for file_path, _ in self._identify_key_files(project_info)[:10]
                    if file_path in project_info["files"]
                }
            }
            
            # Create the prompt
            prompt = f"""
            You are an expert code analyst. Analyze this Python project summary and enhance it with:
            
            1. A high-level architectural overview of the project
            2. Design patterns identified in the code
            3. Potential areas for refactoring or improvement
            4. Critical path analysis of key components
            5. Relationships between ALL classes and modules
            
            Here is the project information:
            {json.dumps(project_summary, indent=2)}
            
            This is the current summary that needs enhancement:
            ```
            {summary[:4000]}  # Sending a truncated version to stay within token limits
            ```
            
            Generate additional sections to be added to the summary, focusing on architectural insights.
            Don't repeat information that's already in the summary.
            """
            
            data = {
                "model": "deepseek-reasoner",
                "messages": [
                    {"role": "system", "content": "You are a helpful AI assistant specialized in code analysis."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 8000
            }
            
            # Make the request
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                response_data = response.json()
                enhanced_content = response_data["choices"][0]["message"]["content"]
                
                # Append the enhanced content to the summary
                enhanced_summary = summary + "\n\n## AI-Enhanced Analysis\n\n" + enhanced_content
                
                print(f"{Colors.GREEN}Summary enhanced with DeepSeek API{Colors.ENDC}")
                return enhanced_summary
            else:
                print(f"{Colors.FAIL}Failed to enhance summary: {response.status_code} {response.text}{Colors.ENDC}")
                return summary
                
        except Exception as e:
            print(f"{Colors.FAIL}Error enhancing summary: {str(e)}{Colors.ENDC}")
            return summary

    def run(self) -> str:
        """Run the full analysis and generate the summary."""
        project_info = self.scan_project()
        summary = self.generate_summary(project_info)
        
        if self.deepseek_api_key:
            summary = self.enhance_with_deepseek(project_info, summary)
            
        self.save_summary(summary)
        return summary

def main():
    """
    Main function that can be run both from command line and directly from an IDE.
    
    When run from an IDE without command line arguments, it will use default values
    and prompt the user for the required project path.
    """
    import sys
    
    # Check if running with command line arguments
    if len(sys.argv) > 1:
        # Parse command line arguments
        parser = argparse.ArgumentParser(description="Generate a summary of a Python codebase")
        parser.add_argument("project_path", help="Path to the project directory")
        parser.add_argument("--output", "-o", help="Path to save the summary")
        parser.add_argument("--deepseek-api-key", help="DeepSeek API key for enhanced summaries")
        parser.add_argument("--max-files", type=int, help="Maximum number of files to process")
        parser.add_argument("--exclude", nargs="+", help="Regex patterns to exclude files/directories")
        parser.add_argument("--threads", type=int, default=10, help="Number of threads for parallel processing")
        
        args = parser.parse_args()
        
        project_path = args.project_path
        output_path = args.output
        deepseek_api_key = args.deepseek_api_key or os.environ.get("DEEPSEEK_API_KEY")
        max_files = args.max_files
        exclude_patterns = args.exclude
        max_threads = args.threads
    else:
        # Interactive mode for IDE usage
        print(f"{Colors.HEADER}Running in interactive mode{Colors.ENDC}")
        
        # Get project path
        default_path = os.getcwd()
        project_path = input(f"Enter project path (default: {default_path}): ").strip() or default_path
        
        # Get output path
        default_output = os.path.join(project_path, "code_summary.md")
        output_path = input(f"Enter output file path (default: {default_output}): ").strip() or default_output
        
        # Get DeepSeek API key
        env_api_key = "sk-da8169d57c5b4bf6812a02b924492b09" #os.environ.get("DEEPSEEK_API_KEY", "")
        if env_api_key:
            use_env_key = input(f"DeepSeek API key found in environment. Use it? (y/n, default: y): ").strip().lower() != 'n'
            deepseek_api_key = env_api_key if use_env_key else None
        else:
            api_key_input = input("Enter DeepSeek API key (optional, press Enter to skip): ").strip()
            deepseek_api_key = api_key_input or None
        
        # Get max files
        max_files_input = input("Maximum number of files to process (optional, press Enter for all): ").strip()
        max_files = int(max_files_input) if max_files_input.isdigit() else None
        
        # Get exclude patterns
        exclude_input = input("Enter exclude patterns (space-separated, press Enter for defaults): ").strip()
        exclude_patterns = exclude_input.split() if exclude_input else None
        
        # Get number of threads
        threads_input = input("Number of threads for parallel processing (default: 1): ").strip()
        max_threads = int(threads_input) if threads_input.isdigit() else 1
    
    # Show settings
    print(f"{Colors.BLUE}Settings:{Colors.ENDC}")
    print(f"- Project path: {project_path}")
    print(f"- Output path: {output_path}")
    print(f"- DeepSeek API: {'Enabled' if deepseek_api_key else 'Disabled'}")
    print(f"- Max files: {max_files or 'All'}")
    print(f"- Exclude patterns: {exclude_patterns or 'Default'}")
    print(f"- Threads: {max_threads}")
    
    # Create and run the summarizer
    summarizer = CodeSummarizer(
        project_path=project_path,
        output_path=output_path,
        deepseek_api_key=deepseek_api_key,
        max_files=max_files,
        exclude_patterns=exclude_patterns,
        max_threads=max_threads
    )
    
    # Run the analysis
    summary = summarizer.run()
    
    print(f"\n{Colors.GREEN}Summary generation complete!{Colors.ENDC}")
    print(f"Summary saved to: {output_path}")
    
    return summary

if __name__ == "__main__":
    main()
