"""
DevOps Study Tracker API

A FastAPI application for tracking study time for DevOps certifications.
"""

from .models import StudySession, StudySessionCreate, Stats
from .storage import save_session, get_all_sessions, get_sessions_by_tag, get_statistics

# Expose main app for ASGI servers
from .main import app

# Define public API
__all__ = [
    "StudySession",
    "StudySessionCreate",
    "Stats",
    "save_session",
    "get_all_sessions",
    "get_sessions_by_tag",
    "get_statistics",
    "app",
]
