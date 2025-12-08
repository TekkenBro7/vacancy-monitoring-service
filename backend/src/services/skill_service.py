from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repositories.skill_repository import SkillRepository
from src.models.skills import Skill
from src.schemas.skills import SkillCreate, SkillRead, SkillUpdate


class SkillService:
    def __init__(self, db: AsyncSession):
        self.repo = SkillRepository(Skill, db)

    async def list_skills(self) -> list[SkillRead]:
        items = await self.repo.list()
        return [SkillRead.model_validate(obj) for obj in items]

    async def get_skill(self, skill_id: int) -> SkillRead:
        skill = await self.repo.get_by_id(skill_id)
        if not skill:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Skill not found")
        return SkillRead.model_validate(skill)

    async def create_skill(self, data: SkillCreate) -> SkillRead:
        try:
            skill_model = Skill(name=data.name)
            skill = await self.repo.create(skill_model)
            return SkillRead.model_validate(skill)

        except IntegrityError as e:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Skill already exists",
            ) from e

    async def update_skill(self, skill_id: int, data: SkillUpdate) -> SkillRead:
        skill = await self.repo.get_by_id(skill_id)
        if not skill:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Skill not found")

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(skill, key, value)

        try:
            updated = await self.repo.update(skill)
            return SkillRead.model_validate(updated)

        except IntegrityError as e:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Skill update conflict",
            ) from e

    async def delete_skill(self, skill_id: int) -> dict[str, bool | int]:
        deleted = await self.repo.delete_by_id(skill_id)
        if not deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Skill not found")

        return {"deleted": True, "skill_id": skill_id}
