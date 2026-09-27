import json

from openai import APIError, OpenAI
from pydantic import ValidationError

from app.models.utterance import Utterance
from app.providers.errors import KnowledgeExtractionError
from app.providers.knowledge_extraction_schema import KnowledgeExtraction


class OpenAIKnowledgeModel:
    """KnowledgeModel implementation using the OpenAI Chat Completions API."""

    def __init__(self, api_key: str) -> None:
        """Initialize with an OpenAI API key."""
        self._client = OpenAI(api_key=api_key)

    def _format_transcript(self, utterances: list[Utterance]) -> str:
        """Format utterances as a readable conversation transcript."""
        return "\n".join(f"{u.speaker.value}: {u.text}" for u in utterances)

    def _extract_all(self, utterances: list[Utterance]) -> KnowledgeExtraction:
        """Extract all knowledge fields from utterances in a single structured API call."""
        transcript = self._format_transcript(utterances)
        try:
            response = self._client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a knowledge extraction assistant. "
                            "Analyze the conversation and respond with a JSON object containing exactly these fields: "
                            "title (concise 5-10 word title), "
                            "question (the main question discussed), "
                            "summary (1-3 sentence summary), "
                            "answer (the answer or conclusion reached), "
                            "category (1-3 word topic category), "
                            "keywords (list of key terms as JSON array). "
                            "Respond in the same language as the conversation."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Extract knowledge from this conversation:\n\n{transcript}",
                    },
                ],
                response_format={"type": "json_object"},
            )
        except APIError as exc:
            raise KnowledgeExtractionError(f"OpenAI API error: {exc}") from exc
        content = response.choices[0].message.content or "{}"
        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise KnowledgeExtractionError(f"LLM returned invalid JSON: {exc}") from exc
        try:
            return KnowledgeExtraction.model_validate(data)
        except ValidationError as exc:
            raise KnowledgeExtractionError(f"LLM response does not match expected schema: {exc}") from exc

    def summarize_conversation(self, utterances: list[Utterance]) -> str:
        """Generate a text summary of the conversation."""
        return self._extract_all(utterances).summary

    def extract_questions(self, utterances: list[Utterance]) -> list[str]:
        """Extract questions discussed in the conversation."""
        question = self._extract_all(utterances).question
        return [question] if question else []

    def extract_keywords(self, utterances: list[Utterance]) -> list[str]:
        """Extract relevant keywords from the conversation."""
        return self._extract_all(utterances).keywords

    def classify_category(self, utterances: list[Utterance]) -> str:
        """Classify the main topic of the conversation into a category."""
        return self._extract_all(utterances).category

    def generate_title(self, utterances: list[Utterance]) -> str:
        """Generate a concise title for the knowledge item."""
        return self._extract_all(utterances).title
