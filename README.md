# AeroLearn AI

**A Modern, Modular Platform for Adaptive Aerospace Education**

---

## Overview

AeroLearn AI is an integrated platform for adaptive and personalized aerospace education. It combines modular component architecture, advanced event-driven communication, secure authentication, flexible data storage, and AI-powered learning assistance.

The project is organized to deliver a scalable, robust foundation for rapid educational application prototyping and deployment.

---

## Project Structure

```
├── app                 # Main application modules (auth, UI, models, API)
│   ├── core            # Core application functionality
│   ├── models          # Data models and storage interfaces
│   ├── ui              # User interface components
│   └── utils           # Utility functions and helpers
├── integrations        # Integration framework: events, interfaces, monitoring, registry
├── scripts             # Setup and utility scripts
├── tests               # Comprehensive test suites (unit, integration, UI, mocks)
├── docs                # Architecture, integration, and user/developer documentation
├── resources           # Static resources, templates, sample data
├── tools               # Project management, monitoring utilities
```

---

## Architecture Overview

AeroLearn AI uses a **modular, event-driven architecture** aligning with modern best practices for extensibility and testability:

- **Event Bus System:** Enables loose coupling and cross-component messaging
- **Component Registry:** Centralizes lifecycle and dependency management
- **Interface Contracts:** Standardized interfaces for major functional areas
- **Monitoring Foundation:** Built-in tools for health metrics and status tracking
- **Separation of Concerns:** Clear split between core domain, integrations, and UI logic

For a deeper dive, see [docs/architecture/architecture_overview.md](docs/architecture/architecture_overview.md).

---

## Key Features

- **AI-powered Content Analysis:** Intelligent indexing and organization of educational materials
- **Adaptive Learning Assistance:** Personalized chatbot support for students
- **Comprehensive Analytics:** Progress tracking and performance insights
- **Content Enhancement:** AI-driven suggestions for improving educational materials
- **Cross-course Content Analysis:** Similarity detection and knowledge mapping
- **Cloud Integration:** Seamless synchronization with Google Drive and other services

---

## Installation

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure environment variables (copy `.env.example` to `.env` and edit)
4. Run setup script: `python scripts/setup.py`
5. Launch the application: `python -m app`

## PyQt6-Only UI Environment Policy

**IMPORTANT: To run or test the UI components:**

1. **Create and activate a dedicated virtual environment for UI work:**
   ```sh
   python -m venv .venv-ui
   source .venv-ui/bin/activate  # Or activate as appropriate for your OS
   ```

2. **Install only these packages:**
   ```sh
   pip install --upgrade pip
   pip install pytest pytest-qt PyQt6
   ```

3. **Never install `PyQt5`, `PySide2`, or `PySide6`** in the same environment.
   - These will cause conflicts and break the UI and test suite
   - DLL/QtCore import errors typically indicate a mixed environment

4. **Troubleshooting:**
   - If UI components fail to launch or import, ensure only PyQt6 is installed
   - Add `qt_api = pyqt6` to the `[pytest]` section in your `pytest.ini`
   - See [`/docs/development/pytest-qt-pyqt6-fix.md`](docs/development/pytest-qt-pyqt6-fix.md) for complete troubleshooting

5. **Project Rule:**
   - All UI test code and fixtures use **only** PyQt6
   - Tests will fail explicitly if PyQt6 is missing
   - UI components should not be run from the main backend/server environment

> **Important:** Do NOT install PyQt6, PyQt5, PySide2, PySide6, or pytest-qt in your main project virtual environment. These packages may cause internal errors and make all pytest runs fail if Qt DLLs are absent or misconfigured, even if no GUI code is tested. Always use a separate virtual environment dedicated to GUI/UI tests.

## Setting the UI Environment Variable

You **must** set the environment variable `AEROLEARN_UI_VENV=1` before running any UI components or PyQt6-related tests.

### Quick Steps by Platform

**On Linux/Mac:**
```sh
export AEROLEARN_UI_VENV=1
python app/main.py
```
or, for tests:
```sh
export AEROLEARN_UI_VENV=1
pytest tests/ui/
```

**On Windows (CMD):**
```cmd
set AEROLEARN_UI_VENV=1
python app\main.py
```

**On Windows (PowerShell):**
```powershell
$env:AEROLEARN_UI_VENV="1"
python app\main.py
```

### IDE Configuration

**In PyCharm:**
1. Go to Run → Edit Configurations
2. Select your run configuration
3. Expand "Environment variables"
4. Add: `AEROLEARN_UI_VENV=1`
5. Click Apply and OK

**In VS Code:**
1. Open `.vscode/launch.json` (create if needed)
2. Add to your configuration:
   ```json
   "env": {
       "AEROLEARN_UI_VENV": "1"
   }
   ```

**Permanent Setup:**
- Add to your shell profile (~/.bashrc, ~/.zshrc, etc.):
  ```sh
  export AEROLEARN_UI_VENV=1
  ```

If this environment variable is not set, UI components and tests will refuse to run to prevent Qt dependency conflicts.

---

## Development

The current development follows the **Phase 1: Integration Framework Foundation** plan:

- [x] Event bus, types, and subscribers
- [x] Component registry and dependency tracker
- [x] Interface contracts for all major integration points
- [x] Foundation for monitoring health/status/transactions
- [ ] Authentication, storage, API, UI, and test framework (next phases)

See the [Contributing Guidelines](CONTRIBUTING.md) for information on how to contribute to this project.

---

## Documentation

Detailed documentation is available in the `docs/` directory:

- [Architecture Documentation](docs/architecture/) - System design and component interactions
- [Integration Framework](docs/integration_framework.md) - Event system and component registry
- [API Documentation](docs/api/) - Interface specifications and usage examples
- [User Guides](docs/user_guides/) - End-user and administrator documentation
- [Development Guide](docs/development/) - Developer how-tos and technical deep-dives

---

## Core Components

### 1. Authentication & Authorization
  - Secure credential management and role-based access control

### 2. API Integration
  - Extensible API clients for AI services, cloud storage, and custom providers

### 3. Data Model & Storage
  - ORM models, schema management, and local/cloud file storage

### 4. UI Foundation
  - Component-based desktop UI system with navigation and content management

---

## License

See individual LICENSE.md files in dependencies (for bundled open source modules), and project-level license to be added upon release.
