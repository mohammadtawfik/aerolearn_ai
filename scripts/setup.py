#!/usr/bin/env python3
"""
Setup script for AeroLearn AI development environment.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 9):
        print("Error: AeroLearn AI requires Python 3.9 or higher")
        sys.exit(1)


def create_virtual_env(venv_path):
    """Create a virtual environment."""
    if not os.path.exists(venv_path):
        print(f"Creating virtual environment at {venv_path}")
        subprocess.run([sys.executable, "-m", "venv", venv_path], check=True)
        print("Virtual environment created")
    else:
        print(f"Virtual environment already exists at {venv_path}")


def install_dependencies(venv_path, dev=False):
    """Install project dependencies."""
    # Construct path to pip
    if os.name == "nt":  # Windows
        pip_path = os.path.join(venv_path, "Scripts", "pip")
    else:  # macOS/Linux
        pip_path = os.path.join(venv_path, "bin", "pip")
 
    # Upgrade pip
    subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
 
    # Install dependencies
    req_file = "requirements-dev.txt" if dev else "requirements.txt"
    print(f"Installing dependencies from {req_file}")
    subprocess.run([pip_path, "install", "-r", req_file], check=True)
    print("Dependencies installed")


def setup_environment(env_file=".env.example"):
    """Set up environment variables."""
    if not os.path.exists(".env"):
        if os.path.exists(env_file):
            print(f"Creating .env file from {env_file}")
            with open(env_file, "r") as source:
                with open(".env", "w") as target:
                    target.write(source.read())
            print(".env file created. Please update it with your actual configuration.")
        else:
            print(f"Warning: {env_file} not found. Please create .env file manually.")
    else:
        print(".env file already exists")


def setup_pre_commit(venv_path):
    """Install and configure pre-commit hooks."""
    if os.name == "nt":  # Windows
        pre_commit_path = os.path.join(venv_path, "Scripts", "pre-commit")
    else:  # macOS/Linux
        pre_commit_path = os.path.join(venv_path, "bin", "pre-commit")
 
    if os.path.exists(".git"):
        if os.path.exists(pre_commit_path):
            print("Installing pre-commit hooks")
            subprocess.run([pre_commit_path, "install"], check=True)
            print("Pre-commit hooks installed")
        else:
            print("Warning: pre-commit not found in virtual environment")
    else:
        print("Warning: Not a git repository, skipping pre-commit setup")


def create_secure_directory():
    """Create secure directory for credentials."""
    secure_dir = "secure_credentials"
    if not os.path.exists(secure_dir):
        os.makedirs(secure_dir)
        print(f"Created {secure_dir} directory for storing credentials")
     
        # Create a README file in the secure directory
        readme_path = os.path.join(secure_dir, "README.md")
        with open(readme_path, "w") as f:
            f.write("""# Secure Credentials

This directory is for storing sensitive credential files such as:
- DeepSeek API key
- Google service account JSON files
- Other API keys and secrets

**IMPORTANT**: Files in this directory should NEVER be committed to version control.
The directory is included in .gitignore to prevent accidental commits.

## How to use

1. Place your credential files in this directory
2. Reference them in your .env file using relative paths
3. The application will load them securely at runtime

Example .env entry:
GOOGLE_APPLICATION_CREDENTIALS=./secure_credentials/service-account.json

""")
        print("Added instructions for storing credentials")


def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(description="Set up AeroLearn AI development environment")
    parser.add_argument("--dev", action="store_true", help="Install development dependencies")
    parser.add_argument("--venv", default="venv", help="Path to virtual environment")
    args = parser.parse_args()
    
    print("Setting up AeroLearn AI development environment")
    
    # Check Python version
    check_python_version()
    
    # Create virtual environment
    venv_path = args.venv
    create_virtual_env(venv_path)
    
    # Install dependencies
    install_dependencies(venv_path, args.dev)
    
    # Setup environment variables
    setup_environment()
    
    # Create secure credentials directory
    create_secure_directory()
    
    # Setup pre-commit if in dev mode
    if args.dev:
        setup_pre_commit(venv_path)
    
    print("
Setup complete!")
    print(f"Activate the virtual environment with:")
    if os.name == "nt":  # Windows
        print(f"    {venv_path}\Scripts\activate")
    else:  # macOS/Linux
        print(f"    source {venv_path}/bin/activate")
    print("
Start the application with:")
    print("    python -m app.main")


if __name__ == "__main__":
    main()
