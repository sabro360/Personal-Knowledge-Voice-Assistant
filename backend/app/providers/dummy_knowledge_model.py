from app.models.utterance import Utterance


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
