from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repositories.search_query_repository import SearchQueryRepository
from src.models.search import SearchQuery
from src.schemas.search_queries import (
    SearchQueryCreate,
    SearchQueryRead,
    SearchQueryUpdate,
)


class SearchQueryService:
    def __init__(self, db: AsyncSession):
        self.repo = SearchQueryRepository(SearchQuery, db)

    async def list_queries(self) -> list[SearchQueryRead]:
        queries = await self.repo.list()
        return [SearchQueryRead.model_validate(q) for q in queries]

    async def get_query(self, query_id: int) -> SearchQueryRead:
        query = await self.repo.get_by_id(query_id)
        if not query:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Search query not found")

        return SearchQueryRead.model_validate(query)

    async def list_user_queries(self, user_id: int) -> list[SearchQueryRead]:
        queries = await self.repo.get_by_user_id(user_id)
        return [SearchQueryRead.model_validate(q) for q in queries]

    async def create_query(self, data: SearchQueryCreate) -> SearchQueryRead:
        try:
            query = SearchQuery(
                user_id=data.user_id,
                query_text=data.query_text,
            )
            created = await self.repo.create(query)

            return SearchQueryRead.model_validate(created)

        except IntegrityError as e:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "User does not exist - cannot create search query",
            ) from e

    async def update_query(
        self,
        query_id: int,
        data: SearchQueryUpdate,
    ) -> SearchQueryRead:

        query = await self.repo.get_by_id(query_id)
        if not query:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                f"Search query with id {query_id} not found",
            )

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(query, key, value)

        try:
            updated = await self.repo.update(query)
            return SearchQueryRead.model_validate(updated)

        except IntegrityError as e:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Search query update conflict",
            ) from e

    async def delete_query(self, query_id: int) -> dict[str, bool | int]:
        deleted = await self.repo.delete_by_id(query_id)
        if not deleted:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                f"Search query with id {query_id} not found",
            )

        return {"deleted": True, "query_id": query_id}
