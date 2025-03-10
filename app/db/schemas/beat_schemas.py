from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class BeatSchema(BaseModel):
    id: str
    tags: str
    title: str
    prompt: str
    status: str
    duration: int
    audio_url: str
    image_url: str
    createTime: datetime
    model_name: str
    error_message: Optional[str] = None
    gpt_description_prompt: str

# Модель для общего ответа
class ResponseData(BaseModel):
    msg: str
    code: int
    data: List[BeatSchema]  # Список объектов Beat
    callbackType: str


class GenerateResponse(BaseModel):
    message: str

class CallbackResponse(BaseModel):
    message: str

class BaseGenre(BaseModel):
    genre:str