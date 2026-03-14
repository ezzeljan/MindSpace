"""MySQL-backed store for MindSpace data using SQLAlchemy."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env for local development
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

import openai
from openai import OpenAI

# Database configuration
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set. Please configure your database connection in .env file.")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(String(50), primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.id"))
    sender = Column(String(50))
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)


class MoodEntry(Base):
    __tablename__ = "mood_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.id"))
    mood = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow)


class Reflection(Base):
    __tablename__ = "reflections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.id"))
    prompt = Column(String(255))
    text = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)


# Create tables
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _next_user_id() -> str:
    import time
    return f"user-{int(time.time() * 1000)}"


# User management
def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            return {"id": user.id, "email": user.email, "hashed_password": user.hashed_password}
        return None
    finally:
        db.close()


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            return {"id": user.id, "email": user.email, "hashed_password": user.hashed_password}
        return None
    finally:
        db.close()


def create_user(email: str, hashed_password: str) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        user_id = _next_user_id()
        user = User(id=user_id, email=email, hashed_password=hashed_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return {"id": user.id, "email": user.email, "hashed_password": user.hashed_password}
    finally:
        db.close()


# Chat messages
def get_chat_history(user_id: str) -> List[Dict[str, Any]]:
    db = SessionLocal()
    try:
        messages = db.query(ChatMessage).filter(ChatMessage.user_id == user_id).order_by(ChatMessage.timestamp).all()
        return [{"id": m.id, "sender": m.sender, "message": m.message, "timestamp": m.timestamp.isoformat() + "Z"} for m in messages]
    finally:
        db.close()


def add_chat_message(user_id: str, sender: str, message: str) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        msg = ChatMessage(user_id=user_id, sender=sender, message=message)
        db.add(msg)
        db.commit()
        db.refresh(msg)
        return {"id": msg.id, "sender": msg.sender, "message": msg.message, "timestamp": msg.timestamp.isoformat() + "Z"}
    finally:
        db.close()


# Mood entries
def get_mood_logs(user_id: str) -> List[Dict[str, Any]]:
    db = SessionLocal()
    try:
        entries = db.query(MoodEntry).filter(MoodEntry.user_id == user_id).order_by(MoodEntry.timestamp).all()
        return [{"id": e.id, "mood": e.mood, "timestamp": e.timestamp.isoformat() + "Z"} for e in entries]
    finally:
        db.close()


def add_mood_log(user_id: str, mood: str) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        entry = MoodEntry(user_id=user_id, mood=mood)
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return {"id": entry.id, "mood": entry.mood, "timestamp": entry.timestamp.isoformat() + "Z"}
    finally:
        db.close()


# Reflections
def get_reflections(user_id: str) -> List[Dict[str, Any]]:
    db = SessionLocal()
    try:
        reflections = db.query(Reflection).filter(Reflection.user_id == user_id).order_by(Reflection.timestamp).all()
        return [{"id": r.id, "prompt": r.prompt, "text": r.text, "timestamp": r.timestamp.isoformat() + "Z"} for r in reflections]
    finally:
        db.close()


def add_reflection(user_id: str, prompt: str, text: str) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        reflection = Reflection(user_id=user_id, prompt=prompt, text=text)
        db.add(reflection)
        db.commit()
        db.refresh(reflection)
        return {"id": reflection.id, "prompt": reflection.prompt, "text": reflection.text, "timestamp": reflection.timestamp.isoformat() + "Z"}
    finally:
        db.close()


def generate_assistant_reply(user_text: str) -> str:
    # 1) Try Gemini API key first (preferred for Gemini model usage)
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    openai_api_key = os.environ.get("OPENAI_API_KEY")

    system_prompt = (
        "You are a supportive emotional wellness assistant in an app called MindSpace. "
        "Your role is to help users reflect on their feelings, encourage self-awareness, and suggest simple coping strategies such as breathing exercises or journaling. "
        "Respond in a calm, respectful, and non-judgmental way. "
        "Do not give medical advice or psychological diagnoses. "
        "If the user expresses serious distress, suggest seeking help from a professional or talking to someone they trust. "
        "Keep responses supportive, empathetic, and reflective."
    )

    fallback_response = (
        f"I hear you said: '{user_text}'. "
        "That sounds meaningful, and I'm here to listen. "
        "Can you tell me more about what you're feeling right now?"
    )

    if not gemini_api_key and not openai_api_key:
        return fallback_response

    # Use Gemini responses API when GEMINI_API_KEY is present
    if gemini_api_key:
        try:
            client = OpenAI(api_key=gemini_api_key)
            response = client.responses.create(
                model="gemini-1.5",
                input={
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_text},
                    ]
                },
                max_output_tokens=300,
            )
            ai_text = response.output_text.strip() if hasattr(response, "output_text") else ""
            if not ai_text:
                # Some client versions return structured output
                ai_text = " ".join([c.text for c in response.output[0].content if hasattr(c, 'text')])
            if ai_text:
                print("[chatbot] Gemini response used")
                return ai_text
            print("[chatbot] Gemini returned empty response")
        except Exception as e:
            print(f"[chatbot] Gemini API failed: {type(e).__name__}: {e}")

    # Fall back to OpenAI ChatCompletion if available
    if openai_api_key:
        try:
            client = OpenAI(api_key=openai_api_key)
            for model in ["gpt-4o-mini", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"]:
                try:
                    response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_text}
                        ],
                        max_tokens=300,
                        temperature=0.7,
                    )
                    ai_text = response.choices[0].message["content"].strip()
                    if ai_text:
                        print(f"[chatbot] OpenAI response used (model={model})")
                        return ai_text
                except Exception as e:
                    print(f"[chatbot] OpenAI model {model} failed: {type(e).__name__}: {e}")
        except Exception as e:
            print(f"[chatbot] OpenAI client init failed: {type(e).__name__}: {e}")

    print("[chatbot] AI calls failed / quota issue, returning fallback")
    return f"I’m sorry, the AI service is temporarily unavailable (quota/usage issue). {fallback_response}"

