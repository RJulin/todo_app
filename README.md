# Next.js + FastAPI Template

A minimal template project with Next.js frontend and Python FastAPI backend.

## Project Structure

```
├── frontend/          # Next.js application
├── backend/           # FastAPI application
└── README.md          # This file
```

## Quick Start

### Backend (FastAPI)

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

API will be available at `http://localhost:8000`

### Frontend (Next.js)

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run development server:
   ```bash
   npm run dev
   ```

Frontend will be available at `http://localhost:3000`

## Features

- **Backend**: FastAPI with basic health check endpoint
- **Frontend**: Next.js with simple landing page
- **CORS**: Configured for local development
- **Hot Reload**: Both frontend and backend support hot reloading 