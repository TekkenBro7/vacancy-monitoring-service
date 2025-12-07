from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repositories.base_repository import BaseRepository
from src.models.locations import City, Country
from src.schemas.locations import (
    CityCreate,
    CityRead,
    CityUpdate,
    CountryCreate,
    CountryRead,
    CountryUpdate,
)


class CountryService:
    def __init__(self, db: AsyncSession):
        self.repo = BaseRepository(Country, db)

    async def list_countries(self) -> list[CountryRead]:
        items = await self.repo.list()
        return [CountryRead.model_validate(obj) for obj in items]

    async def get_country(self, country_id: int) -> CountryRead:
        country = await self.repo.get_by_id(country_id)
        if not country:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Country not found")
        return CountryRead.model_validate(country)

    async def create_country(self, data: CountryCreate) -> CountryRead:
        try:
            country = Country(name=data.name)
            country = await self.repo.create(country)
            return CountryRead.model_validate(country)
        except IntegrityError as e:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail="Country with this name already exists",
            ) from e

    async def update_country(self, country_id: int, data: CountryUpdate) -> CountryRead:
        country = await self.repo.get_by_id(country_id)
        if not country:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Country not found")

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(country, key, value)

        try:
            updated = await self.repo.update(country)
            return CountryRead.model_validate(updated)
        except IntegrityError as e:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail="Country update conflict",
            ) from e

    async def delete_country(self, country_id: int) -> dict[str, bool | int]:
        deleted = await self.repo.delete_by_id(country_id)
        if not deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Country not found")
        return {"deleted": True, "country_id": country_id}


class CityService:
    def __init__(self, db: AsyncSession):
        self.repo = BaseRepository(City, db)

    async def list_cities(self) -> list[CityRead]:
        items = await self.repo.list()
        return [CityRead.model_validate(obj) for obj in items]

    async def get_city(self, city_id: int) -> CityRead:
        city = await self.repo.get_by_id(city_id)
        if not city:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "City not found")
        return CityRead.model_validate(city)

    async def create_city(self, data: CityCreate) -> CityRead:
        try:
            city = City(name=data.name, description=data.description, country_id=data.country_id)
            city = await self.repo.create(city)
            return CityRead.model_validate(city)
        except IntegrityError as e:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail="City creation conflict",
            ) from e

    async def update_city(self, city_id: int, data: CityUpdate) -> CityRead:
        city = await self.repo.get_by_id(city_id)
        if not city:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "City not found")

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(city, key, value)

        try:
            updated = await self.repo.update(city)
            return CityRead.model_validate(updated)
        except IntegrityError as e:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail="City update conflict",
            ) from e

    async def delete_city(self, city_id: int) -> dict[str, bool | int]:
        deleted = await self.repo.delete_by_id(city_id)
        if not deleted:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "City not found")
        return {"deleted": True, "city_id": city_id}
