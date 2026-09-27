from datetime import datetime, timezone

from app.providers.voice_provider import RealtimeCredentials


class DummyVoiceProvider:
    """Fake VoiceProvider returning fixed responses for testing without external API calls."""

    def create_realtime_credentials(self) -> RealtimeCredentials:
        """Return fixed credentials for testing."""
        return RealtimeCredentials(
            client_secret="dummy_client_secret",
            expires_at=datetime(2099, 12, 31, tzinfo=timezone.utc),
            model="gpt-4o-realtime-preview",
        )
