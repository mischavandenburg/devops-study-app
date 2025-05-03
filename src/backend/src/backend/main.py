from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from typing import List, Optional

from .models import StudySession, StudySessionCreate, Stats
from .storage import save_session, get_all_sessions, get_sessions_by_tag, get_statistics
from .config import (
    APP_NAME,
    API_HOST,
    API_PORT,
    CORS_ALLOW_ORIGINS,
    CORS_ALLOW_CREDENTIALS,
    CORS_ALLOW_METHODS,
    CORS_ALLOW_HEADERS,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=APP_NAME,
    description="API for tracking study time for DevOps studies",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
)


@app.get("/")
async def root():
    """Root endpoint returning API information"""
    return {"message": "DevOps Study Tracker API"}


@app.get("/health")
async def health():
    """Health endpoint for kubernetes probes"""
    return {"status": "healthy"}


@app.post("/sessions", response_model=StudySession)
async def create_session(session: StudySessionCreate):
    """Create a new study session"""
    logger.info(
        f"Creating new session: {session.minutes} minutes with tag: {session.tag}"
    )
    try:
        new_session = save_session(session)
        return new_session
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")


@app.get("/sessions", response_model=List[StudySession])
async def read_sessions(
    tag: Optional[str] = Query(None, description="Filter sessions by tag"),
):
    """Get all study sessions, optionally filtered by tag"""
    try:
        if tag:
            logger.info(f"Fetching sessions with tag: {tag}")
            return get_sessions_by_tag(tag)
        else:
            logger.info("Fetching all sessions")
            return get_all_sessions()
    except Exception as e:
        logger.error(f"Error fetching sessions: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error fetching sessions: {str(e)}"
        )


@app.get("/stats", response_model=Stats)
async def read_stats():
    """Get aggregated statistics about study sessions"""
    logger.info("Fetching statistics")
    try:
        return get_statistics()
    except Exception as e:
        logger.error(f"Error fetching statistics: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error fetching statistics: {str(e)}"
        )


# Marker for CI pipeline
# This comment is used to trigger the CI pipeline when changes are made to this file.


def main():
    """Entry point for running the API server"""
    logger.info(f"Starting {APP_NAME} API")
    uvicorn.run("backend.main:app", host=API_HOST, port=API_PORT, reload=True)


if __name__ == "__main__":
    main()
