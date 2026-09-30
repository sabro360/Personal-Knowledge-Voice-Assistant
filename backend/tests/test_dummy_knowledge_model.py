from app.providers.dummy_knowledge_model import DummyKnowledgeModel
from app.providers.knowledge_extraction_schema import KnowledgeExtraction


def test_summarize_conversation_returns_fixed_string() -> None:
    """summarize_conversation() should return a fixed string."""
    model = DummyKnowledgeModel()
    result = model.summarize_conversation([])

    assert isinstance(result, str)
    assert result == "dummy summary"


def test_extract_questions_returns_fixed_list() -> None:
    """extract_questions() should return a fixed list of strings."""
    model = DummyKnowledgeModel()
    result = model.extract_questions([])

    assert isinstance(result, list)
    assert result == ["dummy question"]


def test_extract_keywords_returns_fixed_list() -> None:
    """extract_keywords() should return a fixed list of strings."""
    model = DummyKnowledgeModel()
    result = model.extract_keywords([])

    assert isinstance(result, list)
    assert result == ["dummy keyword"]


def test_classify_category_returns_fixed_string() -> None:
    """classify_category() should return a fixed category string."""
    model = DummyKnowledgeModel()
    result = model.classify_category([])

    assert isinstance(result, str)
    assert result == "dummy category"


def test_generate_title_returns_fixed_string() -> None:
    """generate_title() should return a fixed title string."""
    model = DummyKnowledgeModel()
    result = model.generate_title([])

    assert isinstance(result, str)
    assert result == "dummy title"


def test_extract_knowledge_returns_knowledge_extraction_list() -> None:
    """extract_knowledge() should return a list with one KnowledgeExtraction."""
    model = DummyKnowledgeModel()
    result = model.extract_knowledge([])

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], KnowledgeExtraction)
    assert result[0].title == "dummy title"
    assert result[0].question == "dummy question"
    assert result[0].summary == "dummy summary"
    assert result[0].answer == "dummy answer"
    assert result[0].category == "dummy category"
    assert result[0].keywords == ["dummy keyword"]
    assert result[0].related_questions == ["dummy related question"]
