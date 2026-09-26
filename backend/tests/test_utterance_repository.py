from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.database import Base
from app.models.conversation_session import ConversationSession
from app.models.utterance import SpeakerType
from app.repositories.utterance_repository import UtteranceRepository


def _make_engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


def test_create_returns_persisted_utterance() -> None:
    """create() should persist an Utterance with all fields and return it."""
    with Session(_make_engine()) as db:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add(cs)
        db.flush()

        repo = UtteranceRepository(db)
        ts = datetime.now(timezone.utc)
        utt = repo.create(
            session_id=cs.id,
            speaker=SpeakerType.user,
            text="なぜCDって虹色なの？",
            timestamp=ts,
            sequence_number=1,
        )

        assert utt.id is not None
        assert utt.session_id == cs.id
        assert utt.speaker == SpeakerType.user
        assert utt.text == "なぜCDって虹色なの？"
        assert utt.timestamp == ts.replace(tzinfo=None)
        assert utt.sequence_number == 1


def test_list_by_session_returns_utterances_in_sequence_order() -> None:
    """list_by_session() should return utterances sorted by sequence_number ascending."""
    with Session(_make_engine()) as db:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add(cs)
        db.flush()

        repo = UtteranceRepository(db)
        ts = datetime.now(timezone.utc)
        repo.create(session_id=cs.id, speaker=SpeakerType.assistant, text="second", timestamp=ts, sequence_number=2)
        repo.create(session_id=cs.id, speaker=SpeakerType.user, text="first", timestamp=ts, sequence_number=1)

        utterances = repo.list_by_session(cs.id)

        assert len(utterances) == 2
        assert utterances[0].sequence_number == 1
        assert utterances[1].sequence_number == 2


def test_list_by_session_returns_only_target_session_utterances() -> None:
    """list_by_session() should not return utterances from other sessions."""
    with Session(_make_engine()) as db:
        cs1 = ConversationSession(started_at=datetime.now(timezone.utc))
        cs2 = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add_all([cs1, cs2])
        db.flush()

        repo = UtteranceRepository(db)
        ts = datetime.now(timezone.utc)
        repo.create(session_id=cs1.id, speaker=SpeakerType.user, text="session 1", timestamp=ts, sequence_number=1)
        repo.create(session_id=cs2.id, speaker=SpeakerType.user, text="session 2", timestamp=ts, sequence_number=1)

        utterances = repo.list_by_session(cs1.id)

        assert len(utterances) == 1
        assert utterances[0].text == "session 1"


def test_list_by_session_returns_empty_list_for_missing_session() -> None:
    """list_by_session() should return an empty list for a non-existent session_id."""
    with Session(_make_engine()) as db:
        repo = UtteranceRepository(db)

        assert repo.list_by_session(9999) == []
