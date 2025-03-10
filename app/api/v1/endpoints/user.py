from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.future import select
from fastapi.params import Depends
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.schemas.user_schemas import UserInfoResponse
from app.core.security import get_current_user
from app.services.beat_service.generate_functions import get_user_by_email
from app.db.schemas.user_schemas import BeatSchema, BeatsResponse
from app.db.database import get_db
from app.db.models import Beat, User

router = APIRouter()


@router.post("/user_info")
async def get_user_info(user_email: str = Depends(get_current_user),
                  db: AsyncSession = Depends(get_db)) -> UserInfoResponse:
    user = await get_user_by_email(user_email, db)

    if user:
        return UserInfoResponse(total_generation=user.total_generations, available_generations=user.available_generations)
    else:
        raise HTTPException(status_code=400, detail="User not found")


@router.post("/get_beats")
async def get_user_beats(
        user_email: str = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
        page: Optional[int] = Query(None, alias="page", ge=1),
        page_size: Optional[int] = Query(5, alias="page_size", ge=1, le=100),
) -> BeatsResponse:
    user_object = await db.execute(select(User).where(User.email == user_email))
    user = user_object.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Добавляем сортировку по убыванию времени создания
    beats_query = select(Beat).where(Beat.user_id == user.id).order_by(Beat.created_at.desc())

    total_beats_object = await db.execute(select(Beat).where(Beat.user_id == user.id))
    total_beats = total_beats_object.scalars().all()
    total = len(total_beats)

    if page is not None and page_size is not None:
        beats_object = await db.execute(
            beats_query.offset((page - 1) * page_size).limit(page_size)
        )
        beats = beats_object.scalars().all()
    else:
        beats = total_beats

    return BeatsResponse(
        beats=[BeatSchema(**beat.__dict__) for beat in beats],
        total=total,
        page=page,
        page_size=page_size
    )


