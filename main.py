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



@app.get(
    "/",
    tags=["API Information"],
    summary="API Information"
)
def home():
    return {
        "status": "healthy",
        "message": "Welcome to THE SEVENTH SIP Backend API",

        "api": {
            "name": "The Seventh Sip Backend API",
            "version": "1.0.0",
            "description": "Backend API for The Seventh Sip cafe ordering system.",
            "base_url": "http://127.0.0.1:8000",
            "documentation": {
                "swagger": "/docs",
                "redoc": "/redoc"
            }
        },

        "authentication": {
            "admin": "X-API-Key",
            "user": "X-User-Secret"
        },

        "endpoints": {

            "menu": {
                "admin": [
                    {
                        "method": "POST",
                        "path": "/menu/admin/create",
                        "description": "Create a new menu item",
                        "authentication": "Admin"
                    },
                    {
                        "method": "POST",
                        "path": "/menu/admin/create/bulk",
                        "description": "Create multiple menu items",
                        "authentication": "Admin"
                    },
                    {
                        "method": "PATCH",
                        "path": "/menu/admin/update/{menu_id}",
                        "description": "Update a menu item",
                        "authentication": "Admin"
                    },
                    {
                        "method": "DELETE",
                        "path": "/menu/admin/delete/{menu_id}",
                        "description": "Delete a menu item",
                        "authentication": "Admin"
                    }
                ],

                "public": [
                    {
                        "method": "GET",
                        "path": "/menu/list",
                        "description": "List all menu items"
                    },
                    {
                        "method": "GET",
                        "path": "/menu/filter",
                        "description": "Filter menu items by category"
                    },
                    {
                        "method": "GET",
                        "path": "/menu/list/names",
                        "description": "List all menu names"
                    },
                    {
                        "method": "GET",
                        "path": "/menu/list/categories",
                        "description": "List all menu categories"
                    },
                    {
                        "method": "GET",
                        "path": "/menu/list/price",
                        "description": "List menu items by price"
                    },
                    {
                        "method": "GET",
                        "path": "/menu/filter/price",
                        "description": "Filter menu items by price range"
                    }
                ]
            },

            "users": {
                "user": [
                    {
                        "method": "POST",
                        "path": "/users/register",
                        "description": "Register a new user"
                    },
                    {
                        "method": "POST",
                        "path": "/users/login",
                        "description": "Login user"
                    },
                    {
                        "method": "PATCH",
                        "path": "/users/update",
                        "description": "Update current user's details",
                        "authentication": "User"
                    }
                ],

                "admin": [
                    {
                        "method": "GET",
                        "path": "/users/admin/list",
                        "description": "List all users",
                        "authentication": "Admin"
                    },
                    {
                        "method": "GET",
                        "path": "/users/admin/list/usernames",
                        "description": "List all usernames",
                        "authentication": "Admin"
                    },
                    {
                        "method": "GET",
                        "path": "/users/admin/{user_id}",
                        "description": "Get user by ID",
                        "authentication": "Admin"
                    },
                    {
                        "method": "DELETE",
                        "path": "/users/admin/delete/{user_id}",
                        "description": "Delete user",
                        "authentication": "Admin"
                    }
                ]
            },

            "addons": {
                "public": [
                    {
                        "method": "GET",
                        "path": "/addons/menu/{menu_id}",
                        "description": "Get add-ons for a menu item"
                    }
                ],

                "admin": [
                    {
                        "method": "POST",
                        "path": "/addons/admin/create",
                        "description": "Create a new add-on",
                        "authentication": "Admin"
                    },
                    {
                        "method": "PATCH",
                        "path": "/addons/admin/update/{addon_id}",
                        "description": "Update an add-on",
                        "authentication": "Admin"
                    },
                    {
                        "method": "DELETE",
                        "path": "/addons/admin/delete/{addon_id}",
                        "description": "Delete an add-on",
                        "authentication": "Admin"
                    }
                ]
            },

            "orders": {
                "user": [
                    {
                        "method": "POST",
                        "path": "/orders/create",
                        "description": "Create a new order",
                        "authentication": "User"
                    },
                    {
                        "method": "GET",
                        "path": "/orders/my-orders",
                        "description": "Get authenticated user's orders",
                        "authentication": "User"
                    },
                    {
                        "method": "GET",
                        "path": "/orders/{order_id}",
                        "description": "Get a specific order",
                        "authentication": "User"
                    },
                    {
                        "method": "PATCH",
                        "path": "/orders/{order_id}/cancel",
                        "description": "Cancel a pending order",
                        "authentication": "User"
                    }
                ],

                "admin": [
                    {
                        "method": "PATCH",
                        "path": "/orders/admin/{order_id}/status",
                        "description": "Update order status",
                        "authentication": "Admin"
                    }
                ]
            }
        },

        "order_status": [
            "pending",
            "confirmed",
            "preparing",
            "on_the_way",
            "delivered",
            "canceled"
        ],

        "quick_start": {
            "1": "Open /docs for interactive Swagger documentation",
            "2": "Register a user using POST /users/register",
            "3": "Use the returned secret key as X-User-Secret",
            "4": "Use X-API-Key for admin endpoints",
            "5": "Create orders using POST /orders/create"
        }
    }




if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
