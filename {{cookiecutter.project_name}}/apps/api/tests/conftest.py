"""
Shared test fixtures for the application.

These fixtures focus on providing test data that matches the expected contracts,
not on internal implementation details.
"""

import os
from typing import AsyncGenerator
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from {{ cookiecutter.__api_package_name }}.models.user import User
from {{ cookiecutter.__api_package_name }}.models.message import Message, MessageSegment
from {{ cookiecutter.__api_package_name }}.models.chat import Chat


# =============================================================================
# Database Fixtures
# =============================================================================


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a database session for testing using local PostgreSQL.
    Creates a fresh engine per test to avoid event loop conflicts.
    """
    from {{ cookiecutter.__api_package_name }}.common.environ import env_str

    database_url = "".join([
        "postgresql+asyncpg://",
        env_str("DB_USERNAME", "postgres"),
        ":",
        env_str("DB_PASSWORD", "postgres"),
        "@",
        f"{env_str('DB_HOST', 'localhost')}:{env_str('DB_PORT', '5432')}",
        "/",
        env_str("DB_NAME", "{{ cookiecutter.database_name }}"),
        f"?ssl={env_str('DB_SSL_MODE', 'prefer')}",
    ])

    engine = create_async_engine(database_url, echo=False)
    sessionmaker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with sessionmaker() as session:
        yield session
        # Rollback any changes made during the test
        await session.rollback()

    await engine.dispose()


# =============================================================================
# User Fixtures
# =============================================================================


@pytest.fixture
def sample_user() -> User:
    """A sample user object matching the User contract."""
    return User(
        id="test-user-123",
        username="testuser",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def sample_user_id() -> str:
    """A sample user ID."""
    return "test-user-123"


# =============================================================================
# Chat & Message Fixtures
# =============================================================================


@pytest.fixture
def sample_chat_id():
    """A sample chat UUID."""
    return uuid4()


@pytest.fixture
def sample_chat(sample_user_id, sample_chat_id) -> Chat:
    """A sample chat object matching the Chat contract."""
    return Chat(
        id=sample_chat_id,
        user_id=sample_user_id,
        title="Test Chat",
        messages=[],
    )


@pytest.fixture
def sample_message(sample_chat_id) -> Message:
    """A sample message object matching the Message contract."""
    return Message(
        id=uuid4(),
        chat_id=sample_chat_id,
        role="user",  # type: ignore[arg-type]
        segments=[MessageSegment.text("Hello, this is a test message")],
    )


@pytest.fixture
def sample_assistant_message(sample_chat_id) -> Message:
    """A sample assistant message object."""
    return Message(
        id=uuid4(),
        chat_id=sample_chat_id,
        role="assistant",  # type: ignore[arg-type]
        segments=[MessageSegment.text("Hello! How can I help you today?")],
    )


@pytest.fixture
def sample_message_history(sample_chat_id) -> list[Message]:
    """A sample conversation history with multiple messages."""
    return [
        Message(
            id=uuid4(),
            chat_id=sample_chat_id,
            role="user",  # type: ignore[arg-type]
            segments=[MessageSegment.text("Hello!")],
        ),
        Message(
            id=uuid4(),
            chat_id=sample_chat_id,
            role="assistant",  # type: ignore[arg-type]
            segments=[MessageSegment.text("Hi there! How can I help?")],
        ),
        Message(
            id=uuid4(),
            chat_id=sample_chat_id,
            role="user",  # type: ignore[arg-type]
            segments=[MessageSegment.text("What's the weather like?")],
        ),
    ]


# =============================================================================
# Auth Fixtures
# =============================================================================


@pytest.fixture
def users_yaml_content() -> str:
    """YAML content for test users file."""
    return """
- id: "test-user-123"
  username: "testuser"
  password: "testpass123"
  first_name: "Test"
  last_name: "User"
- id: "admin-user-456"
  username: "admin"
  password: "adminpass456"
  first_name: "Admin"
  last_name: "User"
"""


@pytest.fixture
def users_file(tmp_path, users_yaml_content) -> str:
    """Create a temporary users.yaml file for testing."""
    users_file = tmp_path / "users.yaml"
    users_file.write_text(users_yaml_content)
    return str(users_file)


@pytest.fixture
def auth_env_vars(users_file) -> dict[str, str]:
    """Environment variables for auth testing."""
    return {
        "AUTH_LOCAL_USERS_PATH": users_file,
        "AUTH_LOCAL_JWT_SECRET": "test-secret-key-for-testing",
        "AUTH_LOCAL_JWT_TTL": "3600",
    }


# =============================================================================
# Environment Fixtures
# =============================================================================


@pytest.fixture
def clean_env():
    """Provide a clean environment context for testing env functions."""
    original_environ = os.environ.copy()
    yield os.environ
    os.environ.clear()
    os.environ.update(original_environ)
