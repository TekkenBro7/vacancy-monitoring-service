from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_async_session
from src.schemas.search_queries import (
    SearchQueryCreate,
    SearchQueryRead,
    SearchQueryUpdate,
)
from src.services.search_query_service import SearchQueryService

router = APIRouter()


def get_search_query_service(
    db: AsyncSession = Depends(get_async_session),
) -> SearchQueryService:
    return SearchQueryService(db)


@router.get("/", response_model=list[SearchQueryRead])
async def list_queries(
    service: SearchQueryService = Depends(get_search_query_service),
) -> list[SearchQueryRead]:
    return await service.list_queries()


@router.get("/{query_id}", response_model=SearchQueryRead)
async def get_query(
    query_id: int,
    service: SearchQueryService = Depends(get_search_query_service),
) -> SearchQueryRead:
    return await service.get_query(query_id)


@router.get("/user/{user_id}", response_model=list[SearchQueryRead])
async def list_queries_by_user(
    user_id: int,
    service: SearchQueryService = Depends(get_search_query_service),
) -> list[SearchQueryRead]:
    return await service.list_user_queries(user_id)


@router.post("/", response_model=SearchQueryRead)
async def create_query(
    data: SearchQueryCreate,
    service: SearchQueryService = Depends(get_search_query_service),
) -> SearchQueryRead:
    return await service.create_query(data)


@router.patch("/{query_id}", response_model=SearchQueryRead)
async def update_query(
    query_id: int,
    data: SearchQueryUpdate,
    service: SearchQueryService = Depends(get_search_query_service),
) -> SearchQueryRead:
    return await service.update_query(query_id, data)


@router.delete("/{query_id}")
async def delete_query(
    query_id: int,
    service: SearchQueryService = Depends(get_search_query_service),
) -> dict[str, bool | int]:
    return await service.delete_query(query_id)
