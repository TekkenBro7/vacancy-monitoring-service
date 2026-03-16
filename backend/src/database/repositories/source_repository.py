from datetime import date

from sqlalchemy import select, update

from src.database.repositories.base_repository import BaseRepository
from src.models.sources import Source


class SourceRepository(BaseRepository[Source]):
    async def get_by_name(self, name: str) -> Source | None:
        query = select(Source).where(Source.name == name)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_last_successful_parse_date(
        self,
        source_id: int,
        parsed_date: date,
    ):
        stmt = (
            update(Source)
            .where(Source.id == source_id)
            .where(
                (Source.last_successful_parse_date == None)
                | (Source.last_successful_parse_date < parsed_date)
            )
            .values(last_successful_parse_date=parsed_date)
        )

        await self.session.execute(stmt)
        await self.session.commit()
