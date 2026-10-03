from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn
from src.database import init_db
from routes.menus import router as menu_router
from routes.users import router as user_router
from routes.addons import router as addon_router
from routes.orders import router as order_router
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from src.exceptions import validation_exception_handler, integrity_exception_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    print("\nDatabase tables created✅.")
    yield
    print("\nshutting down the app")


app = FastAPI(
    title="THESEVENTH SIP Backend API",
    description="This is the backend API for THESEVENTH SIP project.",
    version="1.0.0",
    docs_url="/docs",
    lifespan=lifespan
)


## ENDPOINTS
app.include_router(menu_router)
app.include_router(user_router)
app.include_router(addon_router)
app.include_router(order_router)


## CUSTOM EXCEPTION HANDLERS
app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler
)

app.add_exception_handler(
    IntegrityError,
    integrity_exception_handler
)


@app.get("/")
def home():
    return {
        "status": "healthy",
        "message": "Welcome to the THESEVENTH SIP Backend API",
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
