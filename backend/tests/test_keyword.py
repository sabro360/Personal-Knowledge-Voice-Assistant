import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.database import Base
from app.models.keyword import Keyword


def test_keyword_tablename() -> None:
    """Keyword should map to keywords table."""
    assert Keyword.__tablename__ == "keywords"


def test_keyword_columns() -> None:
    """Keyword should have all required columns."""
    columns = {col.name for col in Keyword.__table__.columns}
    assert columns == {"id", "name"}


def test_keyword_insert_and_retrieve() -> None:
    """Keyword should be insertable and retrievable via in-memory SQLite."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        k = Keyword(name="光学")
        session.add(k)
        session.commit()
        session.refresh(k)

        assert k.id is not None
        assert k.name == "光学"


def test_keyword_name_unique() -> None:
    """Keyword name should be unique."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        session.add(Keyword(name="光学"))
        session.commit()

    with Session(engine) as session:
        session.add(Keyword(name="光学"))
        with pytest.raises(IntegrityError):
            session.commit()
