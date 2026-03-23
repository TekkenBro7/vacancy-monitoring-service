from sqlalchemy import select

from src.database.repositories.base_repository import BaseRepository
from src.models.skills import Skill


class SkillRepository(BaseRepository[Skill]):
    async def get_by_name(self, name: str) -> Skill | None:
        query = select(Skill).where(Skill.name.ilike(name))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_or_create(self, name: str) -> tuple[Skill, bool]:
        skill = await self.get_by_name(name)

        if skill:
            return skill, False

        skill = Skill(name=name)
        self.session.add(skill)
        await self.session.flush()
        return skill, True

    async def get_or_create_many(self, names: list[str]) -> list[Skill]:
        skills = []

        for name in names:
            if not name or not name.strip():
                continue

            skill, _ = await self.get_or_create(name.strip())
            skills.append(skill)

        return skills
