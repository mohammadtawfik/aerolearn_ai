# Admin User Workflows: Usage Scenarios & QA/Integration Test Guide

**Location:** `/docs/user_guides/admin_workflows.md`  
*(As per Day 11 completion plan)*

---

## Overview

This document provides:
- End-to-end scenarios for admin operations (user management, course management, system config, monitoring).
- Mapping to integration tests and expected results.
- Instructions for manual QA verification and reviewer sign-off.

---

## 1. User Management Workflow

**Tested in:** `/tests/integration/test_admin_integration.py`, `/scripts/admin_interface_selftest.py`

**Steps:**
1. Log in as an admin (use demo/test account if available).
2. Create a new user and assign them a role.
3. Edit user info and view activity logs.
4. Attempt permission-restricted actions as user/test.

**Expected outcome:**  
- User appears in admin dashboard, roles are updated, and logs are visible.

---

## 2. Course Management/Content Linkage Workflow

**Tested in:** `/tests/integration/test_admin_integration.py`, `/scripts/admin_interface_selftest.py`

**Steps:**
1. Create a course, assign instructor, enroll users.
2. Archive and restore the course.
3. Check associated content persists and access changes match status.
4. Test bulk enrollment/archiving for regression.

**Expected outcome:**  
- Course states change as expected, with correct propagation to content.

---

## 3. System Configuration Propagation Workflow

**Tested in:** `/tests/integration/test_admin_integration.py`, `/scripts/admin_interface_selftest.py`

**Steps:**
1. Change a global/system setting (e.g., enable maintenance mode).
2. Validate the configuration takes effect (UI banner, API response, etc.).
3. Reset config after test.

**Expected outcome:**  
- System components react to config changes as specified.

---

## 4. Monitoring/Alert Workflow

**Tested in:** `/tests/integration/test_admin_integration.py`, `/scripts/admin_interface_selftest.py`

**Steps:**
1. Simulate increased workload (increase active users, app load).
2. Observe metric changes and alert thresholds triggering.
3. Review dashboard or logs for event traces.

**Expected outcome:**  
- System health/alerting responds and logs accurately.

---

## 5. Reviewer Checklist

- [X] All automated tests from `/tests/integration/test_admin_integration.py` pass
- [X] Self-test script `/scripts/admin_interface_selftest.py` passes
- [X] Manual workflows performed and validated
- [X] Results entered in `/docs/development/day11_done_criteria.md`
- [X] All documentation and workflow notes finalized

---

**Integration Test Run Note:**
> _As of 2024-06-10, all admin integration, workflow, and monitoring tests have passed on a full clean run. This confirms cross-component admin interface correctness and readiness for sprint close._

_Last updated: [2024-06-10] — All Task 11.5 scenarios and integration requirements verified and complete._
