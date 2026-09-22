# ResourceHub — Project Context

## Project Name

ResourceHub

## Project Type

Shared Resource Reservation & Asynchronous Job Processing Platform

## Objective

Build a mid-level backend engineering project to learn and demonstrate:

- Django
- Django REST Framework
- PostgreSQL
- Test-Driven Development
- Docker
- Docker Compose
- Git
- Computer Networks
- Operating System concepts
- Celery
- Redis
- Backend engineering principles

## Project Description

ResourceHub is a backend platform where users can:

- authenticate
- view shared processing resources
- reserve resources for a specific time period
- submit asynchronous processing jobs
- upload input files
- track job status
- retrieve processing results

The resources are logical/shared processing resources.
The project does NOT attempt to replicate any proprietary system.

## Core Architecture

Client
  ↓ HTTP
Django + Django REST Framework
  ↓
PostgreSQL

Django
  ↓
Redis
  ↓
Celery Worker
  ↓
Job Processing
  ↓
Filesystem

## Core Entities

- User
- Resource
- Reservation
- Job
- JobFile
- Result

## Core Features

### Authentication
- User registration
- Login
- Authentication
- Authorization

### Resources
- Create resource
- List resources
- View resource
- Update resource
- Enable/disable resource

### Reservations
- Create reservation
- Check availability
- Detect overlapping reservations
- Cancel reservation
- Prevent conflicting reservations

### Jobs
- Create job
- Upload input file
- Queue job
- Process asynchronously
- Track job status
- Store result

### Testing
- Unit tests
- API tests
- Integration tests
- TDD workflow

### Infrastructure
- PostgreSQL
- Redis
- Celery
- Docker
- Docker Compose

## Learning Priorities

1. Understand the code before implementing it.
2. Understand Django and DRF internals at a practical level.
3. Understand PostgreSQL and database transactions.
4. Understand concurrency and race conditions.
5. Understand HTTP and client-server communication.
6. Understand filesystem I/O and OS concepts.
7. Understand asynchronous job processing.
8. Practice TDD.
9. Practice Git workflow.
10. Keep the architecture simple enough to explain line-by-line.

## MVP

The initial version will include:

- Authentication
- Resource management
- Resource reservations
- Reservation conflict detection
- Job creation
- File upload
- Celery job processing
- Job status
- Result retrieval
- PostgreSQL
- Redis
- Docker Compose
- pytest
- Git

## Explicitly Out of Scope

- Kubernetes
- Microservices
- Kafka
- Temporal
- WebSockets
- Real cloud resource provisioning
- Real GPU scheduling
- Complex frontend
- Production cloud deployment

These may be considered later only if the core project is complete.

## Development Principle

Every technology used in the project must have a clear reason for being present.

Avoid adding technologies only to make the project appear more complex.