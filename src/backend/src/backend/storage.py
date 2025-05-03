import csv
import os
import uuid
from datetime import datetime
from typing import List, Dict
import logging

from .models import StudySession, StudySessionCreate, Stats
from .config import DATA_DIR

# Configure logging
logger = logging.getLogger(__name__)

# Constants
SESSIONS_FILE = os.path.join(DATA_DIR, "sessions.csv")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# CSV headers
CSV_HEADERS = ["id", "timestamp", "minutes", "tag"]


def _create_csv_if_not_exists():
    """Create the CSV file with headers if it doesn't exist"""
    if not os.path.exists(SESSIONS_FILE):
        logger.info(f"Creating new sessions CSV file at {SESSIONS_FILE}")
        with open(SESSIONS_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()


def save_session(session: StudySessionCreate) -> StudySession:
    """Save a new study session to the CSV file"""
    _create_csv_if_not_exists()

    # Create a complete StudySession with generated fields
    new_session = StudySession(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(),
        minutes=session.minutes,
        tag=session.tag,
    )

    # Append to CSV file
    with open(SESSIONS_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writerow(
            {
                "id": new_session.id,
                "timestamp": new_session.timestamp.isoformat(),
                "minutes": new_session.minutes,
                "tag": new_session.tag,
            }
        )

    logger.info(f"Saved new session with ID {new_session.id}")
    return new_session


def get_all_sessions() -> List[StudySession]:
    """Retrieve all study sessions from the CSV file"""
    _create_csv_if_not_exists()
    sessions = []

    with open(SESSIONS_FILE, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sessions.append(
                StudySession(
                    id=row["id"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    minutes=int(row["minutes"]),
                    tag=row["tag"],
                )
            )

    logger.info(f"Retrieved {len(sessions)} sessions")
    return sessions


def get_sessions_by_tag(tag: str) -> List[StudySession]:
    """Retrieve study sessions filtered by tag"""
    all_sessions = get_all_sessions()
    filtered_sessions = [
        session for session in all_sessions if session.tag.lower() == tag.lower()
    ]
    logger.info(f"Retrieved {len(filtered_sessions)} sessions with tag '{tag}'")
    return filtered_sessions


def get_statistics() -> Stats:
    """Calculate aggregated statistics from all sessions"""
    sessions = get_all_sessions()

    # Calculate total minutes
    total_minutes = sum(session.minutes for session in sessions)

    # Calculate minutes by tag
    time_by_tag: Dict[str, int] = {}
    sessions_by_tag: Dict[str, int] = {}

    for session in sessions:
        tag = session.tag
        if tag not in time_by_tag:
            time_by_tag[tag] = 0
            sessions_by_tag[tag] = 0

        time_by_tag[tag] += session.minutes
        sessions_by_tag[tag] += 1

    stats = Stats(
        total_time=total_minutes,
        time_by_tag=time_by_tag,
        total_sessions=len(sessions),
        sessions_by_tag=sessions_by_tag,
    )

    logger.info(
        f"Calculated statistics: {total_minutes} minutes across {len(sessions)} sessions"
    )
    return stats
