import json
from unittest.mock import MagicMock, patch

import pytest

from app.providers.errors import KnowledgeExtractionError
from app.providers.openai_knowledge_model import OpenAIKnowledgeModel


def _make_model_with_content(content: str) -> OpenAIKnowledgeModel:
    """Create an OpenAIKnowledgeModel whose API call returns the given content string."""
    mock_response = MagicMock()
    mock_response.choices[0].message.content = content
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    with patch("app.providers.openai_knowledge_model.OpenAI", return_value=mock_client):
        return OpenAIKnowledgeModel(api_key="test-key")


def test_extract_all_raises_on_invalid_json() -> None:
    """_extract_all() should raise KnowledgeExtractionError when LLM returns invalid JSON."""
    model = _make_model_with_content("not valid json")
    with pytest.raises(KnowledgeExtractionError):
        model.generate_title([])


def test_extract_all_raises_on_missing_fields() -> None:
    """_extract_all() should raise KnowledgeExtractionError when JSON is missing required fields."""
    model = _make_model_with_content(json.dumps({"title": "only title"}))
    with pytest.raises(KnowledgeExtractionError):
        model.generate_title([])
