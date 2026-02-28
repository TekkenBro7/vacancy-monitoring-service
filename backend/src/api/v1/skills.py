from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_async_session
from src.schemas.skills import SkillCreate, SkillRead, SkillUpdate
from src.services.skill_service import SkillService

router = APIRouter()


def get_skill_service(
    db: AsyncSession = Depends(get_async_session),
) -> SkillService:
    return SkillService(db)


@router.get("/", response_model=list[SkillRead])
async def list_skills(service: SkillService = Depends(get_skill_service)) -> list[SkillRead]:
    return await service.list_skills()


@router.get("/{skill_id}/", response_model=SkillRead)
async def get_skill(
    skill_id: int,
    service: SkillService = Depends(get_skill_service),
) -> SkillRead:
    return await service.get_skill(skill_id)


@router.post("/", response_model=SkillRead)
async def create_skill(
    data: SkillCreate,
    service: SkillService = Depends(get_skill_service),
) -> SkillRead:
    return await service.create_skill(data)


@router.patch("/{skill_id}/", response_model=SkillRead)
async def update_skill(
    skill_id: int,
    data: SkillUpdate,
    service: SkillService = Depends(get_skill_service),
) -> SkillRead:
    return await service.update_skill(skill_id, data)


@router.delete("/{skill_id}/")
async def delete_skill(
    skill_id: int,
    service: SkillService = Depends(get_skill_service),
) -> dict[str, bool | int]:
    return await service.delete_skill(skill_id)
