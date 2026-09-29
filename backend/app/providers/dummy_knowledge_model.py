from app.models.utterance import Utterance
from app.providers.knowledge_extraction_schema import KnowledgeExtraction


class DummyKnowledgeModel:
    """Fake KnowledgeModel that returns fixed responses for testing without external AI calls."""

    def summarize_conversation(self, utterances: list[Utterance]) -> str:
        """Return a fixed summary string regardless of utterances."""
        return "dummy summary"

    def extract_questions(self, utterances: list[Utterance]) -> list[str]:
        """Return a fixed list of questions regardless of utterances."""
        return ["dummy question"]

    def extract_keywords(self, utterances: list[Utterance]) -> list[str]:
        """Return a fixed list of keywords regardless of utterances."""
        return ["dummy keyword"]

    def classify_category(self, utterances: list[Utterance]) -> str:
        """Return a fixed category string regardless of utterances."""
        return "dummy category"

    def generate_title(self, utterances: list[Utterance]) -> str:
        """Return a fixed title string regardless of utterances."""
        return "dummy title"

    def extract_knowledge(self, utterances: list[Utterance]) -> KnowledgeExtraction:
        """Return a fixed KnowledgeExtraction for testing."""
        return KnowledgeExtraction(
            title="dummy title",
            question="dummy question",
            summary="dummy summary",
            answer="dummy answer",
            category="dummy category",
            keywords=["dummy keyword"],
        )
