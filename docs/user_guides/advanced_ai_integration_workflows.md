# Advanced AI Integration Testing Workflows

**Location:** `/docs/user_guides/advanced_ai_integration_workflows.md`  
**Project:** AeroLearn AI  
**Last updated:** 2024-06-09

---

## Overview

This guide explains the advanced AI integration testing framework for AeroLearn AI, covering semantic search, content relationship mapping, and external resource discovery. It details test workflows, relevance/scoring metrics, result interpretation, and troubleshooting.

## Table of Contents

1. Introduction
2. Integration Test Matrix
3. Running Integration Tests
4. Interpreting Results & Metrics
5. Customizing/Extending Tests
6. Troubleshooting & FAQ
7. References

---

## 1. Introduction

AeroLearn AI’s advanced AI integration tests ensure seamless operation across content repositories, relationship graphs, and external AI resources. These test suites validate:

- Cross-module feature flows
- Real-world content scenarios
- Strict relevance and scoring criteria
- Robustness under realistic conditions

---

## 2. Integration Test Matrix

| Test File                                               | Scope                              | Key Features Tested                          | Expected Outcome                                 |
|---------------------------------------------------------|------------------------------------|----------------------------------------------|--------------------------------------------------|
| `/tests/integration/test_semantic_search_integration.py` | Hybrid/semantic search (all repos) | Permission filtering, hybrid ranking, dedup. | Relevant, permission-appropriate results         |
| `/tests/integration/test_relationship_mapping_integration.py` | Concept/relationship mapping       | Concept extraction, KG navigation, recs.     | Accurate graph, traceable relationships          |
| `/tests/integration/test_resource_discovery_integration.py` | Ext. resource discovery            | API orchestrator, provider plugin, scoring   | Relevant, quality-assessed external resources    |

---

## 3. Running Integration Tests

1. **Install dependencies**:  
   Follow `/README.md` environment setup if not already done.

2. **To run all integration tests:**  
   ```sh
   pytest tests/integration/
   ```
   Or run specific test:
   ```sh
   pytest tests/integration/test_semantic_search_integration.py
   ```

3. **CI Integration**:  
   Tests are integrated with CI as per `/docs/api/test_ci.md` (see CI configuration for details).

---

## 4. Interpreting Results & Metrics

- **Relevance (semantic search):**
  - Each returned result must match at least one search intent or keyword set.
  - Scores must meet or exceed the customizable threshold.
  - Deduplication and permission checks enforced.

- **Relationship accuracy:**
  - Knowledge graph structures must encode all primary relationships and handle cycles/branches.
  - Unit and integration coverage for navigation and recommendations.

- **Resource discovery:**
  - Each discovered resource is evaluated on content match and external score (e.g., DeepSeek scoring, internal heuristics).
  - Only passing, top-ranked resources included in test pass.

- **Metrics:** Each test outputs relevance/accuracy percentage, plus summary log file in `/tests/reports/` (if enabled).

---

## 5. Customizing or Extending Tests

- **Add new test scenarios:**  
  Copy an existing integration test script and adjust fixtures/inputs.
- **Add new resource provider plugin:**  
  Implement new class in `/app/core/external_resources/` as per provider base class.
- **Tune scoring thresholds:**  
  Adjust parameters in the orchestrator (see `/app/core/ai/resource_discovery.py` or semantic search config).

---

## 6. Troubleshooting & FAQ

- **Tests not found:**  
  Verify all dependency modules and fixtures are present (see `/tests/fixtures/`).

- **Permission errors:**  
  Review test user setup in fixtures; ensure proper role assignments.

- **Low relevance or missing results:**  
  Increase dataset diversity; check content index and vector DB sync.

- **Resource provider failures:**  
  Check network/API credentials for new plugins.

---

## 7. References

- `/docs/development/day13_plan.md`
- `/docs/api/search_api.md`
- `/docs/user_guides/semantic_search.md`
- `/docs/architecture/knowledge_graph.md`
- `/docs/api/resource_discovery_api.md`

---

**For contributors:** When editing or adding new advanced AI test workflows, update this document and reference file locations explicitly in all communications.