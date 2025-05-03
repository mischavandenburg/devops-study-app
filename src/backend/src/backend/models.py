from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict


class StudySessionCreate(BaseModel):
    """Model for creating a new study session"""

    minutes: int = Field(..., gt=0, description="Study duration in minutes")
    tag: str = Field(
        ...,
        min_length=1,
        description="Tag for the study session (e.g., certification name, topic)",
    )


class StudySession(StudySessionCreate):
    """Complete study session model including generated fields"""

    id: str = Field(..., description="Unique identifier for the session")
    timestamp: datetime = Field(
        ..., description="Timestamp of when the session was created"
    )


class Stats(BaseModel):
    """Model for aggregated statistics"""

    total_time: int = Field(..., description="Total study time in minutes")
    time_by_tag: Dict[str, int] = Field(..., description="Study time grouped by tag")
    total_sessions: int = Field(..., description="Total number of study sessions")
    sessions_by_tag: Dict[str, int] = Field(
        ..., description="Number of sessions grouped by tag"
    )
