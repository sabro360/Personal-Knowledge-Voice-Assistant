from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.database import Base
from app.models.utterance import SpeakerType, Utterance


def test_utterance_tablename() -> None:
    """Utterance should map to utterances table."""
    assert Utterance.__tablename__ == "utterances"


def test_utterance_columns() -> None:
    """Utterance should have all required columns."""
    columns = {col.name for col in Utterance.__table__.columns}
    assert columns == {"id", "session_id", "speaker", "text", "timestamp", "sequence_number"}


def test_speaker_type_values() -> None:
    """SpeakerType should have user, assistant, and system values."""
    assert SpeakerType.user == "user"
    assert SpeakerType.assistant == "assistant"
    assert SpeakerType.system == "system"


def test_utterance_insert_and_retrieve() -> None:
    """Utterance should be insertable and retrievable via in-memory SQLite."""
    from app.models.conversation_session import ConversationSession

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        session.add(cs)
        session.flush()

        utt = Utterance(
            session_id=cs.id,
            speaker=SpeakerType.user,
            text="なぜCDって虹色なの？",
            timestamp=datetime.now(timezone.utc),
            sequence_number=1,
        )
        session.add(utt)
        session.commit()
        session.refresh(utt)

        assert utt.id is not None
        assert utt.session_id == cs.id
        assert utt.speaker == SpeakerType.user
        assert utt.text == "なぜCDって虹色なの？"
        assert utt.timestamp is not None
        assert utt.sequence_number == 1
