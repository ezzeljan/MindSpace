# MindSpace

MindSpace is a wellness companion built with React + Vite on the frontend, and an optional Python backend for persisting chat, mood, and reflection data.

## 🚀 Running the frontend

```bash
# from the repo root
npm install
npm run dev
```

The frontend runs on http://localhost:5173 and proxies API requests to `http://localhost:8000/api`.

## 🧠 Running the backend (Python)

The backend is optional but enables persistence of chat history, mood logs, and reflections.

### 1) Create a Python environment

```bash
cd backend
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS / Linux
# source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Start the API server

```bash
uvicorn backend.api:app --reload --port 8000
```

### 4) (Optional) Open the Streamlit admin dashboard

```bash
streamlit run backend/streamlit_app.py
```

The streamlit app will start the backend automatically if it is not already running.

## 🧩 How the frontend uses the backend

- `/api/auth/login` for signing in and obtaining a session token
- `/api/auth/register` for creating a new account
- `/api/chat` for chat messages (requires authentication)
- `/api/mood` for mood logging (requires authentication)
- `/api/reflection` for journaling (requires authentication)

The frontend is configured to proxy `/api/*` to `http://localhost:8000` when running in development mode.
