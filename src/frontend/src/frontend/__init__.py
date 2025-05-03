"""
DevOps Study Timer Frontend

A Flask web application for tracking study time for DevOps certifications.
"""

# Import and expose main functions and app
from .main import app, get_sessions, create_session

# Define public API
__all__ = ["app", "get_sessions", "create_session"]
