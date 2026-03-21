from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from src.dependencies.users import get_current_user, validate_access_token


class TestGetCurrentUser:
    @pytest.mark.asyncio
    async def test_returns_user_on_valid_token(self) -> None:
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_user.email = "test@example.com"
        mock_db = AsyncMock()

        with patch(
            "src.dependencies.users.decode_access_token",
            return_value={"sub": "1", "role": "user"},
        ), patch(
            "src.dependencies.users.UserService"
        ) as mock_service_class:
            mock_service = AsyncMock()
            mock_service.get_user_me.return_value = mock_user
            mock_service_class.return_value = mock_service

            with patch(
                "src.schemas.users.UserMe.model_validate",
                return_value=MagicMock(id=1, username="testuser"),
            ) as mock_validate:
                result = await get_current_user(token="valid_token", db=mock_db)

        mock_service.get_user_me.assert_called_once_with(1)
        mock_validate.assert_called_once_with(mock_user)

    @pytest.mark.asyncio
    async def test_raises_401_when_no_subject_in_token(self) -> None:
        mock_db = AsyncMock()

        with patch(
            "src.dependencies.users.decode_access_token",
            return_value={"role": "user"},  # no "sub"
        ):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(token="invalid_token", db=mock_db)

        assert exc_info.value.status_code == 401
        assert "no subject" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_raises_401_on_decode_error(self) -> None:
        mock_db = AsyncMock()

        with patch(
            "src.dependencies.users.decode_access_token",
            side_effect=ValueError("Token expired"),
        ):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(token="expired_token", db=mock_db)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Token expired"

    @pytest.mark.asyncio
    async def test_raises_404_when_user_not_found(self) -> None:
        mock_db = AsyncMock()

        with patch(
            "src.dependencies.users.decode_access_token",
            return_value={"sub": "999", "role": "user"},
        ), patch(
            "src.dependencies.users.UserService"
        ) as mock_service_class:
            mock_service = AsyncMock()
            mock_service.get_user_me.return_value = None
            mock_service_class.return_value = mock_service

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(token="valid_token", db=mock_db)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "User not found"


class TestValidateAccessToken:
    @pytest.mark.asyncio
    async def test_returns_payload_on_valid_token(self) -> None:
        expected_payload = {"sub": "1", "role": "admin"}

        with patch(
            "src.dependencies.users.decode_access_token",
            return_value=expected_payload,
        ):
            result = await validate_access_token(token="valid_token")

        assert result == expected_payload

    @pytest.mark.asyncio
    async def test_raises_401_on_decode_error(self) -> None:
        with patch(
            "src.dependencies.users.decode_access_token",
            side_effect=ValueError("Invalid signature"),
        ):
            with pytest.raises(HTTPException) as exc_info:
                await validate_access_token(token="invalid_token")

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid signature"