import os
import pathlib
import json
import datetime

def create_directory(path):
    """Create directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)
    print(f"Created directory: {path}")

def create_file(path, content=""):
    """Create file with given content."""
    with open(path, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Created file: {path}")

def create_init_file(path):
    """Create a Python __init__.py file."""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    content = f'''"""
AeroLearn AI - Aerospace Engineering Education Platform
Created: {today}

This module is part of the AeroLearn AI project.
"""

'''
    create_file(os.path.join(path, "__init__.py"), content)

def generate_project_structure():
    # Code remains the same until the architecture_doc section...
    
    # Create a basic architecture document with plain ASCII characters
    architecture_doc = """# AeroLearn AI System Architecture

## Overview

AeroLearn AI is designed with a component-based architecture to ensure modularity, extensibility, and robust integration between system components. The architecture follows a layered approach with clear separation of concerns.

## Core Architecture Components

### 1. Application Core

The application core provides fundamental services and utilities:

- **Authentication & Authorization**: User authentication, role-based access control
- **Database Operations**: Cloud database connectivity, local cache synchronization
- **Google Drive Integration**: File storage, retrieval, and metadata management
- **AI Services**: Integration with DeepSeek API, content analysis, vector embeddings

### 2. User Interfaces

Three separate but integrated interfaces:

- **Professor Interface**: Content management, student monitoring, analytics
- **Student Interface**: Content access, AI learning assistance, progress tracking
- **Administrator Interface**: System management, user administration, reporting

### 3. Integration Framework

Ensures seamless communication between components:

- **Standardized Interfaces**: Clear contracts for component interactions
- **Component Registry**: Dynamic registration and discovery of components
- **Event System**: Publisher-subscriber model for loose coupling

### 4. Data Model

Structured representation of system entities:

- **User Models**: Authentication, profile, permissions
- **Course Models**: Structure, metadata, relationships
- **Content Models**: Various content types, metadata, embeddings
- **Assessment Models**: Questions, answers, evaluations, analytics

## System Diagrams

### Component Interaction Diagram

+-------------------+ +-------------------+ +-------------------+ | Professor UI | | Student UI | | Admin UI | +--------+----------+ +---------+---------+ +---------+---------+ | | | v v v +----------------------------------------------------------------+ | Core Application Layer | +----------------+----------------+----------------+---------------+ | Auth Service | Storage Service | AI Service | Analytics | +--------+-------+--------+-------+--------+-------+-------+-------+ | | | | v v v v +-------------+ +----------------+ +------------+ +------------+ | User Data | | Google Drive | | DeepSeek | | Database | +-------------+ +----------------+ +------------+ +------------+


### Integration Framework

+--------------------------------------------------------------+ | Integration Framework | +----------------+----------------+---------------------------+ | Interfaces | Registry | Event System | | - Define | - Component | - Publish/Subscribe | | contracts | registration | - Event routing | | - Version | - Service | - Cross-component | | management | discovery | communication | +----------------+----------------+---------------------------+


## Security Architecture

- Secure credential storage
- Role-based access control
- Data encryption
- API authentication
- Privacy protection

## Integration Principles

1. Standardized interfaces for all component interactions
2. Explicit definition of component dependencies
3. Versioning of interfaces for backward compatibility
4. Automated testing of integration points
5. Component health monitoring and conflict detection
"""
    create_file(os.path.join("", "docs/architecture/architecture_overview.md"), architecture_doc)
    
    print(f"\nProject structure generated in: {os.path.abspath(base_dir)}")
    print("You can start development by:")
    print(f"1. cd {base_dir}")
    print("2. python scripts/setup.py --dev")
    print("3. Activate the virtual environment")
    print("4. python -m app.main")

if __name__ == "__main__":
    generate_project_structure()