from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class UserBase(BaseModel):
    email: EmailStr = Field(..., title="User Email Address", min_length=5)
    password: str = Field(
        ...,
        title="User Password",
        min_length=8,
        max_length=128,
        description="Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number, and one special character."
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str) -> str:
        pattern = r"^[A-Za-z\d@$!%*?&]{8,128}$"  # Только латиница, цифры и спецсимволы
        if not re.match(pattern, password):
            raise ValueError("Password must be at least 8 characters long and must not contain Cyrillic letters.")
        return password


# Модель, которая будет включать данные пользователя и токен
class TokenResponse(BaseModel):
    access_token: str = Field(..., title="Access Token")
    token_type: str = Field("bearer", title="Token Type")

    class Config:
        orm_mode = True


class RegistrationResponse(BaseModel):
    status: str = "success"  # Статус регистрации
    message: str  # Сообщение для пользователя

    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Registration successful. Please check your email to confirm."
            }
        }

class LogoutResponseSchema(BaseModel):
    message: str
    user_email: str

class VerifyCode(BaseModel):
    code: str  # Тип string для кода

    @field_validator("code")
    @classmethod
    def check_digits(cls, value):
        if not value.isdigit():
            raise ValueError('Code must contain only digits')
        if len(value) != 6:
            raise ValueError('Code must be exactly 6 digits')
        return value

class VerificationResponseSchema(BaseModel):
    message: str
    user_email: str

    class Config:
        orm_mode = True

class UserMail(BaseModel):
    email: EmailStr = Field(..., title="User Email Address", min_length=5)

class UserInfoResponse(BaseModel):
    isVerified:bool
