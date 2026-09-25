from app.core.config import Settings, get_settings


def test_settings_default_database_url() -> None:
    """Settings should have a sqlite default for database_url."""
    settings = Settings()
    assert "sqlite" in settings.database_url


def test_get_settings_returns_settings_instance() -> None:
    """get_settings() should return a Settings instance."""
    settings = get_settings()
    assert isinstance(settings, Settings)
