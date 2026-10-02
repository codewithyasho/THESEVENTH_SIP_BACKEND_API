from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    errors = []

    for error in exc.errors():

        field = error["loc"][-1]

        if field == "item_price":
            message = "Price must be greater than 0"
        else:
            message = error["msg"]

        errors.append({
            "field": field,
            "message": message
        })

    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "errors": errors
        }
    )


async def integrity_exception_handler(
    request: Request,
    exc: IntegrityError
):
    return JSONResponse(
        status_code=409,
        content={
            "status": "error",
            "message": "Menu item name already exists"
        }
    )