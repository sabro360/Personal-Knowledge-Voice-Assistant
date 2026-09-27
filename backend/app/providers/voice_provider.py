from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass
class RealtimeCredentials:
    """Short-lived credentials for establishing a Realtime API connection."""

    client_secret: str
    expires_at: datetime
    model: str


class VoiceProvider(Protocol):
    """Protocol for creating ephemeral Realtime API credentials."""

    def create_realtime_credentials(self) -> RealtimeCredentials:
        """Create ephemeral credentials for a Realtime API session."""
        ...
