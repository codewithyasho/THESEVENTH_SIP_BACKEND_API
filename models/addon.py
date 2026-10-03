from typing import Optional

from sqlmodel import SQLModel, Field


# =========================
# ADD-ON DATABASE MODEL
# =========================

class AddonTable(SQLModel, table=True):
    addon_id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    menu_id: int = Field(
        foreign_key="menutable.menu_id",
        index=True
    )

    name: str = Field(
        min_length=1,
        index=True
    )

    price: float = Field(
        ge=0
    )


# =========================
# CREATE ADD-ON
# =========================

class CreateAddon(SQLModel):
    menu_id: int
    name: str = Field(
        min_length=1
    )
    price: float = Field(
        ge=0
    )


# =========================
# UPDATE ADD-ON
# =========================

class UpdateAddon(SQLModel):
    name: Optional[str] = Field(
        default=None,
        min_length=1
    )

    price: Optional[float] = Field(
        default=None,
        ge=0
    )


# =========================
# READ ADD-ON
# =========================

class ReadAddon(SQLModel):
    addon_id: int
    menu_id: int
    name: str
    price: float