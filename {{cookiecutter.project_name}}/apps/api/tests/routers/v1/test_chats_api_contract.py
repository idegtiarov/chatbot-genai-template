"""
Contract tests for the Chat API endpoints.

These tests define the HTTP contract for /v1/chats endpoints:
- HTTP methods, status codes, and response shapes
- Authentication requirements
- Error responses

Tests focus on WHAT the API returns, not HOW it's implemented internally.
Controller and query implementation may change.
"""

from unittest.mock import patch, AsyncMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from {{ cookiecutter.__api_package_name }}.app.app import app
from {{ cookiecutter.__api_package_name }}.auth import auth_user_id
from {{ cookiecutter.__api_package_name }}.models.chat import Chat
from {{ cookiecutter.__api_package_name }}.models.user import User


class TestChatAPIContract:
    """
    Contract tests for Chat API endpoints.

    These tests verify the HTTP interface behavior that must remain
    stable for API consumers.
    """

    @pytest.fixture
    def client(self):
        """Provide a test client for the FastAPI app."""
        with TestClient(app, raise_server_exceptions=False) as client:
            yield client

    @pytest.fixture
    def mock_user_id(self) -> str:
        """A mock authenticated user ID."""
        return "test-user-123"

    @pytest.fixture
    def mock_chat(self, mock_user_id) -> Chat:
        """A mock chat for testing."""
        return Chat(
            id=uuid4(),
            user_id=mock_user_id,
            title="Test Chat",
            messages=[],
        )

    # =========================================================================
    # Authentication Contract
    # =========================================================================

    def test_create_chat_requires_auth(self, client):
        """
        Contract: POST /v1/chats without auth returns 401.
        """
        response = client.post(
            "/v1/chats",
            json={"data": {"title": "Test"}}
        )

        assert response.status_code == 401

    def test_get_chats_requires_auth(self, client):
        """
        Contract: GET /v1/chats without auth returns 401.
        """
        response = client.get("/v1/chats")

        assert response.status_code == 401

    def test_get_chat_by_id_requires_auth(self, client):
        """
        Contract: GET /v1/chats/{id} without auth returns 401.
        """
        response = client.get(f"/v1/chats/{uuid4()}")

        assert response.status_code == 401

    def test_update_chat_requires_auth(self, client):
        """
        Contract: PATCH /v1/chats/{id} without auth returns 401.
        """
        response = client.patch(
            f"/v1/chats/{uuid4()}",
            json={"data": {"title": "Updated"}}
        )

        assert response.status_code == 401

    def test_delete_chat_requires_auth(self, client):
        """
        Contract: DELETE /v1/chats/{id} without auth returns 401.
        """
        response = client.delete(f"/v1/chats/{uuid4()}")

        assert response.status_code == 401

    # =========================================================================
    # Response Shape Contract (with mocked dependencies)
    # =========================================================================

    def test_create_chat_response_shape(self, client, mock_user_id, mock_chat):
        """
        Contract: POST /v1/chats returns 201 with correct response shape.

        Response must include:
        - data.id (UUID string)
        - data.title (string)
        - data.created_at (ISO datetime)
        - data.user_id (string)
        """
        # Override the auth dependency
        app.dependency_overrides[auth_user_id] = lambda: mock_user_id

        try:
            with patch("{{ cookiecutter.__api_package_name }}.routers.v1.chats.router.ChatCRUD") as MockCRUD:
                mock_crud = AsyncMock()
                mock_crud.save = AsyncMock()
                MockCRUD.return_value = mock_crud

                response = client.post(
                    "/v1/chats",
                    json={"data": {"title": "My New Chat"}},
                    headers={"Authorization": "Bearer fake-token"},
                )

            assert response.status_code == 201
            body = response.json()

            # Verify response shape
            assert "data" in body
            data = body["data"]
            assert "id" in data
            assert "title" in data
            assert "created_at" in data
            assert data["title"] == "My New Chat"
        finally:
            app.dependency_overrides.clear()

    def test_get_chats_response_shape(self, client, mock_user_id):
        """
        Contract: GET /v1/chats returns paginated response shape.

        Response must include:
        - data (array)
        - meta.page.total (int)
        - meta.page.limit (int)
        - meta.page.offset (int)
        """
        app.dependency_overrides[auth_user_id] = lambda: mock_user_id

        try:
            with patch("{{ cookiecutter.__api_package_name }}.routers.v1.chats.router.ChatCRUD") as MockCRUD:
                from {{ cookiecutter.__api_package_name }}.app.schemas import Paginated, PaginationQuery

                mock_crud = AsyncMock()
                mock_crud.get_all_for_user_paginated = AsyncMock(
                    return_value=Paginated([], 0, PaginationQuery(limit=10, offset=0))
                )
                MockCRUD.return_value = mock_crud

                response = client.get(
                    "/v1/chats?limit=10&offset=0",
                    headers={"Authorization": "Bearer fake-token"},
                )

            assert response.status_code == 200
            body = response.json()

            # Verify response shape (actual API uses meta.page structure)
            assert "data" in body
            assert isinstance(body["data"], list)
            assert "meta" in body
            assert "page" in body["meta"]
            assert "total" in body["meta"]["page"]
            assert "limit" in body["meta"]["page"]
            assert "offset" in body["meta"]["page"]
        finally:
            app.dependency_overrides.clear()

    def test_get_chat_not_found_response(self, client, mock_user_id):
        """
        Contract: GET /v1/chats/{id} returns 404 for non-existent chat.

        Response must include:
        - error.status (int)
        - error.title (string)
        - error.type (string)
        - error.details (array)
        """
        from {{ cookiecutter.__api_package_name }}.app.exceptions import NotFoundException

        app.dependency_overrides[auth_user_id] = lambda: mock_user_id

        try:
            with patch("{{ cookiecutter.__api_package_name }}.routers.v1.chats.router.ChatCRUD") as MockCRUD:
                mock_crud = AsyncMock()
                mock_crud.get_by_id_for_user = AsyncMock(
                    side_effect=NotFoundException("Chat not found")
                )
                MockCRUD.return_value = mock_crud

                response = client.get(
                    f"/v1/chats/{uuid4()}",
                    headers={"Authorization": "Bearer fake-token"},
                )

            assert response.status_code == 404
            body = response.json()

            # Verify error response shape
            assert "error" in body
            assert "status" in body["error"]
            assert "title" in body["error"]
            assert "type" in body["error"]
            assert body["error"]["status"] == 404
        finally:
            app.dependency_overrides.clear()

    def test_delete_chat_with_valid_id_accepted(self, client, mock_user_id):
        """
        Contract: DELETE /v1/chats/{id} with auth returns 204 or 404.

        Note: We only test that auth works - actual deletion logic is tested
        in CRUD layer. This test verifies the endpoint accepts authenticated
        requests (not 401) even if the resource doesn't exist (404 is ok).
        """
        app.dependency_overrides[auth_user_id] = lambda: mock_user_id

        try:
            response = client.delete(
                f"/v1/chats/{uuid4()}",
                headers={"Authorization": "Bearer fake-token"},
            )

            # Should not be 401 (auth works), but 404 is acceptable (resource not found)
            assert response.status_code in [204, 404]
        finally:
            app.dependency_overrides.clear()

    # =========================================================================
    # Request Validation Contract
    # =========================================================================

    def test_create_chat_validates_request_body(self, client, mock_user_id):
        """
        Contract: POST /v1/chats validates request body structure.
        Missing 'data' wrapper should return 422.
        """
        app.dependency_overrides[auth_user_id] = lambda: mock_user_id

        try:
            response = client.post(
                "/v1/chats",
                json={"title": "Missing data wrapper"},  # Wrong format
                headers={"Authorization": "Bearer fake-token"},
            )

            assert response.status_code == 422
        finally:
            app.dependency_overrides.clear()

    def test_update_chat_validates_request_body(self, client, mock_user_id):
        """
        Contract: PATCH /v1/chats/{id} validates request body structure.
        """
        app.dependency_overrides[auth_user_id] = lambda: mock_user_id

        try:
            response = client.patch(
                f"/v1/chats/{uuid4()}",
                json={"title": "Missing data wrapper"},  # Wrong format
                headers={"Authorization": "Bearer fake-token"},
            )

            assert response.status_code == 422
        finally:
            app.dependency_overrides.clear()

    def test_invalid_uuid_returns_422(self, client, mock_user_id):
        """
        Contract: Invalid UUID in path returns 422.
        """
        app.dependency_overrides[auth_user_id] = lambda: mock_user_id

        try:
            response = client.get(
                "/v1/chats/not-a-valid-uuid",
                headers={"Authorization": "Bearer fake-token"},
            )

            assert response.status_code == 422
        finally:
            app.dependency_overrides.clear()


class TestHealthEndpointContract:
    """Contract tests for health check endpoint."""

    @pytest.fixture
    def client(self):
        """Provide a test client."""
        with TestClient(app, raise_server_exceptions=False) as client:
            yield client

    def test_root_returns_ok(self, client):
        """
        Contract: GET / returns health status.

        Response must include:
        - data.ok (boolean, always true when running)
        """
        response = client.get("/")

        assert response.status_code == 200
        body = response.json()
        assert body == {"data": {"ok": True}}
