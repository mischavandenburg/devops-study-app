import json
import requests
import responses
from conftest import captured_templates
from frontend.main import app


@responses.activate
def test_index_page(client):
    """Test the index route when API returns sessions"""
    # Sample response data that mimics what the backend would return
    sample_sessions = [
        {
            "id": "12345",
            "timestamp": "2025-04-23T10:15:30Z",
            "minutes": 45,
            "tag": "Python",
        },
        {
            "id": "67890",
            "timestamp": "2025-04-22T14:20:00Z",
            "minutes": 30,
            "tag": "AWS",
        },
    ]

    # Mock the API response for sessions
    responses.add(
        responses.GET,
        "http://localhost:22112/sessions",
        json=sample_sessions,
        status=200,
    )

    # Use the captured_templates context manager to verify rendered template
    with captured_templates(app) as templates:
        response = client.get("/")

        # Check the response
        assert response.status_code == 200

        # Check that the correct template was rendered
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == "index.html"

        # Check that sessions were passed to the template with correct formatting
        rendered_sessions = context["sessions"]
        assert len(rendered_sessions) == 2

        # Verify first session data
        assert rendered_sessions[0]["id"] == "12345"
        assert rendered_sessions[0]["minutes"] == 45
        assert rendered_sessions[0]["tag"] == "Python"
        assert rendered_sessions[0]["formatted_date"] == "2025-04-23 10:15"

        # Verify the sessions are sorted by timestamp (newest first)
        assert (
            rendered_sessions[0]["timestamp_obj"]
            > rendered_sessions[1]["timestamp_obj"]
        )


@responses.activate
def test_index_page_api_error(client):
    """Test the index route when API returns an error"""
    # Mock the API response to return an error
    responses.add(
        responses.GET,
        "http://localhost:22112/sessions",
        json={"error": "Internal server error"},
        status=500,
    )

    with captured_templates(app) as templates:
        response = client.get("/")

        # Check the response
        assert response.status_code == 200

        # Check that the correct template was rendered with empty sessions
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == "index.html"
        assert context["sessions"] == []


@responses.activate
def test_add_session_valid(client):
    """Test adding a valid study session"""
    # Mock the API response for creating a session
    responses.add(
        responses.POST,
        "http://localhost:22112/sessions",
        json={
            "id": "abcde",
            "timestamp": "2025-04-24T09:30:00Z",
            "minutes": 60,
            "tag": "Docker",
        },
        status=200,
    )

    # Send a POST request to add a new session
    response = client.post("/add_session", data={"minutes": "60", "tag": "Docker"})

    # Verify redirect to index page
    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    # Verify the API was called with correct payload
    request = responses.calls[0].request
    assert request.body is not None, "Request body should not be None"
    assert json.loads(request.body) == {"minutes": 60, "tag": "Docker"}


def test_add_session_invalid_minutes(client):
    """Test adding a study session with invalid minutes"""
    # Send a POST request with invalid minutes (non-numeric)
    response = client.post("/add_session", data={"minutes": "invalid", "tag": "Docker"})

    # Verify redirect to index page
    assert response.status_code == 302
    assert response.headers["Location"] == "/"


def test_add_session_empty_tag(client):
    """Test adding a study session with empty tag"""
    # Send a POST request with empty tag
    response = client.post("/add_session", data={"minutes": "30", "tag": ""})

    # Verify redirect to index page
    assert response.status_code == 302
    assert response.headers["Location"] == "/"


def test_add_session_zero_minutes(client):
    """Test adding a study session with zero minutes"""
    # Send a POST request with zero minutes
    response = client.post("/add_session", data={"minutes": "0", "tag": "Docker"})

    # Verify redirect to index page
    assert response.status_code == 302
    assert response.headers["Location"] == "/"


@responses.activate
def test_add_session_api_error(client):
    """Test adding a session when API returns an error"""
    # Mock the API to return an error
    responses.add(
        responses.POST,
        "http://localhost:22112/sessions",
        json={"error": "Server error"},
        status=500,
    )

    # Send a POST request to add a new session
    response = client.post("/add_session", data={"minutes": "45", "tag": "Terraform"})

    # Verify redirect to index page despite API error
    assert response.status_code == 302
    assert response.headers["Location"] == "/"


@responses.activate
def test_health_endpoint_api_healthy(client):
    """Test the health endpoint when the API is healthy"""
    # Mock the API health endpoint to return success
    responses.add(
        responses.GET,
        "http://localhost:22112/health",
        json={"status": "healthy"},
        status=200,
    )

    # Send a GET request to the health endpoint
    response = client.get("/health")

    # Verify response
    assert response.status_code == 200
    data = response.json
    assert data["status"] == "healthy"
    assert data["api_connectivity"] is True


@responses.activate
def test_health_endpoint_api_down(client):
    """Test the health endpoint when the API is down"""
    # Mock the API health endpoint to return a connection error
    responses.add(
        responses.GET,
        "http://localhost:22112/health",
        body=requests.RequestException("Connection error"),
    )

    # Send a GET request to the health endpoint
    response = client.get("/health")

    # Verify response - should return 503 when API is down
    assert response.status_code == 503
    data = response.json
    assert data["status"] == "unhealthy"
    assert data["api_connectivity"] is False
