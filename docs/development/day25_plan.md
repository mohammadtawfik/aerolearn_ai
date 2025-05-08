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

# AeroLearn AI – Day 25 Plan
*Location: `/docs/development/day25_plan.md`*

## Focus: AI Enhancement – Recommendation Engine

---

### Task 4.4.1: Student Learning Path Recommendations (3 hours)
- [ ] Implement personalized learning path generation
- [ ] Create prerequisite-based sequencing
- [ ] Develop adaptive difficulty progression
- [ ] Build personalized pace recommendations
- [ ] **Integration**: Test path generation across different content types
- [ ] **Testing**: Verify path appropriateness for different students
- [ ] **Documentation**: Document learning path algorithms

---

### Task 4.4.2: Content Optimization Suggestions (3 hours)
- [ ] Create content improvement workflow
- [ ] Implement specific enhancement templates
- [ ] Develop before/after content previews
- [ ] Build improvement tracking and analytics
- [ ] **Integration**: Test suggestions for all content formats
- [ ] **Testing**: Verify suggestion quality and applicability
- [ ] **Documentation**: Document optimization suggestion workflow

---

### Task 4.4.3: Personalized Material Selection (2 hours)
- [ ] Implement student learning style detection
- [ ] Create content-style matching algorithms
- [ ] Develop personalized content filtering
- [ ] Build adaptive content presentation
- [ ] **Integration**: Ensure personalization works across components
- [ ] **Testing**: Verify personalization improves learning outcomes
- [ ] **Documentation**: Document personalization approach

---

### Task 4.4.4: Professor Teaching Insights (2 hours)
- [ ] Create teaching effectiveness analytics
- [ ] Implement content impact visualization
- [ ] Develop student engagement correlation
- [ ] Build teaching strategy recommendations
- [ ] **Integration**: Test with data from multiple components
- [ ] **Testing**: Verify insight accuracy and actionability
- [ ] **Documentation**: Document teaching insight methodology

---

### Task 4.4.5: Cross-Course Recommendation Integration (2 hours)
- [ ] Implement cross-course data aggregation
- [ ] Create unified recommendation engine
- [ ] Develop cross-referencing of related content
- [ ] Build curriculum-wide optimization suggestions
- [ ] **Integration**: Test recommendations across course boundaries
- [ ] **Testing**: Verify cross-course recommendation relevance
- [ ] **Documentation**: Document cross-course recommendation engine

---

#### Daily Notes
- Progress/cross-team blockers:
- Testing & review assignments:
- Documentation assignments:
- End-of-day summary:

---

## Appendix: Test-Driven & Protocol-First Preparation Guidance

> **This appendix exists to align all Day 25 feature development with strict TDD and protocol-driven project rules.**  
> *No code, tests, or implementation may begin on any new surface until the following process is satisfied for each functional block below.*

### PREPARATION CHECKLIST FOR EACH DAY 25 FEATURE

1. **Test Skeletons First:**  
   - Before implementation, create modular/unit test stubs for:
     - Learning path recommendations (`/tests/unit/core/ai/test_learning_path.py`)
     - Content optimization suggestions (`/tests/unit/core/ai/test_content_optimization.py`)
     - Material selection (`/tests/unit/core/ai/test_material_selection.py`)
     - Teaching insights (`/tests/unit/core/ai/test_teaching_insights.py`)
     - Cross-course recommendation integration (`/tests/unit/core/ai/test_crosscourse_reco.py`)
2. **Protocol & API Field Documentation:**  
   - Before implementation, draft or extend API protocol docs for each workflow in `/docs/architecture/` (e.g., `ai_recommendation_protocol.md`, etc.)
   - All fields and expected signatures must be defined/documented before use.
3. **Integration Test Planning:**  
   - Create outlines for integration tests in `/tests/integration/ai/` for cross-module and cross-content compatibility.
4. **Live Update of This Plan & Docs:**  
   - As new APIs, modules, or docs arise from Day 25 work, update `/code_summary.md` and `/docs/architecture/architecture_overview.md` promptly to reflect new surfaces/tests.
5. **Hygiene:**  
   - Maintain the environment/import separation and protocol discipline as required by project-wide policy.

**REMINDER:**  
_Do not begin code/logic implementation for any Day 25 feature outside of this TDD/protocol sequence or outside the boundaries of the original plan and its cited docs._
