from datetime import datetime, timezone

from app.providers.errors import VoiceProviderError
from app.providers.voice_provider import RealtimeCredentials
from app.schemas.realtime import RealtimeSessionResponse


def test_realtime_credentials_fields() -> None:
    """RealtimeCredentials should store all fields correctly."""
    creds = RealtimeCredentials(
        client_secret="ek_test",
        expires_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        model="gpt-4o-realtime-preview",
    )
    assert creds.client_secret == "ek_test"
    assert creds.model == "gpt-4o-realtime-preview"
    assert creds.expires_at == datetime(2024, 1, 1, tzinfo=timezone.utc)


def test_realtime_session_response_fields() -> None:
    """RealtimeSessionResponse should validate and store all fields."""
    resp = RealtimeSessionResponse(
        client_secret="ek_test",
        expires_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        model="gpt-4o-realtime-preview",
    )
    assert resp.client_secret == "ek_test"
    assert resp.model == "gpt-4o-realtime-preview"
    assert resp.expires_at == datetime(2024, 1, 1, tzinfo=timezone.utc)


def test_voice_provider_error_is_exception() -> None:
    """VoiceProviderError should be an Exception subclass."""
    err = VoiceProviderError("provider failed")
    assert isinstance(err, Exception)
    assert str(err) == "provider failed"
