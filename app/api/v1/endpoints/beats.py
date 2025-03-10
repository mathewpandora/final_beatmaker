from fastapi import APIRouter, BackgroundTasks
from app.services.beat_service.generator import generate_beat_by_genre
from app.services.websocket_service.websokcet_manager import get_manager
from app.services.beat_service.callback_functions import *
from app.services.beat_service.generate_functions import *
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_current_user
from app.db.database import get_db
from app.db.schemas.beat_schemas import *
import dotenv
import os

dotenv.load_dotenv()
TOKEN = os.getenv("LOVEAI_API_TOKEN")

router = APIRouter()


@router.post("/generate", response_model=GenerateResponse)
async def generate(
        genre_data: BaseGenre,
        background_tasks: BackgroundTasks,
        user_email: str = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
) -> GenerateResponse:
    try:
        existing_beat = await get_existing_beat(db, genre_data.genre, user_email)
        if existing_beat:
            await update_user_generations(user_email, db)
            return GenerateResponse(
                message="Existing beat found.",
            )
        await update_user_generations(user_email, db)
        db_genre = await get_genre_prompt(genre_data, db)
        db_user = await get_user_by_email(user_email, db)
        background_tasks.add_task(generate_beat_by_genre, db_genre, db_user, db)
        return GenerateResponse(message="Beat has started generation")
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=500, detail="Redis problem")


@router.get("/callback")
async def get_callback(
        response: ResponseData,
        background_tasks: BackgroundTasks,
        db: AsyncSession = Depends(get_db),
        manager: ConnectionManager = Depends(get_manager),
) -> CallbackResponse:
    beat = await handle_callback(response.data, db)
    background_tasks.add_task(notify_user_about_beat, beat['beat_id'], db, manager)
    return CallbackResponse(message="thanks")
"""
        if beat_id:
            # Используем асинхронную функцию для извлечения email и отправки сообщения
            await notify_user_about_beat(beat_id, db, manager)

        return answer
    except HTTPException as e:
        # Логируем ошибку обработки
        logger.error(f"HTTP error while processing callback: {str(e)}")
        raise e
    except Exception as e:
        # Логируем нештатные ошибки
        logger.error(f"Unexpected error while processing callback: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing data")
"""
