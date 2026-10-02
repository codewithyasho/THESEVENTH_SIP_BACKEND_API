from dotenv import load_dotenv
from fastapi import Header, HTTPException, Depends
from sqlmodel import Session, select
import os

from src.database import get_session
from models.user import UserTable


load_dotenv()

ADMIN_SECRET = os.getenv("ADMIN_SECRET")


# -----------------------------
# ADMIN API KEY AUTHENTICATION
# -----------------------------

def verify_api_key(
    x_api_key: str = Header()
):
    if x_api_key != ADMIN_SECRET:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )

    return x_api_key


# -----------------------------
# USER SECRET KEY AUTHENTICATION
# -----------------------------

def get_current_user(
    x_user_secret: str = Header(..., alias="X-User-Secret"),
    session: Session = Depends(get_session)
):
    user = session.exec(
        select(UserTable).where(
            UserTable.secret_key == x_user_secret
        )
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid user secret key"
        )

    return user