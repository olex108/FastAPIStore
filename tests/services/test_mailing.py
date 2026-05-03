import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.services.mailing import send_email_task


@pytest.mark.asyncio
async def test_send_email_task_success(tmp_path):
    # 1. Создаем временный файл, имитирующий Excel-чек
    test_file = tmp_path / "receipt.xlsx"
    test_file.write_bytes(b"fake excel content")

    # Данные для теста
    subject = "Тестовый заказ"
    recipient = "test@example.com"
    body = "Ваш чек во вложении"
    file_path = str(test_file)

    # 2. Мокаем функцию send из aiosmtplib
    with patch("src.services.mailing.send", new_callable=AsyncMock) as mock_send:
        await send_email_task(
            subject=subject,
            recipient=recipient,
            body=body,
            file_path=file_path
        )

        # 3. Проверки
        # Проверяем, что функция send была вызвана один раз
        assert mock_send.called

        # Вытаскиваем отправленное сообщение из аргументов вызова
        sent_message = mock_send.call_args[0][0]

        assert sent_message["To"] == recipient
        assert sent_message["Subject"] == subject
        # Проверяем наличие вложения
        assert len(sent_message.get_payload()) > 1
        assert sent_message.get_payload()[1].get_filename() == "receipt.xlsx"


@pytest.mark.asyncio
async def test_send_email_task_file_not_found():
    # Проверка поведения при отсутствии файла
    with pytest.raises(FileNotFoundError):
        await send_email_task(
            subject="Error",
            recipient="test@example.com",
            body="Text",
            file_path="non_existent_path.xlsx"
        )


@pytest.mark.asyncio
async def test_send_email_task_smtp_error():
    # Проверка, что исключение SMTP пробрасывается дальше для Taskiq
    with patch("src.services.mailing.send", side_effect=Exception("SMTP Error")):
        with pytest.raises(Exception) as exc:
            await send_email_task(
                subject="Error",
                recipient="test@example.com",
                body="Text",
                file_path=None  # Без файла для простоты
            )
        assert str(exc.value) == "SMTP Error"
