from datetime import datetime, timezone

from openai import APIError, OpenAI

from app.providers.errors import VoiceProviderError
from app.providers.voice_provider import RealtimeCredentials


class OpenAIVoiceProvider:
    """VoiceProvider implementation using the OpenAI Realtime API."""

    _REALTIME_MODEL = "gpt-4o-realtime-preview"

    def __init__(self, api_key: str) -> None:
        """Initialize with an OpenAI API key."""
        self._client = OpenAI(api_key=api_key)

    def create_realtime_credentials(self) -> RealtimeCredentials:
        """Create ephemeral credentials for a Realtime API session via OpenAI."""
        try:
            session = self._client.beta.realtime.sessions.create(
                model=self._REALTIME_MODEL
            )
        except APIError as exc:
            raise VoiceProviderError(f"OpenAI Realtime API error: {exc}") from exc
        return RealtimeCredentials(
            client_secret=session.client_secret.value,
            expires_at=datetime.fromtimestamp(
                session.client_secret.expires_at, tz=timezone.utc
            ),
            model=session.model,
        )
