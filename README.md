# ResourceHub

ResourceHub is a backend-focused **shared resource and asynchronous job processing platform** built with Django and Django REST Framework.

The project provides a system where users can submit processing jobs to different types of shared resources. Jobs are processed asynchronously using **Celery and Redis**, while **PostgreSQL** stores the application and job state.

The current implementation supports CSV analytics and image processing operations through a React frontend and Django REST API.

---

## Features

* JWT-based authentication
* Resource management
* Job creation and tracking
* Asynchronous job processing with Celery
* Redis message broker
* PostgreSQL database
* File upload and result storage
* CSV processing

  * CSV Profile
  * CSV Analysis
  * CSV Validation
* Image processing

  * Image Resize
  * Image Grayscale
* Job status tracking
* Result file generation
* Frontend job monitoring and result visualization
* Automated backend tests

---

## Architecture

```text
                         React Frontend
                               |
                               v
                       Django REST API
                               |
                 +-------------+-------------+
                 |                           |
                 v                           v
            PostgreSQL                    Redis
                 |                           |
                 |                           v
                 |                    Celery Worker
                 |                           |
                 |                           v
                 |                    Job Processing
                 |                           |
                 +---------------------------+
                             |
                             v
                         File Storage
```

### Processing Flow

```text
User
 |
 | Create Job
 v
Django REST API
 |
 | Create Job record
 v
PostgreSQL
 |
 | Submit Celery task
 v
Redis
 |
 | Task consumed
 v
Celery Worker
 |
 | Execute operation
 v
Processor
 |
 | Save result
 v
Job Result
 |
 v
Frontend
```

---

## Supported Resources and Operations

| Resource Type    | Operation | Input              | Output |
| ---------------- | --------- | ------------------ | ------ |
| CSV Analytics    | Profile   | CSV                | JSON   |
| CSV Analytics    | Analyze   | CSV                | JSON   |
| CSV Analytics    | Validate  | CSV + schema       | JSON   |
| Image Processing | Resize    | Image + dimensions | PNG    |
| Image Processing | Grayscale | Image              | PNG    |

---

# CSV Processing

## 1. CSV Profile

The Profile operation provides a structural overview of a CSV dataset.

For each column, it reports:

* Column name
* Inferred type
* Missing values
* Unknown values
* Number of unique values

Example:

```json
{
  "rows": 100,
  "columns": 4,
  "columns_info": [
    {
      "name": "age",
      "type": "integer",
      "missing": 2,
      "unknown": 1,
      "unique": 45
    }
  ]
}
```

### Type Inference

The processor supports:

* `integer`
* `float`
* `string`

Numeric type inference is based on non-missing values.

If more than 50% of the non-missing values are numeric, the column is treated as numeric.

Invalid values in a numeric column are counted as `unknown`.

---

## 2. CSV Analyze

The Analyze operation extends CSV profiling with numeric statistics.

For numeric columns it calculates:

* Minimum
* Maximum
* Mean

Example:

```json
{
  "name": "age",
  "type": "integer",
  "missing": 0,
  "unknown": 1,
  "unique": 25,
  "statistics": {
    "min": 18,
    "max": 65,
    "mean": 32.5
  }
}
```

Unknown values are excluded from numeric statistics.

---

## 3. CSV Validate

The Validate operation checks whether a CSV matches a user-defined schema.

Example schema:

```json
{
  "columns": {
    "name": "string",
    "age": "integer",
    "salary": "float"
  }
}
```

The validation checks:

* Expected columns are present
* Unexpected columns are rejected
* Values match their expected types
* Required numeric values are present
* Integer values do not contain decimals

Validation errors include:

* Column
* CSV row
* Error message

Example:

```json
{
  "valid": false,
  "errors": [
    {
      "column": "age",
      "row": 3,
      "message": "Expected integer."
    }
  ]
}
```

---

# Image Processing

## 4. Image Resize

The Resize operation accepts an image and target dimensions.

Example parameters:

```json
{
  "width": 800,
  "height": 600
}
```

The processed image is returned as a PNG file.

The operation validates that:

* Width is an integer
* Height is an integer
* Both dimensions are greater than zero

---

## 5. Image Grayscale

The Grayscale operation converts an image to grayscale using Pillow.

The resulting image:

* Is stored as PNG
* Preserves the original dimensions
* Uses grayscale mode (`L`)

Invalid image files are rejected during processing.

---

# Backend

The backend is implemented using:

* **Python**
* **Django**
* **Django REST Framework**
* **PostgreSQL**
* **Celery**
* **Redis**
* **Pandas**
* **Pillow**
* **Pydantic**
* **SimpleJWT**

### Backend responsibilities

The Django backend handles:

* Authentication
* Resource management
* Job creation
* Parameter validation
* File uploads
* Job status
* API responses
* Result file access

Celery handles the asynchronous execution of processing jobs.

---

# Frontend

The frontend is built with:

* **React**
* **TypeScript**
* **Vite**

The frontend currently provides:

* Resource selection
* Operation selection
* File upload
* Operation-specific parameters
* CSV validation schema configuration
* Job creation
* Job listing
* Job status monitoring
* Job details
* Result visualization
* Result file downloads

---

# Job Lifecycle

