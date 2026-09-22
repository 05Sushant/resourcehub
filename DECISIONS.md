# Architecture Decisions

This file records important technical and architectural decisions
made during the development of ResourceHub.

---

## ADR-001 — PostgreSQL

### Decision

Use PostgreSQL as the primary database.

### Reason

ResourceHub contains relational data and requires:

- foreign keys
- constraints
- transactions
- indexing
- concurrency control

PostgreSQL is therefore more appropriate for this learning project
than SQLite.

### Status

Accepted

---

## ADR-002 — Django REST Framework

### Decision

Use Django REST Framework for the API.

### Reason

The project is intended to be a backend/API-focused application.
DRF provides serializers, API views, authentication and permission
mechanisms that allow us to focus on backend engineering.

### Status

Accepted

---

## ADR-003 — Celery

### Decision

Use Celery for asynchronous job processing.

### Reason

File processing jobs should not block the HTTP request-response
cycle.

Celery allows jobs to be executed asynchronously by worker processes.

### Status

Accepted

---

## ADR-004 — Redis

### Decision

Use Redis as the initial Celery message broker.

### Reason

Celery requires a mechanism for passing tasks from the Django
application to workers. Redis provides this functionality and is
also useful for learning message queues and in-memory data stores.

### Status

Accepted

---

## ADR-005 — Docker Compose

### Decision

Use Docker Compose for local multi-service development.

### Reason

ResourceHub contains multiple services:

- Django
- PostgreSQL
- Redis
- Celery worker

Docker Compose allows these services to run together with a
consistent development environment.

### Status

Accepted

---

## ADR-006 — Temporal

### Decision

Do not use Temporal in the initial MVP.

### Reason

The initial job-processing requirements are simple asynchronous
tasks. Celery is sufficient for the MVP.

Temporal may be studied later as an alternative for durable,
multi-step workflows.

### Status

Accepted