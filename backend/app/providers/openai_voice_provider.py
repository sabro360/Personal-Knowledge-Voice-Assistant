from datetime import datetime, timezone

from openai import APIError, OpenAI

from app.providers.errors import VoiceProviderError
from app.providers.voice_provider import RealtimeCredentials


class OpenAIVoiceProvider:
    """VoiceProvider implementation using the OpenAI Realtime API."""

    _REALTIME_MODEL = "gpt-realtime-2.1"

    def __init__(self, api_key: str) -> None:
        """Initialize with an OpenAI API key."""
        self._client = OpenAI(api_key=api_key)

    def create_realtime_credentials(self) -> RealtimeCredentials:
        """Create ephemeral credentials for a Realtime API session via OpenAI."""
        try:
            result = self._client.realtime.client_secrets.create(
                session={"type": "realtime", "model": self._REALTIME_MODEL}
            )
        except APIError as exc:
            raise VoiceProviderError(f"OpenAI Realtime API error: {exc}") from exc
        return RealtimeCredentials(
            client_secret=result.value,
            expires_at=datetime.fromtimestamp(result.expires_at, tz=timezone.utc),
            model=result.session.model,
        )
