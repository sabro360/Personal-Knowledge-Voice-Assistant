from datetime import datetime

from pydantic import BaseModel


class RealtimeSessionResponse(BaseModel):
    """API response schema for POST /realtime/session."""

    client_secret: str
    expires_at: datetime
    model: str
