from sqladmin import Admin, ModelView
from app.db.database import engine
from app.db.models import *
from fastapi import FastAPI
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from dotenv import load_dotenv
import os

load_dotenv()


# 🔐 Авторизация для админки
class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        if form["username"] == "admin" and form["password"] == "secret":
            request.session.update({"authenticated": True})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return request.session.get("authenticated", False)


# 📌 Вьюхи для моделей
class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email, User.total_generations, User.is_verified, User.created_at]
    column_searchable_list = [User.email]
    column_sortable_list = [User.id, User.created_at]


class BeatAdmin(ModelView, model=Beat):
    column_list = [Beat.id, Beat.user_id, Beat.genre, Beat.title, Beat.status, Beat.created_at]
    column_sortable_list = [Beat.id, Beat.created_at]
    column_searchable_list = [Beat.title, Beat.genre]


class GenrePromptAdmin(ModelView, model=GenrePrompt):
    column_list = [GenrePrompt.id, GenrePrompt.genre, GenrePrompt.prompt, GenrePrompt.created_at]


class GenerationPackageAdmin(ModelView, model=GenerationPackage):
    column_list = [GenerationPackage.id, GenerationPackage.name, GenerationPackage.generations_count, GenerationPackage.price]


# ⚡ Функция для инициализации админки
def init_admin(app: FastAPI):
    auth_backend = AdminAuth(os.getenv("ADMIN_SECRET_KEY"))
    admin = Admin(app, engine, authentication_backend=auth_backend)

    admin.add_view(UserAdmin)
    admin.add_view(BeatAdmin)
    admin.add_view(GenrePromptAdmin)
    admin.add_view(GenerationPackageAdmin)
