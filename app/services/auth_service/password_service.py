from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, соответствует ли открытый пароль захешированному.

    Аргументы:
        plain_password (str): Открытый пароль.
        hashed_password (str): Захешированный пароль.

    Возвращает:
        bool: True, если пароли совпадают, иначе False.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Хеширует пароль с использованием алгоритма bcrypt.

    Аргументы:
        password (str): Открытый пароль.

    Возвращает:
        str: Захешированный пароль.
    """
    return pwd_context.hash(password)