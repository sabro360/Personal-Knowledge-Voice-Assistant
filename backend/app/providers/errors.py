class KnowledgeExtractionError(Exception):
    """Raised when knowledge extraction fails due to an invalid LLM response."""


class VoiceProviderError(Exception):
    """Raised when voice provider fails to create realtime credentials."""
