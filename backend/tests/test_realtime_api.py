from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.api.realtime import get_voice_provider
from app.main import app
from app.providers.dummy_voice_provider import DummyVoiceProvider

client = TestClient(app)


def test_create_realtime_session_returns_200() -> None:
    """POST /realtime/session should return HTTP 200."""
    response = client.post("/realtime/session")
    assert response.status_code == 200


def test_create_realtime_session_returns_all_fields() -> None:
    """POST /realtime/session response should contain client_secret, expires_at, and model."""
    response = client.post("/realtime/session")
    data = response.json()
    assert "client_secret" in data
    assert "expires_at" in data
    assert "model" in data


def test_create_realtime_session_returns_dummy_values() -> None:
    """POST /realtime/session should return the DummyVoiceProvider's fixed values."""
    response = client.post("/realtime/session")
    data = response.json()
    assert data["client_secret"] == "dummy_client_secret"
    assert data["model"] == "gpt-4o-realtime-preview"


def test_create_realtime_session_returns_503_when_provider_not_configured() -> None:
    """POST /realtime/session should return 503 when voice provider is not configured."""

    def raise_503() -> None:
        raise HTTPException(status_code=503, detail="Voice provider not configured")

    app.dependency_overrides[get_voice_provider] = raise_503
    response = client.post("/realtime/session")
    app.dependency_overrides[get_voice_provider] = lambda: DummyVoiceProvider()
    assert response.status_code == 503
    assert response.json()["detail"] == "Voice provider not configured"


def test_create_realtime_session_returns_502_on_provider_error() -> None:
    """POST /realtime/session should return 502 when the voice provider raises VoiceProviderError."""
    from app.providers.errors import VoiceProviderError

    class FailingProvider:
        def create_realtime_credentials(self) -> None:
            raise VoiceProviderError("test error")

    app.dependency_overrides[get_voice_provider] = lambda: FailingProvider()
    response = client.post("/realtime/session")
    app.dependency_overrides[get_voice_provider] = lambda: DummyVoiceProvider()
    assert response.status_code == 502
    assert response.json()["detail"] == "Voice provider error"
