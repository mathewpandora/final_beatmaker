from pydantic import BaseModel, Field
from typing import List

class UserInfoResponse(BaseModel):
    total_generation: int = Field(..., title="How much user has beat generations", ge=0)
    available_generations: int = Field(..., title="How much available generations user had", ge=0)

class BeatSchema(BaseModel):
    genre: str
    image_url: str
    url: str
    title: str

class BeatsResponse(BaseModel):
    beats: List[BeatSchema]
    total: int
    page: int
    page_size: int


