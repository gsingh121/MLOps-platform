# Enterprise MLOps Platform

A full-stack, end-to-end MLOps platform built to manage machine learning models, govern deployments, and monitor telemetry. This project features a robust async Python backend and a modern Angular frontend, containerized for easy deployment.

## Key Features

* **Model Registry:** Register ML models and track multiple versions, including framework, algorithm, and training data artifacts.
* **Deployment Governance:** Enforce lifecycle stages (Draft -> Approved) before allowing production deployments. 
* **State Management:** Track deployment states (Requested, Deploying, Succeeded, Failed) with simulated workflows.
* **Telemetry & Monitoring:** Capture prediction latency, throughput, error rates, and drift scores for deployed models.
* **Rollback Capabilities:** Safely roll back production deployments to previous states.

## Tech Stack

* **Backend:** FastAPI, Python 3.11, SQLAlchemy (Async), aiosqlite (SQLite), Pytest
* **Frontend:** Angular 17, TypeScript, Tailwind/CSS
* **Infrastructure:** Docker, Docker Compose

---

## Prerequisites

To run this project locally, ensure you have the following installed:
* Python 3.11+
* Node.js 18+
* Docker & Docker Compose
* Git

---

## Quick Start (Docker)

The easiest way to run the entire stack is using Docker Compose.

```bash
# Clone the repository
git clone [https://github.com/gsingh121/MLOps-platform.git](https://github.com/gsingh121/MLOps-platform.git)
cd MLOps-platform

# Build and start the containers
docker-compose up --build
Frontend UI: http://localhost:80

Backend API: http://localhost:8000

API Documentation (Swagger): http://localhost:8000/docs

Local Development Setup
If you prefer to run the services locally without Docker for active development:

1. Backend Setup
Bash
cd backend

# Create and activate a virtual environment
python -m venv venv
# On Windows use: .\venv\Scripts\Activate.ps1
# On Mac/Linux use: source venv/bin/activate 

# Install dependencies
pip install -r requirements.txt

# Run the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
2. Frontend Setup
Open a new terminal window:

Bash
cd frontend

# Install Node modules
npm install

# Start the Angular development server
npx ng serve
Navigate to http://localhost:4200 to view the frontend.

Running Tests
The backend includes a comprehensive test suite covering the full MLOps lifecycle (10 acceptance scenarios).

Bash
cd backend
# Ensure your virtual environment is active
python -m pytest tests/ -v
Architecture Notes
Database: Uses asynchronous SQLite (aiosqlite) for zero-configuration local development.

Idempotency: Deployment endpoints support idempotency keys to prevent duplicate deployments during network retries.

Correlation IDs: The backend middleware automatically injects and logs X-Correlation-ID headers for request tracing.
