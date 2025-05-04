import os
from unittest import mock

from backend.config import (
    APP_NAME,
    API_HOST,
    API_PORT,
    DATA_DIR,
    CORS_ALLOW_ORIGINS,
    CORS_ALLOW_METHODS,
    CORS_ALLOW_HEADERS,
    CORS_ALLOW_CREDENTIALS,
)


def test_settings_default_values():
    """Test that Settings has the expected default values."""
    assert APP_NAME == "DevOps Study Tracker"
    assert API_HOST == "0.0.0.0"
    assert API_PORT == 22112
    assert DATA_DIR.endswith("data")

    # Test CORS default values
    assert CORS_ALLOW_ORIGINS == ["*"]
    assert CORS_ALLOW_METHODS == ["*"]
    assert CORS_ALLOW_HEADERS == ["*"]
    assert CORS_ALLOW_CREDENTIALS is True


@mock.patch.dict(
    os.environ,
    {
        "API_HOST": "127.0.0.1",
        "API_PORT": "9000",
        "CORS_ALLOW_ORIGINS": "https://example.com,https://api.example.com",
        "CORS_ALLOW_METHODS": "GET,POST,PUT",
        "CORS_ALLOW_HEADERS": "Content-Type,Authorization",
        "CORS_ALLOW_CREDENTIALS": "false",
    },
)
def test_settings_from_env():
    """Test that Settings loads values from environment variables."""
    # Force reload of the config module to get updated environment variables
    import importlib
    import backend.config

    importlib.reload(backend.config)

    # Import the settings again after reload
    from backend.config import (
        API_HOST,
        API_PORT,
        CORS_ALLOW_ORIGINS,
        CORS_ALLOW_METHODS,
        CORS_ALLOW_HEADERS,
        CORS_ALLOW_CREDENTIALS,
    )

    assert API_HOST == "127.0.0.1"
    assert API_PORT == 9000

    # Test CORS values from environment
    assert CORS_ALLOW_ORIGINS == [
        "https://example.com",
        "https://api.example.com",
    ]
    assert CORS_ALLOW_METHODS == ["GET", "POST", "PUT"]
    assert CORS_ALLOW_HEADERS == ["Content-Type", "Authorization"]
    assert CORS_ALLOW_CREDENTIALS is False
