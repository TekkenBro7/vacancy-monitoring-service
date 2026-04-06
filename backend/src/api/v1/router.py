from fastapi import APIRouter

from src.api.v1.auth import router as auth_router
from src.api.v1.bookmarks import router as bookmarks_router
from src.api.v1.cities import router as cities_router
from src.api.v1.comments import router as comments_router
from src.api.v1.companies import router as companies_router
from src.api.v1.comparisons import router as comparisons_router
from src.api.v1.currency import router as currencies_router
from src.api.v1.roles import router as roles_router
from src.api.v1.search_queries import router as search_queries_router
from src.api.v1.skills import router as skills_router
from src.api.v1.source_types import router as source_types_router
from src.api.v1.sources import router as sources_router
from src.api.v1.user_profiles import router as user_profiles_router
from src.api.v1.users import router as users_router
from src.api.v1.vacancies import router as vacancies_router

v1_router = APIRouter()
v1_router.include_router(users_router, prefix="/users", tags=["Users"])
v1_router.include_router(roles_router, prefix="/roles", tags=["Roles"])
v1_router.include_router(user_profiles_router, prefix="/user_profiles", tags=["User_profiles"])
v1_router.include_router(currencies_router, prefix="/currencies", tags=["Currencies"])
v1_router.include_router(source_types_router, prefix="/source_types", tags=["Source_types"])
v1_router.include_router(sources_router, prefix="/sources", tags=["Sources"])
v1_router.include_router(cities_router, prefix="/cities", tags=["Cities"])
v1_router.include_router(search_queries_router, prefix="/search_queries", tags=["Search_queries"])
v1_router.include_router(companies_router, prefix="/companies", tags=["Companies"])
v1_router.include_router(vacancies_router, prefix="/vacancies", tags=["Vacancies"])
v1_router.include_router(comments_router, prefix="/comments", tags=["Comments"])
v1_router.include_router(comparisons_router, prefix="/comparisons", tags=["Comparisons"])
v1_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
v1_router.include_router(skills_router, prefix="/skills", tags=["Skills"])
v1_router.include_router(bookmarks_router, prefix="/bookmarks", tags=["Bookmarks"])
