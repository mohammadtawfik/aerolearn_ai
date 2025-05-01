<!--
File Location: /docs/api/week2_api.md
Do not relocate. Task 14.5 Week 2 Docs.
-->

# AeroLearn AI Week 2 API Documentation

## Overview

API endpoints updated or added in Week 2 for content management, storage integration, batch upload, and admin features.

---

## Endpoints

### Content Management

- `POST /api/content/upload`  
  Upload new content in bulk.

- `GET /api/content/search`  
  Query/search content with AI and keyword filters.

### Admin

- `POST /api/admin/user/role`  
  Edit a user’s role or permissions.

### Batch

- `POST /api/batch/start`  
  Begin a batch upload.

- `GET /api/batch/status`  
  Monitor batch progress.

### Monitoring

- `GET /api/integrations/health`  
  Check status/metrics of all system integrations.

---

## Models

- Content, User, Batch, HealthStatus, etc. (link to models)

---

## Authentication

- All endpoints require bearer token/session.

---

## Change Log

| Version | Change                                            |
|---------|--------------------------------------------------|
| 2.0     | Week 2: Added batch endpoints, admin role PATCH.  |

---