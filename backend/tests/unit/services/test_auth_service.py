import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException, Response

from src.core.enums import VerificationPurpose
from src.schemas.auth import LoginSchema
from src.services.auth_service import AuthService


@pytest.fixture
def mock_user_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def service(mock_user_service: AsyncMock) -> AuthService:
    return AuthService(mock_user_service)


@pytest.fixture
def mock_response() -> MagicMock:
    return MagicMock(spec=Response)


@pytest.fixture
def mock_user() -> MagicMock:
    user = MagicMock()
    user.id = 1
    user.password_hash = "hashed_password"
    user.role.name = "user"
    user.google_id = None
    return user


class TestLogin:
    @pytest.mark.asyncio
    async def test_successful_login(
        self,
        service: AuthService,
        mock_user_service: AsyncMock,
        mock_response: MagicMock,
        mock_user: MagicMock,
    ) -> None:
        mock_user_service.get_user_by_username.return_value = mock_user

        with (
            patch("src.services.auth_service.verify_password", return_value=True),
            patch(
                "src.services.auth_service.create_access_token",
                return_value="access_token",
            ),
            patch(
                "src.services.auth_service.create_refresh_token",
                return_value="refresh_token",
            ),
            patch("src.services.auth_service.set_refresh_token_cookie") as mock_set_cookie,
        ):
            result = await service.login(
                LoginSchema(username="testuser", password="password123"),
                mock_response,
            )

        assert result.access_token == "access_token"
        mock_set_cookie.assert_called_once()

    @pytest.mark.asyncio
    async def test_login_user_not_found(
        self,
        service: AuthService,
        mock_user_service: AsyncMock,
        mock_response: MagicMock,
    ) -> None:
        mock_user_service.get_user_by_username.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await service.login(
                LoginSchema(username="unknown", password="password123"),
                mock_response,
            )

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid credentials"

    @pytest.mark.asyncio
    async def test_login_wrong_password(
        self,
        service: AuthService,
        mock_user_service: AsyncMock,
        mock_response: MagicMock,
        mock_user: MagicMock,
    ) -> None:
        mock_user_service.get_user_by_username.return_value = mock_user

        with patch("src.services.auth_service.verify_password", return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                await service.login(
                    LoginSchema(username="testuser", password="wrong"),
                    mock_response,
                )

        assert exc_info.value.status_code == 401


class TestRefresh:
    @pytest.mark.asyncio
    async def test_successful_refresh(
        self,
        service: AuthService,
        mock_user_service: AsyncMock,
        mock_response: MagicMock,
        mock_user: MagicMock,
    ) -> None:
        mock_request = MagicMock()
        mock_request.cookies.get.return_value = "valid_refresh_token"
        mock_user_service.user_repo.get_user_with_role.return_value = mock_user

        with (
            patch(
                "src.services.auth_service.decode_refresh_token",
                return_value={"sub": "1"},
            ),
            patch(
                "src.services.auth_service.create_access_token",
                return_value="new_access",
            ),
            patch(
                "src.services.auth_service.create_refresh_token",
                return_value="new_refresh",
            ),
            patch("src.services.auth_service.set_refresh_token_cookie"),
        ):
            result = await service.refresh(mock_request, mock_response)

        assert result.access_token == "new_access"

    @pytest.mark.asyncio
    async def test_refresh_no_token(
        self,
        service: AuthService,
        mock_response: MagicMock,
    ) -> None:
        mock_request = MagicMock()
        mock_request.cookies.get.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await service.refresh(mock_request, mock_response)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "No refresh token"

    @pytest.mark.asyncio
    async def test_refresh_user_not_found(
        self,
        service: AuthService,
        mock_user_service: AsyncMock,
        mock_response: MagicMock,
    ) -> None:
        mock_request = MagicMock()
        mock_request.cookies.get.return_value = "valid_token"
        mock_user_service.user_repo.get_user_with_role.return_value = None

        with patch(
            "src.services.auth_service.decode_refresh_token",
            return_value={"sub": "999"},
        ):
            with pytest.raises(HTTPException) as exc_info:
                await service.refresh(mock_request, mock_response)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "User not found"


class TestLogout:
    @pytest.mark.asyncio
    async def test_logout_clears_cookie(
        self,
        service: AuthService,
        mock_response: MagicMock,
    ) -> None:
        with patch("src.services.auth_service.clear_refresh_token_cookie") as mock_clear:
            result = await service.logout(mock_response)

        assert result["message"] == "Successfully logged out"
        mock_clear.assert_called_once_with(mock_response)


class TestGoogleAuth:
    @pytest.mark.asyncio
    async def test_google_auth_existing_user(
        self,
        service: AuthService,
        mock_user_service: AsyncMock,
        mock_response: MagicMock,
        mock_user: MagicMock,
    ) -> None:
        mock_user_service.get_by_google_id.return_value = mock_user

        with (
            patch(
                "src.services.auth_service.exchange_code_for_token",
                new_callable=AsyncMock,
                return_value={"access_token": "google_token"},
            ),
            patch(
                "src.services.auth_service.get_google_user_info",
                new_callable=AsyncMock,
                return_value={"sub": "google123", "email": "test@gmail.com", "name": "Test"},
            ),
            patch(
                "src.services.auth_service.create_access_token",
                return_value="access_token",
            ),
            patch(
                "src.services.auth_service.create_refresh_token",
                return_value="refresh_token",
            ),
        ):
            token, refresh = await service.google_auth("auth_code", mock_response)

        assert token.access_token == "access_token"
        assert refresh == "refresh_token"

    @pytest.mark.asyncio
    async def test_google_auth_creates_new_user(
        self,
        service: AuthService,
        mock_user_service: AsyncMock,
        mock_response: MagicMock,
        mock_user: MagicMock,
    ) -> None:
        mock_user_service.get_by_google_id.return_value = None
        mock_user_service.get_by_email.return_value = None
        mock_user_service.create_google_user.return_value = mock_user

        with (
            patch(
                "src.services.auth_service.exchange_code_for_token",
                new_callable=AsyncMock,
                return_value={"access_token": "google_token"},
            ),
            patch(
                "src.services.auth_service.get_google_user_info",
                new_callable=AsyncMock,
                return_value={"sub": "google123", "email": "new@gmail.com", "name": "New User"},
            ),
            patch(
                "src.services.auth_service.create_access_token",
                return_value="access_token",
            ),
            patch(
                "src.services.auth_service.create_refresh_token",
                return_value="refresh_token",
            ),
        ):
            token, refresh = await service.google_auth("auth_code", mock_response)

        assert token.access_token == "access_token"
        assert refresh == "refresh_token"
        mock_user_service.create_google_user.assert_called_once()

    @pytest.mark.asyncio
    async def test_google_auth_attaches_google_id_to_existing_user(
        self,
        service: AuthService,
        mock_user_service: AsyncMock,
        mock_response: MagicMock,
        mock_user: MagicMock,
    ) -> None:
        mock_user.google_id = None
        mock_user_service.get_by_google_id.return_value = None
        mock_user_service.get_by_email.return_value = mock_user
        mock_user_service.attach_google_account.return_value = mock_user

        with (
            patch(
                "src.services.auth_service.exchange_code_for_token",
                new_callable=AsyncMock,
                return_value={"access_token": "google_token"},
            ),
            patch(
                "src.services.auth_service.get_google_user_info",
                new_callable=AsyncMock,
                return_value={
                    "sub": "google123",
                    "email": "existing@gmail.com",
                    "name": "Existing",
                },
            ),
            patch(
                "src.services.auth_service.create_access_token",
                return_value="access_token",
            ),
            patch(
                "src.services.auth_service.create_refresh_token",
                return_value="refresh_token",
            ),
        ):
            token, refresh = await service.google_auth("auth_code", mock_response)

        assert token.access_token == "access_token"
        assert refresh == "refresh_token"
        mock_user_service.attach_google_account.assert_called_once_with(
            user=mock_user,
            google_id="google123",
        )
        mock_user_service.create_google_user.assert_not_called()


class TestSendCode:
    @pytest.mark.asyncio
    async def test_send_code_register_success(
        self,
        service: AuthService,
        mock_user_service: AsyncMock,
    ) -> None:
        mock_user_service.get_by_email.return_value = None

        with (
            patch("src.services.auth_service.redis_client.set", new_callable=AsyncMock),
            patch("src.services.auth_service.hash_password", return_value="hashed"),
            patch(
                "src.services.auth_service.EmailVerificationService.send_code",
                new_callable=AsyncMock,
            ),
        ):
            result = await service.send_code(
                email="test@example.com",
                purpose=VerificationPurpose.REGISTER,
                password="password123",
                username="testuser",
            )

        assert result.message == "Verification code sent"

    @pytest.mark.asyncio
    async def test_send_code_register_missing_password(
        self,
        service: AuthService,
    ) -> None:
        with pytest.raises(HTTPException) as exc_info:
            await service.send_code(
                email="test@example.com",
                purpose=VerificationPurpose.REGISTER,
                password=None,
                username="testuser",
            )

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Password required"

    @pytest.mark.asyncio
    async def test_send_code_register_missing_username(
        self,
        service: AuthService,
    ) -> None:
        with pytest.raises(HTTPException) as exc_info:
            await service.send_code(
                email="test@example.com",
                purpose=VerificationPurpose.REGISTER,
                password="password123",
                username=None,
            )

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Username required"

    @pytest.mark.asyncio
    async def test_send_code_register_user_exists(
        self,
        service: AuthService,
        mock_user_service: AsyncMock,
        mock_user: MagicMock,
    ) -> None:
        mock_user_service.get_by_email.return_value = mock_user

        with pytest.raises(HTTPException) as exc_info:
            await service.send_code(
                email="test@example.com",
                purpose=VerificationPurpose.REGISTER,
                password="password123",
                username="testuser",
            )

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "User already exists"

    @pytest.mark.asyncio
    async def test_send_code_add_password_success(
        self,
        service: AuthService,
        mock_user_service: AsyncMock,
        mock_user: MagicMock,
    ) -> None:
        mock_user.password_hash = None
        mock_user_service.get_by_email.return_value = mock_user

        with (
            patch("src.services.auth_service.redis_client.set", new_callable=AsyncMock),
            patch("src.services.auth_service.hash_password", return_value="hashed"),
            patch(
                "src.services.auth_service.EmailVerificationService.send_code",
                new_callable=AsyncMock,
            ),
        ):
            result = await service.send_code(
                email="test@example.com",
                purpose=VerificationPurpose.ADD_PASSWORD,
                password="password123",
            )

        assert result.message == "Verification code sent"

    @pytest.mark.asyncio
    async def test_send_code_add_password_already_set(
        self,
        service: AuthService,
        mock_user_service: AsyncMock,
        mock_user: MagicMock,
    ) -> None:
        mock_user.password_hash = "existing_hash"
        mock_user_service.get_by_email.return_value = mock_user

        with pytest.raises(HTTPException) as exc_info:
            await service.send_code(
                email="test@example.com",
                purpose=VerificationPurpose.ADD_PASSWORD,
                password="password123",
            )

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Password already set"


class TestVerifyCode:
    @pytest.mark.asyncio
    async def test_verify_code_register_success(
        self,
        service: AuthService,
        mock_user_service: AsyncMock,
        mock_user: MagicMock,
    ) -> None:
        mock_user_service.get_by_email.return_value = None
        mock_user_service.create_user.return_value = mock_user
        pending_data = json.dumps({"username": "testuser", "password_hash": "hashed"})

        with (
            patch(
                "src.services.auth_service.EmailVerificationService.verify_code",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "src.services.auth_service.redis_client.get",
                new_callable=AsyncMock,
                return_value=pending_data,
            ),
            patch(
                "src.services.auth_service.redis_client.delete",
                new_callable=AsyncMock,
            ),
        ):
            result = await service.verify_code(
                email="test@example.com",
                code="123456",
                purpose=VerificationPurpose.REGISTER,
            )

        assert result.message == "Success"
        mock_user_service.create_user.assert_called_once()

    @pytest.mark.asyncio
    async def test_verify_code_invalid_code(
        self,
        service: AuthService,
    ) -> None:
        with patch(
            "src.services.auth_service.EmailVerificationService.verify_code",
            new_callable=AsyncMock,
            return_value=False,
        ):
            with pytest.raises(HTTPException) as exc_info:
                await service.verify_code(
                    email="test@example.com",
                    code="wrong",
                    purpose=VerificationPurpose.REGISTER,
                )

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Invalid or expired code"

    @pytest.mark.asyncio
    async def test_verify_code_pending_expired(
        self,
        service: AuthService,
    ) -> None:
        with (
            patch(
                "src.services.auth_service.EmailVerificationService.verify_code",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "src.services.auth_service.redis_client.get",
                new_callable=AsyncMock,
                return_value=None,
            ),
        ):
            with pytest.raises(HTTPException) as exc_info:
                await service.verify_code(
                    email="test@example.com",
                    code="123456",
                    purpose=VerificationPurpose.REGISTER,
                )

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Pending request expired"

    @pytest.mark.asyncio
    async def test_verify_code_add_password_success(
        self,
        service: AuthService,
        mock_user_service: AsyncMock,
        mock_user: MagicMock,
    ) -> None:
        mock_user.password_hash = None
        mock_user_service.get_by_email.return_value = mock_user

        with (
            patch(
                "src.services.auth_service.EmailVerificationService.verify_code",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "src.services.auth_service.redis_client.get",
                new_callable=AsyncMock,
                return_value="hashed_password",
            ),
            patch(
                "src.services.auth_service.redis_client.delete",
                new_callable=AsyncMock,
            ),
        ):
            result = await service.verify_code(
                email="test@example.com",
                code="123456",
                purpose=VerificationPurpose.ADD_PASSWORD,
            )

        assert result.message == "Success"
        mock_user_service.set_password_hash.assert_called_once()