Each processing job follows this lifecycle:

```text
PENDING
   |
   v
RUNNING
   |
   +---------> COMPLETED
   |
   +---------> FAILED
```

### PENDING

The job has been created and is waiting for processing.

### RUNNING

A Celery worker has started processing the job.

### COMPLETED

The operation finished successfully and a result is available.

### FAILED

An error occurred during processing. The error message is stored with the job.

---

# Project Structure

```text
Resource_sharing_platform/
│
├── core/
│   ├── migrations/
│   ├── tests/
│   │   └── test_processors.py
│   │
│   ├── models.py
│   ├── operations.py
│   ├── processors.py
│   ├── schemas.py
│   ├── serializers.py
│   ├── services.py
│   ├── tasks.py
│   ├── urls.py
│   └── views.py
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── CreateJob.tsx
│   │   │   ├── JobDetails.tsx
│   │   │   └── Jobs.tsx
│   │   └── ...
│   └── ...
│
├── resourcehub/
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   └── ...
│
├── media/
│   └── jobs/
│       ├── input/
│       └── results/
│
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

# Local Development

## Prerequisites

Install the following:

* Python 3.11+
* PostgreSQL
* Docker Desktop
* Node.js and npm
* Git

Redis can be run through Docker.

---

## 1. Clone the Repository

```bash
git clone https://github.com/05Sushant/resourcehub.git
cd resourcehub
```

---

## 2. Create a Python Virtual Environment

```powershell
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

---

## 3. Install Backend Dependencies

```powershell
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file in the project root.

Example:

```env
SECRET_KEY=your-secret-key
DEBUG=True

DB_NAME=resourcehub
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

Do not commit `.env` to Git.

---

## 5. Run Database Migrations

```powershell
python manage.py migrate
```

---

## 6. Start Redis

Redis can be started using Docker:

```powershell
docker run -d --name resourcehub-redis -p 6379:6379 redis:latest
```

Check that the container is running:

```powershell
docker ps
```

---

## 7. Start the Django Server

```powershell
python manage.py runserver
```

The backend will normally be available at:

```text
http://127.0.0.1:8000/
```

---

## 8. Start the Celery Worker

Open another terminal, activate the virtual environment, and run:

```powershell
celery -A resourcehub worker --loglevel=info --pool=solo
```

The Celery worker is responsible for processing submitted jobs asynchronously.

---

# Frontend Setup

Open another terminal:

```powershell
cd frontend
```

Install dependencies:

```powershell
npm install
```

Start the development server:

```powershell
npm run dev
```

The frontend will normally be available at the URL shown by Vite.

---

# API

The backend exposes REST APIs for authentication, resources, and jobs.

### Authentication

JWT authentication is implemented using Django REST Framework SimpleJWT.

Typical endpoints include:

```text
/api/token/
/api/token/refresh/
```

### Jobs

```text
GET  /api/jobs/
POST /api/jobs/
GET  /api/jobs/<id>/
```

A job submission contains:

* Resource
* Operation
* Parameters
* Input file

The API creates the job and submits it to Celery for asynchronous processing.

---

# Testing

The project uses Django's testing framework for backend tests.

Run the complete core test suite:

```powershell
python manage.py test core
```

The test suite covers areas including:

* CSV profiling
* CSV analysis
* CSV validation
* Image resizing
* Image grayscale conversion
* Operation dispatching
* Parameter validation
* Job processing
* API behavior
* Authentication-related behavior
* Error handling

---

# Asynchronous Processing

ResourceHub uses **Celery** for asynchronous job processing.

The flow is:

```text
Django
  |
  | process_job.delay(job_id)
  v
Redis
  |
  | task
  v
Celery Worker
  |
  v
Processor
```

Only the job ID is passed to the Celery task.

The worker retrieves the corresponding job from PostgreSQL and processes the input file.

PostgreSQL remains the source of truth for job state.

---

# File Processing

Uploaded files are stored under:

```text
media/jobs/input/
```

Generated result files are stored under:

```text
media/jobs/results/
```

Different operations produce different result types:

```text
CSV operations
      ↓
   JSON result

Image operations
      ↓
   PNG result
```

---

# Development Principles

The project focuses on learning and applying backend engineering concepts including:

* REST API design
* Database modeling
* PostgreSQL
* Transactions
* Authentication
* File handling
* Asynchronous processing
* Message brokers
* Background workers
* Automated testing
* Separation of concerns
* API-to-worker architecture

The system is intentionally designed as a modular monolithic application rather than introducing unnecessary microservices.

---

# Future Improvements

Planned improvements may include:

* Docker Compose for the complete application stack
* Improved job cancellation
* Job deletion
* Better frontend result visualization
* More processing operations
* Improved error handling
* Production deployment
* More comprehensive integration tests
* Resource capacity and scheduling improvements

---

# Project Status

ResourceHub is currently under active development.

The current milestone focuses on:

* Django backend
* PostgreSQL persistence
* JWT authentication
* Redis
* Celery asynchronous processing
* CSV processing
* Image processing
* React frontend
* Automated testing

---

## Author

**Sushant Sharma**

Computer Engineering Student

GitHub: [05Sushant](https://github.com/05Sushant)
