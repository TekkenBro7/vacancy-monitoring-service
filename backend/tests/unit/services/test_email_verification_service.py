from unittest.mock import AsyncMock, patch

import pytest
import redis

from src.mail.services.email_verification_service import EmailVerificationService


class TestSendCode:
    @pytest.mark.asyncio
    async def test_send_code_success(self) -> None:
        with (
            patch(
                "src.mail.services.email_verification_service.redis_client.set",
                new_callable=AsyncMock,
            ) as mock_set,
            patch(
                "src.mail.services.email_verification_service.send_verification_email_task"
            ) as mock_task,
            patch.object(EmailVerificationService, "_generate_code", return_value="123456"),
        ):
            await EmailVerificationService.send_code("test@example.com", "register")

        mock_set.assert_called_once()
        mock_task.delay.assert_called_once_with("test@example.com", "123456")

    @pytest.mark.asyncio
    async def test_send_code_stores_with_correct_key(self) -> None:
        with (
            patch(
                "src.mail.services.email_verification_service.redis_client.set",
                new_callable=AsyncMock,
            ) as mock_set,
            patch("src.mail.services.email_verification_service.send_verification_email_task"),
            patch.object(EmailVerificationService, "_generate_code", return_value="654321"),
            patch(
                "src.mail.services.email_verification_service.RedisKeys.verification",
                return_value="email_verification:register:test@example.com",
            ),
        ):
            await EmailVerificationService.send_code("test@example.com", "register")

        call_args = mock_set.call_args
        assert call_args[0][0] == "email_verification:register:test@example.com"
        assert call_args[0][1] == "654321"

    @pytest.mark.asyncio
    async def test_send_code_raises_on_redis_error(self) -> None:
        with (
            patch(
                "src.mail.services.email_verification_service.redis_client.set",
                new_callable=AsyncMock,
                side_effect=redis.RedisError("Connection failed"),
            ),
            patch.object(EmailVerificationService, "_generate_code", return_value="123456"),
        ):
            with pytest.raises(redis.RedisError):
                await EmailVerificationService.send_code("test@example.com", "register")


class TestVerifyCode:
    @pytest.mark.asyncio
    async def test_verify_code_success(self) -> None:
        with (
            patch(
                "src.mail.services.email_verification_service.redis_client.get",
                new_callable=AsyncMock,
                return_value="123456",
            ),
            patch(
                "src.mail.services.email_verification_service.redis_client.delete",
                new_callable=AsyncMock,
            ) as mock_delete,
        ):
            result = await EmailVerificationService.verify_code(
                "test@example.com", "123456", "register"
            )

        assert result is True
        mock_delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_verify_code_wrong_code(self) -> None:
        with (
            patch(
                "src.mail.services.email_verification_service.redis_client.get",
                new_callable=AsyncMock,
                return_value="123456",
            ),
            patch(
                "src.mail.services.email_verification_service.redis_client.delete",
                new_callable=AsyncMock,
            ) as mock_delete,
        ):
            result = await EmailVerificationService.verify_code(
                "test@example.com", "000000", "register"
            )

        assert result is False
        mock_delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_verify_code_not_found(self) -> None:
        with patch(
            "src.mail.services.email_verification_service.redis_client.get",
            new_callable=AsyncMock,
            return_value=None,
        ):
            result = await EmailVerificationService.verify_code(
                "test@example.com", "123456", "register"
            )

        assert result is False

    @pytest.mark.asyncio
    async def test_verify_code_returns_false_on_redis_error(self) -> None:
        with patch(
            "src.mail.services.email_verification_service.redis_client.get",
            new_callable=AsyncMock,
            side_effect=redis.RedisError("Connection failed"),
        ):
            result = await EmailVerificationService.verify_code(
                "test@example.com", "123456", "register"
            )

        assert result is False


class TestGenerateCode:
    def test_generate_code_returns_6_digits(self) -> None:
        code = EmailVerificationService._generate_code()

        assert len(code) == 6
        assert code.isdigit()

    def test_generate_code_in_valid_range(self) -> None:
        for _ in range(10):
            code = EmailVerificationService._generate_code()
            assert 100000 <= int(code) <= 999999
