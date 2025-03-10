from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.v1.endpoints import auth, beats, websocket, user, shop, genres
from app.db.database import engine, Base
from app.admin import init_admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Код, выполняемый при старте приложения (startup)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Код, выполняемый при завершении работы приложения (shutdown)
    await engine.dispose()

"""
Base.metadata.create_all(bind=engine) - при синхронном движке
"""

app = FastAPI(
    title="Beatmaker",
    version="1.0.0",
    description="API для управления пользователями и авторизации",
    lifespan=lifespan
)

# Явное указание типа
app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=["*"],  # Разрешаем все источники
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все методы
    allow_headers=["*"],  # Разрешаем все заголовки
)
init_admin(app)
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(beats.router, prefix="/beats", tags=["Beats"])
app.include_router(websocket.router, prefix="/ws", tags=["Ws"])
app.include_router(user.router, prefix="/user", tags=["User"])
app.include_router(shop.router, prefix="/shop", tags=["Shop"])
app.include_router(genres.router, prefix="/genres", tags=["Genres"])

@app.get("/")
def home():
    return {"message": "Welcome to My FastAPI Project!"}


