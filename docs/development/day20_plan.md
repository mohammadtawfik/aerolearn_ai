---
> ⚠️ **DEVELOPER WARNING – ENVIRONMENT & IMPORT ERRORS** ⚠️  
>
> Recent project history exposed two recurring mistakes that waste developer time and break tests/envs:
>
> **1. Environment Packages:**  
> - **Never install `pytest-qt`, `PyQt6`, `PyQt5`, `PySide6`, or `PySide2` in the project venv unless specifically developing/testing a Qt UI feature.**
> - Their presence can corrupt all test runs with DLL import errors, even if you aren't writing GUI code.
> - Use a separate venv for Qt or GUI work. Document and announce this before merging.
>
> **2. Import Hygiene:**  
> - **Always confirm where models/classes are defined before importing.**
> - E.g., the `Answer` class lives in `app/models/assessment.py`. Importing it from anywhere else causes project-breaking ImportErrors.
> - Use code search or consult `code_summary.md` before changing deep imports.
>
> **Mistakes here create major delays for all. Read this before beginning Day 17–31 work.**
---

# AeroLearn AI – Day 20 Plan
*Location: `/docs/development/day20_plan.md`*

## Focus: Project Management Tools – Development Tracking

---

### Task 3.7.1: Feature Development Tracker (3 hours)
- [ ] Create feature registry with component mappings
- [ ] Implement development status tracking
- [ ] Develop dependency linking between features
- [ ] Build feature impact visualization
- [ ] **Integration**: Test feature tracking across component boundaries
- [ ] **Testing**: Verify feature status updates propagate correctly
- [ ] **Documentation**: Document feature tracking workflow

---

### Task 3.7.2: Milestone Management (3 hours)
- [ ] Implement milestone definition and tracking
- [ ] Create milestone dependency mapping
- [ ] Develop progress visualization
- [ ] Build milestone risk assessment
- [ ] **Integration**: Ensure milestones can span multiple components
- [ ] **Testing**: Verify milestone progress calculation accuracy
- [ ] **Documentation**: Document milestone planning process

---

### Task 3.7.3: Resource Allocation Tools (2 hours)
- [ ] Create resource registry and availability tracking
- [ ] Implement resource assignment to components
- [ ] Develop resource utilization visualization
- [ ] Build resource constraint analysis
- [ ] **Integration**: Test resource allocation across component teams
- [ ] **Testing**: Verify resource conflict detection
- [ ] **Documentation**: Document resource allocation best practices

---

### Task 3.7.4: Documentation Generator (2 hours)
- [ ] Implement component interface documentation extraction
- [ ] Create integration point documentation compilation
- [ ] Develop API reference generator
- [ ] Build documentation site generator
- [ ] **Integration**: Test with documentation from all components
- [ ] **Testing**: Verify documentation completeness and accuracy
- [ ] **Documentation**: Document the documentation generation process

---

#### Daily Notes
- Progress/cross-team blockers:
- Testing & review assignments:
- Documentation assignments:
- End-of-day summary:
