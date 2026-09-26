from openai import OpenAI

from app.models.utterance import Utterance


class OpenAIKnowledgeModel:
    """KnowledgeModel implementation using the OpenAI Chat Completions API."""

    def __init__(self, api_key: str) -> None:
        """Initialize with an OpenAI API key."""
        self._client = OpenAI(api_key=api_key)

    def _format_transcript(self, utterances: list[Utterance]) -> str:
        """Format utterances as a readable conversation transcript."""
        return "\n".join(f"{u.speaker.value}: {u.text}" for u in utterances)

    def _complete(self, system: str, user: str) -> str:
        """Send a chat completion request and return the stripped response text."""
        response = self._client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return (response.choices[0].message.content or "").strip()

    def summarize_conversation(self, utterances: list[Utterance]) -> str:
        """Generate a text summary of the conversation."""
        transcript = self._format_transcript(utterances)
        return self._complete(
            system="You are an expert at summarizing conversations. Respond in the same language as the conversation.",
            user=f"Summarize the following conversation in 1-3 sentences:\n\n{transcript}",
        )

    def extract_questions(self, utterances: list[Utterance]) -> list[str]:
        """Extract questions discussed in the conversation."""
        transcript = self._format_transcript(utterances)
        content = self._complete(
            system="You are an expert at identifying questions from conversations. Respond in the same language as the conversation.",
            user=f"List the main questions discussed in the following conversation. Return one question per line with no extra formatting:\n\n{transcript}",
        )
        return [line.strip() for line in content.splitlines() if line.strip()]

    def extract_keywords(self, utterances: list[Utterance]) -> list[str]:
        """Extract relevant keywords from the conversation."""
        transcript = self._format_transcript(utterances)
        content = self._complete(
            system="You are an expert at extracting keywords from conversations. Respond in the same language as the conversation.",
            user=f"Extract key terms and concepts from the following conversation. Return one keyword per line with no extra formatting:\n\n{transcript}",
        )
        return [line.strip() for line in content.splitlines() if line.strip()]

    def classify_category(self, utterances: list[Utterance]) -> str:
        """Classify the main topic of the conversation into a category."""
        transcript = self._format_transcript(utterances)
        return self._complete(
            system="You are an expert at categorizing topics. Respond in the same language as the conversation.",
            user=f"Classify the main topic of the following conversation into a single category (1-3 words):\n\n{transcript}",
        )

    def generate_title(self, utterances: list[Utterance]) -> str:
        """Generate a concise title for the knowledge item."""
        transcript = self._format_transcript(utterances)
        return self._complete(
            system="You are an expert at creating concise titles. Respond in the same language as the conversation.",
            user=f"Generate a concise title (5-10 words) for the following conversation:\n\n{transcript}",
        )
