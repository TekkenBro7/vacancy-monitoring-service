from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.enums import PostgresErrorCode
from src.database.repositories.role_repository import RoleRepository
from src.models.users import Role
from src.schemas.roles import RoleCreate, RoleRead, RoleUpdate


class RoleService:
    def __init__(self, db: AsyncSession):
        self.repo = RoleRepository(Role, db)

    async def list_roles(self) -> list[RoleRead]:
        roles = await self.repo.list()
        return [RoleRead.model_validate(r) for r in roles]

    async def get_role(self, role_id: int) -> RoleRead:
        role = await self.repo.get_by_id(role_id)
        if not role:
            raise HTTPException(404, "Role not found")
        return RoleRead.model_validate(role)

    async def create_role(self, data: RoleCreate) -> RoleRead:
        try:
            role = Role(name=data.name)
            created = await self.repo.create(role)
            return RoleRead.model_validate(created)

        except IntegrityError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Role with this name already exists",
            ) from e

    async def update_role(self, role_id: int, data: RoleUpdate) -> RoleRead:
        role = await self.repo.get_by_id(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role with id {role_id} not found",
            )

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(role, key, value)

        try:
            updated = await self.repo.update(role)
            return RoleRead.model_validate(updated)

        except IntegrityError as e:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Role with this name already exists",
            ) from e

    async def delete_role(self, role_id: int) -> dict[str, bool | int]:
        try:
            deleted = await self.repo.delete_by_id(role_id)
            if not deleted:
                raise HTTPException(status.HTTP_404_NOT_FOUND, f"Role with id {role_id} not found")

            return {"deleted": True, "role_id": role_id}

        except IntegrityError as e:
            if getattr(e.orig, "pgcode", None) == PostgresErrorCode.FOREIGN_KEY_VIOLATION:
                raise HTTPException(
                    status.HTTP_409_CONFLICT,
                    "Cannot delete role: users are assigned to this role",
                ) from e

            raise
