from fastapi import APIRouter, Depends, HTTPException

from app.core.config import Settings, get_settings
from app.providers.errors import VoiceProviderError
from app.providers.openai_voice_provider import OpenAIVoiceProvider
from app.providers.voice_provider import VoiceProvider
from app.schemas.realtime import RealtimeSessionResponse

router = APIRouter()


def get_voice_provider(settings: Settings = Depends(get_settings)) -> VoiceProvider:
    """Return the configured VoiceProvider instance."""
    if settings.openai_api_key:
        return OpenAIVoiceProvider(api_key=settings.openai_api_key)
    raise HTTPException(status_code=503, detail="Voice provider not configured")


@router.post("/session", response_model=RealtimeSessionResponse)
def create_realtime_session(
    provider: VoiceProvider = Depends(get_voice_provider),
) -> RealtimeSessionResponse:
    """Create an ephemeral Realtime API session credential for WebRTC connection."""
    try:
        creds = provider.create_realtime_credentials()
    except VoiceProviderError:
        raise HTTPException(status_code=502, detail="Voice provider error")
    return RealtimeSessionResponse(
        client_secret=creds.client_secret,
        expires_at=creds.expires_at,
        model=creds.model,
    )
