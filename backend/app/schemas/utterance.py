from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.utterance import SpeakerType


class UtteranceCreate(BaseModel):
    """Request schema for creating an Utterance."""

    speaker: SpeakerType
    text: str


class UtteranceResponse(BaseModel):
    """API response schema for an Utterance."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    speaker: SpeakerType
    text: str
    timestamp: datetime
    sequence_number: int
