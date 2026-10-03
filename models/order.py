from typing import Optional
from datetime import datetime, timezone
from enum import Enum

from sqlmodel import SQLModel, Field


# =========================
# ORDER STATUS
# =========================

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    ON_THE_WAY = "on_the_way"
    DELIVERED = "delivered"
    CANCELED = "canceled"


# =========================
# ORDER TABLE
# =========================

class OrderTable(SQLModel, table=True):

    order_id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    user_id: int = Field(
        foreign_key="usertable.user_id",
        index=True
    )

    total_amount: float = Field(
        default=0,
        ge=0
    )

    status: OrderStatus = Field(
        default=OrderStatus.PENDING
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# =========================
# ORDER ITEM TABLE
# =========================

class OrderMenuTable(SQLModel, table=True):

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    order_id: int = Field(
        foreign_key="ordertable.order_id",
        index=True
    )

    menu_id: int = Field(
        foreign_key="menutable.menu_id",
        index=True
    )

    menu_name: str = Field(
        index=True
    )

    quantity: int = Field(
        gt=0
    )

    price: float = Field(
        gt=0
    )

    # Optional custom instruction
    special_instructions: Optional[str] = None


# =========================
# ORDER ADDON TABLE
# =========================

class OrderAddonTable(SQLModel, table=True):

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    order_item_id: int = Field(
        foreign_key="ordermenutable.id",
        index=True
    )

    addon_id: int = Field(
        foreign_key="addontable.addon_id",
        index=True
    )

    addon_name: str

    price: float = Field(
        ge=0
    )


# =====================================================
# REQUEST MODELS
# =====================================================

class CreateOrderItem(SQLModel):

    menu_id: int

    quantity: int = Field(
        gt=0
    )

    addon_ids: list[int] = Field(
        default_factory=list
    )

    special_instructions: Optional[str] = None


class CreateOrder(SQLModel):

    items: list[CreateOrderItem] = Field(
        min_length=1
    )


class UpdateOrderStatus(SQLModel):

    status: OrderStatus


# =====================================================
# RESPONSE MODELS
# =====================================================

class ReadOrderAddon(SQLModel):

    id: int

    addon_id: int

    addon_name: str

    price: float


class ReadOrderItem(SQLModel):

    id: int

    menu_id: int

    menu_name: str

    quantity: int

    price: float

    special_instructions: Optional[str] = None

    addons: list[ReadOrderAddon] = Field(
        default_factory=list
    )

    item_total: float


class ReadOrder(SQLModel):

    order_id: int

    user_id: int

    total_amount: float

    status: OrderStatus

    created_at: datetime


class ReadOrderWithItems(ReadOrder):

    items: list[ReadOrderItem] = Field(
        default_factory=list
    )