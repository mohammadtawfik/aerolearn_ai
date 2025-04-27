# AeroLearn AI — Course Structure & Organization Model

## Overview

This document describes the core data models and their relationships for supporting hierarchical course structures, content categorization (taxonomy), and persistent tagging within the AeroLearn AI system.

---

## Course Structure Model

- **Course**: The top-level entity representing a learning program.
  - Has multiple **Modules** (ordered).
  - May require other Courses as prerequisites.
  - Linked to Categories and Tags.
- **Module**: A logical subdivision of a Course.
  - Subdivided into **Lessons** (ordered).
  - May have prerequisite Modules.
  - Linked to Categories and Tags.
- **Lesson**: Smallest atomic (content) unit, inside Modules.
  - Linked to Categories and Tags.

### Hierarchy

Course  
└── Module(s)  
  └── Lesson(s)  


## Ordering and Constraints

- Each `Course`, `Module`, and `Lesson` includes an `order` field for sequencing within its parent.
- Courses and Modules support many-to-many `prerequisite` relationships.

## Content Categorization System (Taxonomy)

- **Category** is a hierarchical entity (`parent_id` supports arbitrary depth).
- Categories may be assigned to Courses, Modules, or Lessons.

## Tagging System

- **Tag** is a cross-component label for flexible searching/filtering.
- Courses, Modules, and Lessons may be linked to any number of tags.
- Tag dictionary is global and persistent.

---

## Database Model Relationships

- All taxonomy (category) and tag assignments are many-to-many relationships, using junction tables.

---

## Extension Points

- UI: Drag-and-drop course/module/lesson organization.
- Prerequisite management workflow.
- Category assignment multi-select UI.
- Tag autocomplete and search.

---

## See Also

- `app/models/course.py`
- `app/models/category.py`
- `app/models/tag.py`