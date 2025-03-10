from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.db.models import GenrePrompt

router = APIRouter()

@router.get("/get_genres")
async def get_genres(db: AsyncSession = Depends(get_db)):
    genres_object = await db.execute(select(GenrePrompt.genre))
    genres = genres_object.scalars().all()
    return genres