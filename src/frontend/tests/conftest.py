import pytest
from flask import template_rendered
from contextlib import contextmanager
from frontend.main import app


@contextmanager
def captured_templates(app):
    """Context manager to track templates rendered by the Flask app.
    Allows test to assert on which templates were rendered and their contexts.
    """
    recorded = []

    def record(sender, template, context, **kwargs):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


@pytest.fixture
def client():
    """Test client for the Flask application"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
