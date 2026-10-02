from sqlmodel import SQLModel, Field
from typing import Optional

class MenuTable(SQLModel, table=True):
    menu_id: Optional[int] = Field(default=None, primary_key=True)
    menu_name: str = Field(index=True, unique=True)
    menu_category: str
    menu_price: int = Field(default=None, ge=1)


class CreateMenu(SQLModel):
    menu_name: str
    menu_category: str
    menu_price: int = Field(default=None, ge=1)


class ReadMenu(SQLModel):
    menu_id: int
    menu_name: str
    menu_category: str
    menu_price: int


class UpdateMenu(SQLModel):
    menu_name: Optional[str] = None
    menu_category: Optional[str] = None
    menu_price: Optional[int] = Field(default=None, ge=1)


class DeleteMenu(SQLModel):
    menu_id: int