import json
import logging

from openai import APIError, OpenAI
from pydantic import ValidationError

from app.models.utterance import Utterance
from app.providers.errors import KnowledgeExtractionError
from app.providers.knowledge_extraction_schema import KnowledgeExtraction, KnowledgeExtractionList

logger = logging.getLogger(__name__)


class OpenAIKnowledgeModel:
    """KnowledgeModel implementation using the OpenAI Chat Completions API."""

    def __init__(self, api_key: str) -> None:
        """Initialize with an OpenAI API key."""
        self._client = OpenAI(api_key=api_key)

    def _format_transcript(self, utterances: list[Utterance]) -> str:
        """Format utterances as a readable conversation transcript."""
        return "\n".join(f"{u.speaker.value}: {u.text}" for u in utterances)

    def _extract_all(self, utterances: list[Utterance]) -> list[KnowledgeExtraction]:
        """Extract all knowledge items from utterances in a single structured API call."""
        transcript = self._format_transcript(utterances)
        try:
            response = self._client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a knowledge extraction assistant. "
                            "Analyze the conversation and identify ALL distinct questions or topics discussed. "
                            "Respond with a JSON object containing an 'items' array. "
                            "Each item must have exactly these fields: "
                            "title (concise 5-10 word title), "
                            "question (the question discussed), "
                            "summary (1-3 sentence summary), "
                            "answer (the answer or conclusion reached), "
                            "category (1-3 word topic category), "
                            "keywords (list of key terms as JSON array), "
                            "related_questions (list of follow-up questions the user asked about this topic "
                            "during the conversation, empty list if none). "
                            "If only one topic was discussed, return an array with one item. "
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
            logger.error("OpenAI API error during knowledge extraction: %s", exc)
            raise KnowledgeExtractionError(f"OpenAI API error: {exc}") from exc
        content = response.choices[0].message.content or "{}"
        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            logger.error("LLM returned invalid JSON: %s", exc)
            raise KnowledgeExtractionError(f"LLM returned invalid JSON: {exc}") from exc
        try:
            return KnowledgeExtractionList.model_validate(data).items
        except ValidationError as exc:
            logger.error("LLM response schema mismatch: %s", exc)
            raise KnowledgeExtractionError(f"LLM response does not match expected schema: {exc}") from exc

    def summarize_conversation(self, utterances: list[Utterance]) -> str:
        """Generate a text summary of the conversation."""
        return self._extract_all(utterances).summary

    def extract_questions(self, utterances: list[Utterance]) -> list[str]:
        """Extract questions discussed in the conversation."""
        items = self._extract_all(utterances)
        return [item.question for item in items if item.question]

    def extract_keywords(self, utterances: list[Utterance]) -> list[str]:
        """Extract relevant keywords from the conversation."""
        items = self._extract_all(utterances)
        return items[0].keywords if items else []

    def classify_category(self, utterances: list[Utterance]) -> str:
        """Classify the main topic of the conversation into a category."""
        items = self._extract_all(utterances)
        return items[0].category if items else ""

    def generate_title(self, utterances: list[Utterance]) -> str:
        """Generate a concise title for the knowledge item."""
        items = self._extract_all(utterances)
        return items[0].title if items else ""

    def extract_knowledge(self, utterances: list[Utterance]) -> list[KnowledgeExtraction]:
        """Extract all knowledge items in a single API call, returning one item per topic."""
        return self._extract_all(utterances)
