import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import VerificationCode
import os
import secrets
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

async def send_confirmation_email(to_email: str, verification_code: str) -> None:
    """
    Отправляет email с кодом подтверждения на указанный адрес.

    Аргументы:
        to_email (str): Адрес получателя.
        verification_code (str): Код подтверждения для отправки.

    Выбрасывает:
        ValueError: Если не заданы необходимые SMTP-настройки.
        Exception: При ошибке подключения или отправки сообщения.
    """
    smtp_user: Optional[str] = os.getenv("SMTP_USER")
    smtp_password: Optional[str] = os.getenv("SMTP_PASSWORD")
    smtp_server: Optional[str] = os.getenv("SMTP_SERVER")
    smtp_port_str: Optional[str] = os.getenv("SMTP_PORT")

    if not all([smtp_user, smtp_password, smtp_server, smtp_port_str]):
        raise ValueError("SMTP-настройки не заданы в переменных окружения.")

    try:
        smtp_port: int = int(smtp_port_str)
    except ValueError as e:
        raise ValueError("SMTP_PORT должно быть целым числом.") from e

    # Формируем MIME-сообщение
    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg["Subject"] = "Код для подтверждения аккаунта"
    msg.attach(MIMEText(verification_code, "plain"))

    try:
        # Создаем SMTP-клиента без автоматического запуска STARTTLS
        smtp = aiosmtplib.SMTP(
            hostname=smtp_server,
            port=smtp_port,
            use_tls=False,      # Прямое SSL-соединение не используется
            start_tls=False     # Автоматический запуск STARTTLS отключен
        )

        await smtp.connect()
        await smtp.starttls(validate_certs=False)
        await smtp.login(smtp_user, smtp_password)
        await smtp.send_message(msg)
        await smtp.quit()

    except Exception as e:
        raise Exception(f"Ошибка при отправке email: {e}") from e


async def safe_send_email(email: str, code: str) -> None:
    """
    Безопасно отправляет email и выводит минимальное сообщение об успехе или ошибке.

    Аргументы:
        email (str): Адрес получателя.
        code (str): Код подтверждения для отправки.
    """
    try:
        await send_confirmation_email(email, code)
        logger.info("✅ Письмо успешно отправлено!")
    except Exception as e:
        logger.error("❌ Не удалось отправить письмо: %s", e)


def generate_verification_code() -> str:
    """
    Генерирует и возвращает 6-значный код подтверждения.

    Возвращает:
        str: 6-значный код.
    """
    try:
        code = secrets.randbelow(1000000)  # Число от 0 до 999999
        formatted_code = f"{code:06}"  # Код всегда состоит из 6 цифр
        logger.info("✅ Сгенерирован код подтверждения: %s", formatted_code)
        return formatted_code
    except Exception as e:
        logger.error("❌ Ошибка при генерации кода: %s", e)
        raise


async def create_verification_code(db: AsyncSession, user_id: int) -> str:
    code = generate_verification_code()
    db_verification_code = VerificationCode(user_id=user_id, code=code)
    db.add(db_verification_code)
    await db.commit()
    await db.refresh(db_verification_code)
    return code