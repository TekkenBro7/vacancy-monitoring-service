import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repositories.base_repository import BaseRepository
from src.models.users import Role


class TestBaseRepository:
    @pytest.mark.asyncio
    async def test_create_role(self, db_session: AsyncSession) -> None:
        repo = BaseRepository(Role, db_session)

        role = Role(name="admin")
        created_role = await repo.create(role)

        assert created_role.id is not None
        assert created_role.name == "admin"
        assert isinstance(created_role, Role)

    @pytest.mark.asyncio
    async def test_get_by_id_existing_role(self, db_session: AsyncSession) -> None:
        repo = BaseRepository(Role, db_session)

        role = Role(name="manager")
        created_role = await repo.create(role)

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

        roles = [Role(name=name) for name in ["admin", "manager", "user", "guest"]]
        for role in roles:
            await repo.create(role)

        all_roles = await repo.list()

        assert len(all_roles) == 4
        assert all(isinstance(role, Role) for role in all_roles)
        assert {role.name for role in all_roles} == {"admin", "manager", "user", "guest"}

    @pytest.mark.asyncio
    async def test_list_roles_with_pagination(self, db_session: AsyncSession) -> None:
        repo = BaseRepository(Role, db_session)

        for i in range(10):
            role = Role(name=f"role_{i}")
            await repo.create(role)

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

        role = Role(name="old_name")
        created_role = await repo.create(role)

        created_role.name = "new_name"
        updated_role = await repo.update(created_role)

        assert updated_role.id == created_role.id
        assert updated_role.name == "new_name"

    @pytest.mark.asyncio
    async def test_update_nonexistent_role(self, db_session: AsyncSession) -> None:
        repo = BaseRepository(Role, db_session)

        non_existent_role = await repo.get_by_id(99999)

        assert non_existent_role is None

    @pytest.mark.asyncio
    async def test_update_partial_data(self, db_session: AsyncSession) -> None:
        repo = BaseRepository(Role, db_session)

        role = Role(name="original_name")
        role = await repo.create(role)

        role.name = "updated_name"
        updated_role = await repo.update(role)

        assert updated_role is not None
        assert updated_role.name == "updated_name"

    @pytest.mark.asyncio
    async def test_delete_by_id_existing_role(self, db_session: AsyncSession) -> None:
        repo = BaseRepository(Role, db_session)

        role = Role(name="role_to_delete")
        created_role = await repo.create(role)

        deleted = await repo.delete_by_id(created_role.id)
        assert deleted is True

        deleted_role = await repo.get_by_id(created_role.id)
        assert deleted_role is None

    @pytest.mark.asyncio
    async def test_delete_by_id_nonexistent_role(self, db_session: AsyncSession) -> None:
        repo = BaseRepository(Role, db_session)

        deleted = await repo.delete_by_id(99999)

        assert deleted is False
