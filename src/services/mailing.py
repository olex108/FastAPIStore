#services/mailing.py
import logging
from email.message import EmailMessage
from pathlib import Path
from typing import Optional, List, Dict
from aiosmtplib import send
from src.config.settings import get_settings
from src.config.tkq import broker

settings = get_settings()
debug_logger = logging.getLogger("debug")


@broker.task
async def send_email_task(
        subject: str,
        recipient: str,
        body: str,
        file_path: str,
        is_html: bool = False,
        attachments: Optional[List[Dict]] = None  # Список словарей с контентом файла
):
    """
    Универсальная таска для отправки почты.
    attachments: [{"filename": "invoice.xlsx", "content": b"...", "maintype": "application", "subtype": "..."}]
    """

    debug_logger.info(f"--- Create mailing task to email {recipient} ---")
    message = EmailMessage()
    message["From"] = settings.SMTP.SMTP_USER
    message["To"] = recipient
    message["Subject"] = subject

    if is_html:
        message.set_content("Пожалуйста, используйте клиент с поддержкой HTML")
        message.add_alternative(body, subtype="html")

    else:
        message.set_content(body)

    if file_path:
        with open(file_path, "rb") as f:
            content = f.read()

        debug_logger.info(f"--- Opened file with path: {file_path} ---")

        message.add_attachment(
            content,
            maintype="application",
            subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=Path(file_path).name
        )

    # Добавляем вложения, если они есть
    if attachments:
        for att in attachments:
            message.add_attachment(
                att["content"],
                maintype=att.get("maintype", "application"),
                subtype=att.get("subtype", "octet-stream"),
                filename=att["filename"]
            )

    try:
        await send(
            message,
            hostname=settings.SMTP.SMTP_HOST,
            port=settings.SMTP.SMTP_PORT,
            username=settings.SMTP.SMTP_USER,
            password=settings.SMTP.SMTP_PASS,
            use_tls=(settings.SMTP.SMTP_PORT == 465),
            start_tls=(settings.SMTP.SMTP_PORT == 587),
        )
        debug_logger.info(f"--- Email sent to {recipient} ---")

    except Exception as e:
        debug_logger.error(f"--- Failed to send email: {e} ---")
        raise e  # Позволяет Taskiq зафиксировать ошибку