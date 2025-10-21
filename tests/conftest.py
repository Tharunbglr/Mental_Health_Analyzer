import os

import pytest

from app import create_app


@pytest.fixture()
def app():
    os.environ.setdefault("FLASK_ENV", "development")
    os.environ.setdefault("SECRET_KEY", "test-secret")
    application = create_app()
    application.config.update(
        {
            "TESTING": True,
            # Disable CSRF in tests to allow form posts without tokens
            "WTF_CSRF_ENABLED": False,
        }
    )
    yield application


@pytest.fixture()
def client(app):
    return app.test_client()
