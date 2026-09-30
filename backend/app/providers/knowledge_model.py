from typing import Protocol

from app.models.utterance import Utterance
from app.providers.knowledge_extraction_schema import KnowledgeExtraction


class KnowledgeModel(Protocol):
    """Protocol defining the interface for AI-based knowledge extraction."""

    def summarize_conversation(self, utterances: list[Utterance]) -> str:
        """Generate a text summary of the conversation."""
        ...

    def extract_questions(self, utterances: list[Utterance]) -> list[str]:
        """Extract questions discussed in the conversation."""
        ...

    def extract_keywords(self, utterances: list[Utterance]) -> list[str]:
        """Extract relevant keywords from the conversation."""
        ...

    def classify_category(self, utterances: list[Utterance]) -> str:
        """Classify the main topic of the conversation into a category."""
        ...

    def generate_title(self, utterances: list[Utterance]) -> str:
        """Generate a concise title for the knowledge item."""
        ...

    def extract_knowledge(self, utterances: list[Utterance]) -> list[KnowledgeExtraction]:
        """Extract all knowledge items in a single call, returning one item per topic."""
        ...
