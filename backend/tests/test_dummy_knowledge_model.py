from app.providers.dummy_knowledge_model import DummyKnowledgeModel


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
