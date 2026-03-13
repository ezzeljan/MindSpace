"""Streamlit dashboard + backend launcher for MindSpace.

Running this file will:
1) Start the FastAPI backend (on port 8000)
2) Open a simple Streamlit UI to inspect and add entries

Usage:
    streamlit run backend/streamlit_app.py
"""

import threading
import time
from typing import Optional

import requests
import streamlit as st


API_BASE = "http://localhost:8000/api"


def _start_api_server_once() -> None:
    if "api_thread" in st.session_state:
        return

    from uvicorn import run as uvicorn_run

    def run_server():
        uvicorn_run("backend.api:app", host="0.0.0.0", port=8000, log_level="info")

    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    st.session_state.api_thread = thread

    # give it a moment to start so the UI can call it immediately
    time.sleep(1)


def _api_headers():
    headers = {"Content-Type": "application/json"}
    token = st.session_state.get("token")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _fetch(endpoint: str, method: str = "GET", json: Optional[dict] = None):
    url = f"{API_BASE}/{endpoint.lstrip('/')}"
    try:
        if method == "GET":
            res = requests.get(url, headers=_api_headers(), timeout=3)
        else:
            res = requests.post(url, headers=_api_headers(), json=json, timeout=3)

        if res.status_code == 401:
            st.session_state.pop("token", None)
            st.error("Session expired. Please refresh and log in again.")
            return None

        res.raise_for_status()
        return res.json()
    except Exception as e:
        st.error(f"API request failed: {e}")
        return None


def main():
    st.set_page_config(page_title="MindSpace Backend", layout="wide")
    st.title("MindSpace Backend Dashboard")

    _start_api_server_once()

    if "token" not in st.session_state:
        st.session_state.token = None

    if not st.session_state.token:
        st.subheader("Sign in")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Sign in"):
                try:
                    res = requests.post(
                        f"{API_BASE}/auth/login",
                        json={"email": email, "password": password},
                        timeout=3,
                    )
                    res.raise_for_status()
                    st.session_state.token = res.json().get("access_token")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Login failed: {e}")
        with col2:
            if st.button("Register"):
                try:
                    res = requests.post(
                        f"{API_BASE}/auth/register",
                        json={"email": email, "password": password},
                        timeout=3,
                    )
                    res.raise_for_status()
                    st.session_state.token = res.json().get("access_token")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Registration failed: {e}")

        st.stop()

    if st.button("Sign out"):
        st.session_state.token = None
        st.experimental_rerun()

    tabs = st.tabs(["Chat", "Mood", "Reflection"])

    with tabs[0]:
        st.subheader("Chat history")
        history = _fetch("chat/history") or []
        for msg in history:
            style = "background-color:#e9f5ff;" if msg.get("sender") == "assistant" else "background-color:#f3f4f6;"
            st.markdown(f"**{msg.get('sender').capitalize()}**: {msg.get('text')}  \n*{msg.get('timestamp')}*", unsafe_allow_html=True)

        st.write("---")
        with st.form("send_chat"):
            txt = st.text_area("Message to assistant", key="chat_input")
            if st.form_submit_button("Send"):
                if not txt.strip():
                    st.warning("Write a message before sending")
                else:
                    _fetch("chat/message", method="POST", json={"text": txt})
                    st.experimental_rerun()

    with tabs[1]:
        st.subheader("Mood logs")
        moods = _fetch("mood") or []
        for entry in moods:
            st.markdown(f"- **{entry.get('mood')}** — {entry.get('timestamp')}")

        st.write("---")
        with st.form("add_mood"):
            mood = st.text_input("Mood", key="mood_input")
            if st.form_submit_button("Log mood"):
                if mood.strip():
                    _fetch("mood", method="POST", json={"mood": mood})
                    st.experimental_rerun()

    with tabs[2]:
        st.subheader("Reflections")
        reflections = _fetch("reflection") or []
        for r in reflections:
            st.markdown(f"**{r.get('prompt')}**  \n{r.get('text')}  \n*{r.get('timestamp')}*\n---")

        st.write("---")
        with st.form("add_reflection"):
            prompt = st.text_input("Prompt", key="reflection_prompt")
            text = st.text_area("Reflection", key="reflection_text")
            if st.form_submit_button("Save"):
                if prompt.strip() and text.strip():
                    _fetch("reflection", method="POST", json={"prompt": prompt, "text": text})
                    st.experimental_rerun()


if __name__ == "__main__":
    main()
