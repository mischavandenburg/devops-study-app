import pytest
import pytest_asyncio
from httpx import AsyncClient
import os
import csv
from unittest import mock

# Import the FastAPI app and models from the proper package path
from backend.main import app
from backend.models import StudySessionCreate
from backend.storage import save_session

# Import the storage module itself
import backend.storage as storage_module

# Define the path for a temporary test data file using relative paths
TEST_DATA_FILE = os.path.join(os.path.dirname(__file__), "test_sessions.csv")


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Fixture to set up the test environment before any tests run."""
    # Ensure the test data directory exists
    os.makedirs(os.path.dirname(TEST_DATA_FILE), exist_ok=True)

    # Ensure the test data file does not exist before tests
    if os.path.exists(TEST_DATA_FILE):
        os.remove(TEST_DATA_FILE)
    # Override the SESSIONS_FILE path in the storage module for testing
    storage_module.SESSIONS_FILE = TEST_DATA_FILE  # Use the imported module alias
    yield
    # Clean up the test data file after all tests run
    if os.path.exists(TEST_DATA_FILE):
        os.remove(TEST_DATA_FILE)


@pytest_asyncio.fixture(scope="function")
async def client():
    """Provides an async test client for the FastAPI app."""
    # Use ASGITransport instead of direct app parameter - newer httpx client syntax
    from httpx import ASGITransport

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="function", autouse=True)
def reset_test_data():
    """Fixture to reset the test data file before each test function."""
    if os.path.exists(TEST_DATA_FILE):
        os.remove(TEST_DATA_FILE)

    # Create an empty file with headers using CSV, similar to how the main app does it
    with open(TEST_DATA_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "timestamp", "minutes", "tag"])
        writer.writeheader()


@pytest.mark.asyncio
async def test_root(client: AsyncClient):
    """Test the root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "DevOps Study Tracker API"}


@pytest.mark.asyncio
async def test_create_session(client: AsyncClient):
    """Test creating a new study session."""
    session_data = {"minutes": 30, "tag": "AWS"}
    response = await client.post("/sessions", json=session_data)
    assert response.status_code == 200
    data = response.json()
    assert data["minutes"] == 30
    assert data["tag"] == "AWS"
    assert "id" in data
    assert "timestamp" in data

    # Verify data was saved using CSV
    with open(TEST_DATA_FILE, "r", newline="") as f:
        reader = list(csv.DictReader(f))
        assert len(reader) == 1
        assert int(reader[0]["minutes"]) == 30
        assert reader[0]["tag"] == "AWS"


@pytest.mark.asyncio
async def test_read_sessions_empty(client: AsyncClient):
    """Test reading sessions when none exist."""
    response = await client.get("/sessions")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_read_sessions_all(client: AsyncClient):
    """Test reading all sessions."""
    # Create some sessions first using the storage function directly for setup
    save_session(
        StudySessionCreate(minutes=25, tag="Kubernetes")
    )  # Use imported save_session
    save_session(StudySessionCreate(minutes=50, tag="AWS"))  # Use imported save_session

    response = await client.get("/sessions")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["tag"] == "Kubernetes"
    assert data[1]["tag"] == "AWS"


@pytest.mark.asyncio
async def test_read_sessions_by_tag(client: AsyncClient):
    """Test reading sessions filtered by tag."""
    save_session(
        StudySessionCreate(minutes=25, tag="Kubernetes")
    )  # Use imported save_session
    save_session(StudySessionCreate(minutes=50, tag="AWS"))  # Use imported save_session
    save_session(
        StudySessionCreate(minutes=15, tag="Kubernetes")
    )  # Use imported save_session

    response = await client.get("/sessions?tag=Kubernetes")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(item["tag"] == "Kubernetes" for item in data)

    response = await client.get("/sessions?tag=AWS")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["tag"] == "AWS"

    response = await client.get("/sessions?tag=NonExistent")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_read_stats(client: AsyncClient):
    """Test reading statistics."""
    save_session(
        StudySessionCreate(minutes=25, tag="Kubernetes")
    )  # Use imported save_session
    save_session(StudySessionCreate(minutes=50, tag="AWS"))  # Use imported save_session
    save_session(
        StudySessionCreate(minutes=15, tag="Kubernetes")
    )  # Use imported save_session

    response = await client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_sessions"] == 3
    assert data["total_time"] == 90  # 25 + 50 + 15
    assert "time_by_tag" in data
    assert data["sessions_by_tag"]["Kubernetes"] == 2
    assert data["sessions_by_tag"]["AWS"] == 1


@pytest.mark.asyncio
async def test_read_stats_empty(client: AsyncClient):
    """Test reading statistics when no sessions exist."""
    response = await client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_sessions"] == 0
    assert data["total_time"] == 0
    assert data["time_by_tag"] == {}
    assert data["sessions_by_tag"] == {}


@pytest.mark.asyncio
async def test_error_handling_create_session(client: AsyncClient, monkeypatch):
    """Test error handling in create_session endpoint."""

    # Mock save_session to raise an exception
    def mock_save_session(*args, **kwargs):
        raise Exception("Test error")

    monkeypatch.setattr("backend.main.save_session", mock_save_session)

    session_data = {"minutes": 30, "tag": "AWS"}
    response = await client.post("/sessions", json=session_data)
    assert response.status_code == 500
    assert "Error creating session" in response.json()["detail"]


@pytest.mark.asyncio
async def test_error_handling_read_sessions(client: AsyncClient, monkeypatch):
    """Test error handling in read_sessions endpoint."""

    # Mock get_all_sessions to raise an exception
    def mock_get_all_sessions(*args, **kwargs):
        raise Exception("Test error")

    monkeypatch.setattr("backend.main.get_all_sessions", mock_get_all_sessions)

    response = await client.get("/sessions")
    assert response.status_code == 500
    assert "Error fetching sessions" in response.json()["detail"]


@pytest.mark.asyncio
async def test_error_handling_read_sessions_by_tag(client: AsyncClient, monkeypatch):
    """Test error handling in read_sessions endpoint with tag filter."""

    # Mock get_sessions_by_tag to raise an exception
    def mock_get_sessions_by_tag(*args, **kwargs):
        raise Exception("Test error")

    monkeypatch.setattr("backend.main.get_sessions_by_tag", mock_get_sessions_by_tag)

    response = await client.get("/sessions?tag=AWS")
    assert response.status_code == 500
    assert "Error fetching sessions" in response.json()["detail"]


@pytest.mark.asyncio
async def test_error_handling_read_stats(client: AsyncClient, monkeypatch):
    """Test error handling in read_stats endpoint."""

    # Mock get_statistics to raise an exception
    def mock_get_statistics(*args, **kwargs):
        raise Exception("Test error")

    monkeypatch.setattr("backend.main.get_statistics", mock_get_statistics)

    response = await client.get("/stats")
    assert response.status_code == 500
    assert "Error fetching statistics" in response.json()["detail"]


# Test for the main function
def test_main_function(monkeypatch):
    """Test the main() function that starts the uvicorn server."""
    # Mock uvicorn.run to prevent actually starting the server
    mock_run = mock.Mock()
    monkeypatch.setattr("uvicorn.run", mock_run)

    # Call the main function
    from backend.main import main

    main()

    # Check that uvicorn.run was called with the expected arguments
    mock_run.assert_called_once_with(
        "backend.main:app", host="0.0.0.0", port=22112, reload=True
    )
