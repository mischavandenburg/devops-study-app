import pytest
from datetime import datetime
import os
import uuid
import csv

# Import functions and variables from storage.py using new package structure
from backend.storage import (
    save_session,
    get_all_sessions,
    get_sessions_by_tag,
    get_statistics,
)
from backend.models import StudySessionCreate, StudySession

# Import the storage module itself
import backend.storage as storage_module


# Define the path for a temporary test data file using relative paths
TEST_DATA_FILE = os.path.join(os.path.dirname(__file__), "test_storage_sessions.csv")


@pytest.fixture(scope="module", autouse=True)
def setup_test_data_file():
    """Fixture to set up the test data file path for the storage module tests."""
    # Ensure the test data directory exists
    os.makedirs(os.path.dirname(TEST_DATA_FILE), exist_ok=True)

    original_data_file = storage_module.SESSIONS_FILE  # Use alias
    # Override the SESSIONS_FILE path in the storage module for testing
    storage_module.SESSIONS_FILE = TEST_DATA_FILE  # Use alias
    yield
    # Restore the original data file path and clean up
    storage_module.SESSIONS_FILE = original_data_file  # Use alias
    if os.path.exists(TEST_DATA_FILE):
        os.remove(TEST_DATA_FILE)


@pytest.fixture(scope="function", autouse=True)
def reset_test_data():
    """Fixture to reset the test data file before each test function."""
    if os.path.exists(TEST_DATA_FILE):
        os.remove(TEST_DATA_FILE)
    # Create an empty file with headers using CSV
    with open(TEST_DATA_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "timestamp", "minutes", "tag"])
        writer.writeheader()


def test_save_session():
    """Test saving a single session."""
    session_create = StudySessionCreate(minutes=45, tag="Terraform")
    saved_session = save_session(session_create)

    assert isinstance(saved_session, StudySession)
    assert saved_session.minutes == 45
    assert saved_session.tag == "Terraform"
    assert isinstance(saved_session.id, str)  # ID is stored as string in the model
    assert uuid.UUID(saved_session.id)  # Verify it's a valid UUID string
    assert isinstance(saved_session.timestamp, datetime)

    # Verify with CSV reader
    with open(TEST_DATA_FILE, "r", newline="") as f:
        reader = list(csv.DictReader(f))
        assert len(reader) == 1
        assert int(reader[0]["minutes"]) == 45
        assert reader[0]["tag"] == "Terraform"
        assert saved_session.id == reader[0]["id"]  # Compare as strings


def test_save_multiple_sessions():
    """Test saving multiple sessions sequentially."""
    save_session(StudySessionCreate(minutes=30, tag="Docker"))
    save_session(StudySessionCreate(minutes=60, tag="Python"))

    with open(TEST_DATA_FILE, "r", newline="") as f:
        reader = list(csv.DictReader(f))
        assert len(reader) == 2
        assert reader[0]["tag"] == "Docker"
        assert reader[1]["tag"] == "Python"


def test_get_all_sessions():
    """Test retrieving all sessions."""
    save_session(StudySessionCreate(minutes=20, tag="Git"))
    save_session(StudySessionCreate(minutes=40, tag="CI/CD"))

    sessions = get_all_sessions()
    assert len(sessions) == 2
    assert isinstance(sessions[0], StudySession)
    assert sessions[0].tag == "Git"
    assert sessions[1].tag == "CI/CD"


def test_get_all_sessions_empty():
    """Test retrieving all sessions when none exist."""
    sessions = get_all_sessions()
    assert sessions == []


def test_get_sessions_by_tag():
    """Test retrieving sessions filtered by tag."""
    save_session(StudySessionCreate(minutes=25, tag="AWS"))
    save_session(StudySessionCreate(minutes=55, tag="Azure"))
    save_session(StudySessionCreate(minutes=35, tag="AWS"))

    aws_sessions = get_sessions_by_tag("AWS")
    assert len(aws_sessions) == 2
    assert all(s.tag == "AWS" for s in aws_sessions)

    azure_sessions = get_sessions_by_tag("Azure")
    assert len(azure_sessions) == 1
    assert azure_sessions[0].tag == "Azure"

    gcp_sessions = get_sessions_by_tag("GCP")
    assert gcp_sessions == []


def test_get_statistics():
    """Test calculating statistics."""
    save_session(StudySessionCreate(minutes=10, tag="Linux"))
    save_session(StudySessionCreate(minutes=20, tag="Networking"))
    save_session(StudySessionCreate(minutes=30, tag="Linux"))

    stats = get_statistics()
    assert stats.total_sessions == 3
    assert stats.total_time == 60  # 10 + 20 + 30
    # Calculate average manually if needed
    average_minutes = stats.total_time / stats.total_sessions
    assert average_minutes == 20.0
    assert stats.sessions_by_tag == {"Linux": 2, "Networking": 1}


def test_get_statistics_empty():
    """Test calculating statistics when no sessions exist."""
    stats = get_statistics()
    assert stats.total_sessions == 0
    assert stats.total_time == 0
    # Can't calculate average with zero sessions
    assert stats.time_by_tag == {}
    assert stats.sessions_by_tag == {}


def test_create_and_read_sessions():
    """Test creating sessions and then reading them back."""
    # Create test CSV file with two sessions
    with open(TEST_DATA_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "timestamp", "minutes", "tag"])
        writer.writeheader()
        writer.writerow(
            {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "minutes": 15,
                "tag": "TestTag1",
            }
        )
        writer.writerow(
            {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "minutes": 45,
                "tag": "TestTag2",
            }
        )

    # Read sessions
    sessions = get_all_sessions()
    assert len(sessions) == 2
    assert sessions[0].tag == "TestTag1"
    assert sessions[1].minutes == 45


def test_file_not_exists_handling():
    """Test handling when the data file doesn't exist."""
    # Rename the test file temporarily
    if os.path.exists(TEST_DATA_FILE):
        os.rename(TEST_DATA_FILE, f"{TEST_DATA_FILE}.bak")

    try:
        # This should create the data file
        sessions = get_all_sessions()
        assert sessions == []

        # Verify the file was created with headers
        with open(TEST_DATA_FILE, "r", newline="") as f:
            content = f.read()
            assert "id,timestamp,minutes,tag" in content
    finally:
        # Restore the original file if it existed
        if os.path.exists(f"{TEST_DATA_FILE}.bak"):
            if os.path.exists(TEST_DATA_FILE):
                os.remove(TEST_DATA_FILE)
            os.rename(f"{TEST_DATA_FILE}.bak", TEST_DATA_FILE)
