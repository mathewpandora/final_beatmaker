from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func, Text, Float
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime, timezone


class User(Base):

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    total_generations = Column(Integer, default=0, nullable=False)
    available_generations = Column(Integer, default=0, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    verification_codes = relationship("VerificationCode", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User id={self.id}, email={self.email}>"


class VerificationCode(Base):

    __tablename__ = "verification_codes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    code = Column(String(6), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    """
    Добавил lazy="joined" в связь между моделями User и VerificationCode:
    По умолчанию SQLAlchemy загружает связанные объекты только по мере необходимости, что называется lazy loading. Это может привести к ошибке, если сессия закрыта до того, как данные о связанном объекте будут загружены.
    Чтобы избежать этой ошибки, я предложил использовать lazy="joined". Это заставит SQLAlchemy загружать данные о связанном пользователе сразу, когда будет загружен код верификации, и предотвратит ошибку доступа к user после закрытия сессии.
    """
    user = relationship("User", back_populates="verification_codes", lazy="joined")


class Beat(Base):
    __tablename__ = 'beats'

    id = Column(Integer, primary_key=True)  # Первичный ключ
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Владелец бита (внешний ключ, необязательный)
    task_id = Column(String(120), unique=False, nullable=True)  # ID задачи в API генерации
    genre = Column(String(50), nullable=False)  # Жанр бита
    title = Column(String(255), nullable=True, default='')  # Название бита
    status = Column(String(50), nullable=False, default='in_progress')  # Статус бита
    url = Column(String(255), nullable=True)  # Ссылка на сгенерированный бит
    image_url = Column(String(255), nullable=True)  # Ссылка на изображение бита (новое поле)
    created_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Beat id={self.id}, user_id={self.user_id}, genre={self.genre}, title={self.title}, status={self.status}>"


class GenrePrompt(Base):
    """
    Модель для хранения жанров и длинных промптов
    """
    __tablename__ = 'genre_prompts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    genre = Column(String(100), unique=True, nullable=False)  # Название жанра
    prompt = Column(Text, nullable=False)  # Длинный текстовый промпт
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    def __repr__(self):
        return f"<GenrePrompt id={self.id}, genre={self.genre}, prompt={self.prompt[:50]}...>"


class GenerationPackage(Base):
    __tablename__ = 'generation_packages'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)  # Название пакета
    generations_count = Column(Integer, nullable=False)  # Количество генераций в пакете
    price = Column(Float, nullable=False)  # Цена пакета
    image_url = Column(String(255), nullable=True)  # Ссылка на картинку тарифа (добавленный столбец)

    def __repr__(self):
        return f"<GenerationPackage id={self.id}, name={self.name}, generations_count={self.generations_count}, image_url={self.image_url}>"