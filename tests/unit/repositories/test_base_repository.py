import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repositories.base_repository import BaseRepository
from src.models.users import Role


class TestBaseRepository:
    @pytest.mark.asyncio
    async def test_create_role(self, db_session: AsyncSession) -> None:
        repo = BaseRepository(Role, db_session)

        role_data = {"name": "admin"}

        role = await repo.create(role_data)

        assert role.id is not None
        assert role.name == "admin"
        assert isinstance(role, Role)

    @pytest.mark.asyncio
    async def test_get_by_id_existing_role(self, db_session: AsyncSession) -> None:
        repo = BaseRepository(Role, db_session)

        role_data = {"name": "manager"}
        created_role = await repo.create(role_data)

        retrieved_role = await repo.get_by_id(created_role.id)

        assert retrieved_role is not None
        assert retrieved_role.id == created_role.id
        assert retrieved_role.name == "manager"

    @pytest.mark.asyncio
    async def test_get_by_id_nonexistent_role(self, db_session: AsyncSession) -> None:
        repo = BaseRepository(Role, db_session)

        role = await repo.get_by_id(99999)

        assert role is None

    @pytest.mark.asyncio
    async def test_list_roles(self, db_session: AsyncSession) -> None:
        repo = BaseRepository(Role, db_session)

        roles_data = [{"name": "admin"}, {"name": "manager"}, {"name": "user"}, {"name": "guest"}]

        for role_data in roles_data:
            await repo.create(role_data)

        roles = await repo.list()

        assert len(roles) == 4
        assert all(isinstance(role, Role) for role in roles)
        assert {role.name for role in roles} == {"admin", "manager", "user", "guest"}

    @pytest.mark.asyncio
    async def test_list_roles_with_pagination(self, db_session: AsyncSession) -> None:
        repo = BaseRepository(Role, db_session)

        for i in range(10):
            role_data = {"name": f"role_{i}"}
            await repo.create(role_data)

        first_page = await repo.list(skip=0, limit=3)
        second_page = await repo.list(skip=3, limit=3)

        assert len(first_page) == 3
        assert len(second_page) == 3

        first_page_names = {role.name for role in first_page}
        second_page_names = {role.name for role in second_page}
        assert first_page_names.isdisjoint(second_page_names)

        assert first_page[0].name == "role_0"
        assert first_page[2].name == "role_2"

        assert second_page[0].name == "role_3"
        assert second_page[2].name == "role_5"

    @pytest.mark.asyncio
    async def test_list_empty_database(self, db_session: AsyncSession) -> None:
        repo = BaseRepository(Role, db_session)

        roles = await repo.list()

        assert len(roles) == 0
        assert roles == []

    @pytest.mark.asyncio
    async def test_update_role(self, db_session: AsyncSession) -> None:
        repo = BaseRepository(Role, db_session)

        role_data = {"name": "old_name"}
        role = await repo.create(role_data)

        update_data = {"name": "new_name"}
        updated_role = await repo.update(role.id, update_data)

        assert updated_role is not None
        assert updated_role.id == role.id
        assert updated_role.name == "new_name"

    @pytest.mark.asyncio
    async def test_update_nonexistent_role(self, db_session: AsyncSession) -> None:
        repo = BaseRepository(Role, db_session)

        update_data = {"name": "new_name"}
        result = await repo.update(99999, update_data)

        assert result is None

    @pytest.mark.asyncio
    async def test_update_partial_data(self, db_session: AsyncSession) -> None:
        repo = BaseRepository(Role, db_session)

        role_data = {"name": "original_name"}
        role = await repo.create(role_data)

        update_data = {"name": "updated_name"}
        updated_role = await repo.update(role.id, update_data)

        assert updated_role is not None
        assert updated_role.name == "updated_name"

    @pytest.mark.asyncio
    async def test_delete_by_id_existing_role(self, db_session: AsyncSession) -> None:
        repo = BaseRepository(Role, db_session)

        role_data = {"name": "role_to_delete"}
        role = await repo.create(role_data)

        deleted = await repo.delete_by_id(role.id)

        assert deleted is True

        deleted_role = await repo.get_by_id(role.id)
        assert deleted_role is None

    @pytest.mark.asyncio
    async def test_delete_by_id_nonexistent_role(self, db_session: AsyncSession) -> None:
        repo = BaseRepository(Role, db_session)

        deleted = await repo.delete_by_id(99999)

        assert deleted is False
