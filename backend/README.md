# MindSpace Backend

This folder contains a simple backend for the MindSpace frontend.

## What it includes

- **FastAPI** endpoints that store user inputs (chat history, moods, reflections) in a local JSON file.
- A **Streamlit dashboard** (`streamlit_app.py`) that launches the backend and provides a quick admin UI.

## Getting started

### 1) Create a Python environment

```bash
cd backend
python -m venv .venv
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# macOS / Linux
# source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Run the backend API

```bash
uvicorn backend.api:app --reload --port 8000
```

The frontend expects the API to be available at `http://localhost:8000/api`.

### 4) (Optional) Open the Streamlit admin dashboard

```bash
streamlit run backend/streamlit_app.py
```

This will automatically start the backend server (if not already running) and provide a simple UI to inspect and add entries.
