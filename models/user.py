from typing import Optional

from pydantic import EmailStr
from sqlmodel import SQLModel, Field


class UserTable(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: EmailStr = Field(index=True, unique=True)
    password: str
    secret_key: str = Field(
    unique=True,
    index=True
)


class UserResponseModel(SQLModel):
    user_id: int
    username: str
    email: EmailStr


class RegisterResponseModel(SQLModel):
    status: str = Field(default="success")
    message: str
    user: UserResponseModel
    secret_key: str


class LoginResponseModel(SQLModel):
    status: str = Field(default="success")
    message: str
    user: UserResponseModel


class RegisterUser(SQLModel):
    username: str = Field(
        min_length=3
    )

    email: EmailStr

    password: str = Field(
        min_length=6
    )


class LoginUser(SQLModel):
    username: str = Field(
        min_length=3
    )

    password: str = Field(
        min_length=6
    )


class ListUsers(SQLModel):
    status: str = Field(default="success")
    count: int
    users: list[UserResponseModel]


class UpdateUser(SQLModel):
    username: Optional[str] = Field(
        default=None,
        min_length=3
    )

    email: Optional[EmailStr] = None

    password: Optional[str] = Field(
        default=None,
        min_length=6
    )
