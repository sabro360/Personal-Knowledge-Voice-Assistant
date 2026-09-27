from datetime import datetime

from app.providers.dummy_voice_provider import DummyVoiceProvider


def test_create_realtime_credentials_returns_credentials() -> None:
    """create_realtime_credentials() should return a RealtimeCredentials with fixed values."""
    provider = DummyVoiceProvider()
    creds = provider.create_realtime_credentials()
    assert isinstance(creds.client_secret, str)
    assert creds.client_secret == "dummy_client_secret"
    assert isinstance(creds.expires_at, datetime)
    assert creds.model == "gpt-4o-realtime-preview"
