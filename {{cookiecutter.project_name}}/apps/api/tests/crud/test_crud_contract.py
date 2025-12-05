"""
Contract tests for the CRUD interface.

These tests define the behavioral contract that AbstractCRUD provides:

1. get_by_id() - Retrieve single resource by ID
2. get_by_ids() - Retrieve multiple resources by IDs
3. get_count() - Count resources
4. does_exist() - Check resource existence
5. get_all() - List resources with pagination
6. get_all_paginated() - List resources with pagination metadata
7. save() - Create or update resource
8. save_all() - Bulk create/update
9. delete() - Soft delete resource

Tests focus on WHAT the CRUD layer does, not HOW queries are built.
Query implementation details may change.
"""

from uuid import uuid4

import pytest

from {{ cookiecutter.__api_package_name }}.crud.chat_crud import ChatCRUD
from {{ cookiecutter.__api_package_name }}.models.chat import Chat
from {{ cookiecutter.__api_package_name }}.app.exceptions import NotFoundException


class TestCRUDContract:
    """
    Contract tests for CRUD operations.

    These tests verify the public interface behavior using local PostgreSQL.
    Each test uses unique IDs to avoid conflicts with existing data.
    """

    @pytest.fixture
    def crud(self, db_session) -> ChatCRUD:
        """Provide a CRUD instance for testing."""
        return ChatCRUD(db_session)

    @pytest.fixture
    def unique_user_id(self) -> str:
        """Generate a unique user ID for test isolation."""
        return f"test-user-{uuid4()}"

    @pytest.fixture
    def sample_entity(self, unique_user_id) -> Chat:
        """Create a sample Chat entity for testing."""
        return Chat(
            id=uuid4(),
            user_id=unique_user_id,
            title="Test Chat",
            messages=[],
        )

    @pytest.fixture
    async def persisted_entity(self, crud, sample_entity) -> Chat:
        """Create and persist a sample entity."""
        await crud.save(sample_entity)
        return sample_entity

    # =========================================================================
    # get_by_id() Contract
    # =========================================================================

    async def test_get_by_id_returns_entity_when_exists(self, crud, persisted_entity):
        """
        Contract: get_by_id returns the entity when it exists.
        """
        result = await crud.get_by_id(persisted_entity.id)

        assert result is not None
        assert result.id == persisted_entity.id

    async def test_get_by_id_returns_none_when_not_exists(self, crud):
        """
        Contract: get_by_id returns None when entity doesn't exist.
        """
        nonexistent_id = uuid4()
        result = await crud.get_by_id(nonexistent_id)

        assert result is None

    async def test_get_by_id_raises_when_not_found_and_requested(self, crud):
        """
        Contract: get_by_id raises NotFoundException when raise_not_found=True.
        """
        nonexistent_id = uuid4()

        with pytest.raises(NotFoundException):
            await crud.get_by_id(nonexistent_id, raise_not_found=True)

    async def test_get_by_id_does_not_return_deleted(self, crud, persisted_entity):
        """
        Contract: get_by_id does not return soft-deleted entities.
        """
        await crud.delete(persisted_entity)

        result = await crud.get_by_id(persisted_entity.id)

        assert result is None

    # =========================================================================
    # get_by_ids() Contract
    # =========================================================================

    async def test_get_by_ids_returns_matching_entities(self, crud, unique_user_id):
        """
        Contract: get_by_ids returns all entities matching the given IDs.
        """
        # Create multiple entities with unique IDs
        entities = [
            Chat(id=uuid4(), user_id=unique_user_id, title=f"Chat {i}", messages=[])
            for i in range(3)
        ]
        for entity in entities:
            await crud.save(entity)

        # Request subset
        requested_ids = [entities[0].id, entities[2].id]
        result = await crud.get_by_ids(requested_ids)

        assert len(result) == 2
        result_ids = {e.id for e in result}
        assert entities[0].id in result_ids
        assert entities[2].id in result_ids

    async def test_get_by_ids_ignores_nonexistent(self, crud, persisted_entity):
        """
        Contract: get_by_ids silently ignores non-existent IDs.
        """
        result = await crud.get_by_ids([persisted_entity.id, uuid4()])

        assert len(result) == 1
        assert result[0].id == persisted_entity.id

    # =========================================================================
    # save() Contract
    # =========================================================================

    async def test_save_persists_new_entity(self, crud, sample_entity):
        """
        Contract: save persists a new entity that can be retrieved.
        """
        await crud.save(sample_entity)

        retrieved = await crud.get_by_id(sample_entity.id)
        assert retrieved is not None
        assert retrieved.id == sample_entity.id

    async def test_save_updates_existing_entity(self, crud, persisted_entity):
        """
        Contract: save updates an existing entity's fields.
        """
        persisted_entity.title = "Updated Title"
        await crud.save(persisted_entity)

        retrieved = await crud.get_by_id(persisted_entity.id)
        assert retrieved is not None
        assert retrieved.title == "Updated Title"

    async def test_save_updates_modified_at(self, crud, persisted_entity):
        """
        Contract: save updates the modified_at timestamp by default.
        """
        original_modified = persisted_entity.modified_at
        persisted_entity.title = "Changed"
        await crud.save(persisted_entity)

        retrieved = await crud.get_by_id(persisted_entity.id)
        assert retrieved is not None
        assert retrieved.modified_at >= original_modified

    # =========================================================================
    # delete() Contract
    # =========================================================================

    async def test_delete_soft_deletes_entity(self, crud, persisted_entity):
        """
        Contract: delete performs soft delete (entity still exists but is hidden).
        """
        await crud.delete(persisted_entity)

        # Should not be retrievable via normal get
        result = await crud.get_by_id(persisted_entity.id)
        assert result is None

        # But deleted_at should be set (entity not physically removed)
        assert persisted_entity.deleted_at is not None

    async def test_delete_sets_deleted_at_timestamp(self, crud, persisted_entity):
        """
        Contract: delete sets the deleted_at field to current time.
        """
        assert persisted_entity.deleted_at is None

        await crud.delete(persisted_entity)

        assert persisted_entity.deleted_at is not None
