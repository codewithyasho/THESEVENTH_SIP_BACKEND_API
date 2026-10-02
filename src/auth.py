from dotenv import load_dotenv
from fastapi import Header, HTTPException
import os

load_dotenv()

ADMIN_SECRET = os.getenv("ADMIN_SECRET")


def verify_api_key(x_api_key: str = Header()):
    if x_api_key != ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    return x_api_key
