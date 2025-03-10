from fastapi import APIRouter, status, BackgroundTasks, Depends, Header
from app.core.security import get_current_user
from sqlalchemy.future import select
from app.db.database import get_db
from app.db.schemas.auth_schemas import *
from app.db.models import User
from app.services.auth_service.token_service import *
from app.services.auth_service.verification_service import *
from app.services.auth_service.password_service import *
from app.services.auth_service.register_service import is_email_registered, create_user

router = APIRouter()


@router.post("/register", response_model=RegistrationResponse)
async def register(
        user: UserBase,
        background_tasks: BackgroundTasks,
        db: AsyncSession = Depends(get_db)
) -> RegistrationResponse:
    if await is_email_registered(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    db_user = await create_user(db, user)
    verification_code = await create_verification_code(db, db_user.id)
    background_tasks.add_task(safe_send_email, user.email, verification_code)
    return RegistrationResponse(message="Registration successful. Please check your email to confirm.")


@router.post("/login", response_model=TokenResponse)
async def login(user: UserBase, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    result = await db.execute(select(User).filter(User.email == user.email))
    db_user = result.scalars().first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email or password"
        )
    access_token = create_access_token(data={"sub": db_user.email})
    return TokenResponse(access_token=access_token, token_type="bearer")


@router.post("/logout", status_code=status.HTTP_200_OK, response_model=LogoutResponseSchema)
async def logout_user(
        user_email: str = Depends(get_current_user),
        authorization: str = Header(...)) -> LogoutResponseSchema:
    token = authorization.replace("Bearer ", "").strip()
    if redis_client.get(f"blacklist:{token}"):
        raise HTTPException(status_code=400, detail="Токен уже недействителен")
    invalidate_access_token(token)
    return LogoutResponseSchema(message="Вы успешно вышли", user_email=user_email)


@router.post("/verify", response_model=VerificationResponseSchema)
async def verify_user(code: VerifyCode, user: UserBase, db: AsyncSession = Depends(get_db)) -> VerificationResponseSchema:
    result = await db.execute(select(VerificationCode).filter(VerificationCode.code == code.code))
    db_code = result.scalars().first()
    if not db_code:
        raise HTTPException(status_code=400, detail="Неверный код верификации")
    user_from_db = db_code.user
    if not user_from_db:
        raise HTTPException(status_code=400, detail="Пользователь не найден")
    if user_from_db.is_verified:
        raise HTTPException(status_code=400, detail="Пользователь уже верифицирован")
    if not pwd_context.verify(user.password, user_from_db.password):
        raise HTTPException(status_code=400, detail="Неверный пароль")
    user_from_db.is_verified = True
    user_from_db.available_generations = 1
    db.add(user_from_db)
    await db.commit()
    await db.refresh(user_from_db)
    return VerificationResponseSchema(message = "Пользователь успешно верифицирован", user_email = user.email)


@router.post("/check_verify")
async def check_verify(user_data: UserMail, db: AsyncSession = Depends(get_db)) -> UserInfoResponse:
    try:
        user_object = await db.execute(select(User).where(User.email == user_data.email))
        user = user_object.scalars().first()  # Извлекаем первого пользователя
        if user:
            return UserInfoResponse(isVerified=user.is_verified)
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

