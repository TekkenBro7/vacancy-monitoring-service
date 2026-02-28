from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_async_session
from src.schemas.roles import RoleCreate, RoleRead, RoleUpdate
from src.services.role_service import RoleService

router = APIRouter()


def get_role_service(
    db: AsyncSession = Depends(get_async_session),
) -> RoleService:
    return RoleService(db)


@router.get("/", response_model=list[RoleRead])
async def list_roles(
    service: RoleService = Depends(get_role_service),
) -> list[RoleRead]:
    return await service.list_roles()


@router.get("/{role_id}/", response_model=RoleRead)
async def get_role(
    role_id: int,
    service: RoleService = Depends(get_role_service),
) -> RoleRead:
    return await service.get_role(role_id)


@router.post("/", response_model=RoleRead)
async def create_role(
    data: RoleCreate,
    service: RoleService = Depends(get_role_service),
) -> RoleRead:
    return await service.create_role(data)


@router.patch("/{role_id}/", response_model=RoleRead)
async def update_role(
    role_id: int,
    data: RoleUpdate,
    service: RoleService = Depends(get_role_service),
) -> RoleRead:
    return await service.update_role(role_id, data)


@router.delete("/{role_id}/")
async def delete_role(
    role_id: int,
    service: RoleService = Depends(get_role_service),
) -> dict[str, bool | int]:
    return await service.delete_role(role_id)
