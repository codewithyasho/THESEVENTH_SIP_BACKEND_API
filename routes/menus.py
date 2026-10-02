from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func
from models.menu import MenuTable, MenuResponseModel, CreateMenu, UpdateMenu, CreateBulkMenu, BulkMenuResponse, ReadMenuCount
from src.database import get_session
from src.auth import verify_api_key


router = APIRouter(prefix="/menu", tags=["Admin Menu Management"])


# ENDPOINT 1: create new menu
@router.post(
    "/create", 
    response_model=MenuResponseModel,
    description="Create a new menu item. Requires admin API key.",
    response_description="Returns the created menu item.",
    summary="Create a new menu item"
)
def create_menu(
    menu_data: CreateMenu,
    admin_key: str = Depends(verify_api_key),
    session: Session = Depends(get_session)
):
    # Check if the menu item already exists
    existing_menu = session.exec(
        select(MenuTable).where(
            MenuTable.menu_name == menu_data.menu_name
        )
    ).first()

    if existing_menu:
        raise HTTPException(
            status_code=409,
            detail="Menu item with this name already exists"
        )

    new_menu = MenuTable.model_validate(menu_data)

    session.add(new_menu)
    session.commit()
    session.refresh(new_menu)

    return new_menu


# Endpoitn 2: create bulk menu
@router.post(
    "/create/bulk",
    response_model=BulkMenuResponse,
    description="Create multiple menu items in bulk. Requires admin API key.",
    response_description="Returns the list of created menu items.",
    summary="Create multiple menu items in bulk"
)
def create_bulk_menu(
    bulk_menu_data: CreateBulkMenu,
    admin_key: str = Depends(verify_api_key),
    session: Session = Depends(get_session)
):

    new_menus = []

    for menu_data in bulk_menu_data.menus:

        existing_menu = session.exec(
            select(MenuTable).where(
                MenuTable.menu_name == menu_data.menu_name
            )
        ).first()

        if existing_menu:
            raise HTTPException(
                status_code=409,
                detail=f"Menu item with name '{menu_data.menu_name}' already exists"
            )

        new_menu = MenuTable.model_validate(menu_data)

        new_menus.append(new_menu)

    session.add_all(new_menus)
    session.commit()

    for menu in new_menus:
        session.refresh(menu)

    return {
        "status": "success",
        "count": len(new_menus),
        "menus": new_menus
    }



# ENDPOINT 3: List all menu
@router.get(
    "/list", 
    response_model=ReadMenuCount,
    description="List all menu items. Requires admin API key.",
    response_description="Returns the list of all menu items.",
    summary="List all menu items"
)
def list_menu(
    session : Session = Depends(get_session)
):
    query = select(MenuTable)

    result = session.exec(query).all()

    return {
        "status": "success",
        "count": len(result),
        "menus": result
    }


# ENDPOINT 4: filter menu by category and pagination
@router.get(
    "/filter", 
    response_model=ReadMenuCount,
    description="Filter menu items by category with pagination. Requires admin API key.",
    response_description="Returns the list of filtered menu items.",
    summary="Filter menu items by category with pagination"
)
def filter_menu(
    category: str | None = Query(default=None, description="Enter the category to filter"),
    skip: int = Query(default=0, ge=0, description="Number of menu to skip"),
    limit: int = Query(default=10, ge=1, le=50, description="Max menu to return"),
    session : Session = Depends(get_session)
):  
    if not category:
        raise HTTPException(
            status_code=400, detail="Please provide a category to filter menu.")
    
    query = select(MenuTable)
    
    query = query.where(MenuTable.menu_category == category.lower())

    query = query.offset(skip).limit(limit)

    result = session.exec(query).all()
    return {
        "status": "success",
        "count": len(result),
        "menus": result
    }


# ENDPOINT 5: list all the menu name only.
@router.get(
    "/list/names", 
    description="List all menu names. Requires admin API key.",
    response_description="Returns the list of all menu names.",
    summary="List all menu names"
)
def list_names(session: Session = Depends(get_session)):
    query = select(MenuTable.menu_name).distinct()

    result = session.exec(query).all()

    return {
        "status": "success",
        "count": len(result),
        "menus": result
    }


# ENDPOINT 5.1: list all the categories only.
@router.get(
    "/list/categories",
    description="List all menu categories. Requires admin API key.",
    response_description="Returns the list of all menu categories.",
    summary="List all menu categories"
)
def list_categories(session: Session = Depends(get_session)):
    query = select(MenuTable.menu_category).distinct()

    result = session.exec(query).all()

    return {
        "status": "success",
        "count": len(result),
        "menus": result
    }



# ENDPOINT 6: list menu by price range from lowest to highest
@router.get(
    "/list/price", 
    response_model=ReadMenuCount,
    description="List all menu items sorted by price from lowest to highest. Requires admin API key.",
    response_description="Returns the list of all menu items sorted by price from lowest to highest.",
    summary="List menu items by price"
)
def list_menu_by_price(session: Session = Depends(get_session)):
    query = select(MenuTable).order_by(MenuTable.menu_price.asc())

    result = session.exec(query).all()

    return {
        "status": "success",
        "count": len(result),
        "menus": result
    }


#ENDPOINT 7: filter menu by price range
@router.get(
    "/filter/price", 
    response_model=ReadMenuCount,
    description="Filter menu items by price range.",
    response_description="Returns the list of filtered menu items.",
    summary="Filter menu items by price range"
)
def filter_menu_by_price(
    min_price: int = Query(default=1, ge=1, description="Minimum price to filter"),
    max_price: int = Query(default=1000, ge=1, description="Maximum price to filter"),
    session: Session = Depends(get_session)
):
    if min_price >= max_price:
        raise HTTPException(
            status_code=400, detail="Minimum price cannot be greater than or equal to maximum price.")

    query = select(MenuTable).where(
        MenuTable.menu_price >= min_price,
        MenuTable.menu_price <= max_price
    )

    result = session.exec(query).all()

    return {
        "status": "success",
        "count": len(result),
        "menus": result
    }


# ENDPOINT 8: update item by id
@router.patch(
    "/update/{menu_id}", 
    response_model=MenuResponseModel,
    description="Update a menu item by ID. Requires admin API key.",
    response_description="Returns the updated menu item.",
    summary="Update a menu item by ID"
)
def update_menu(
    menu_id: int,
    update: UpdateMenu,
    admin_key: str = Depends(verify_api_key),
    session: Session = Depends(get_session)
    
):
    exsisting_data = session.get(MenuTable, menu_id)

    if not exsisting_data:
        raise HTTPException(
            status_code=404, detail=f"No menu found for item id: {menu_id}")

    update_data = update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(exsisting_data, key, value)

    session.add(exsisting_data)
    session.commit()
    session.refresh(exsisting_data)

    return exsisting_data


# ENDPOINT 9: delete item by id
@router.delete(
    "/delete/{menu_id}", 
    description="Delete a menu item by ID. Requires admin API key.", 
    response_description="Returns a message confirming the deletion of the menu item.", 
    summary="Delete a menu item by ID"
)
def delete_menu(menu_id: int, session: Session = Depends(get_session), admin_key: str = Depends(verify_api_key)):
    existing_data = session.get(MenuTable, menu_id)

    if not existing_data:
        raise HTTPException(
            status_code=404, detail=f"No menu found for item id: {menu_id}")

    session.delete(existing_data)
    session.commit()

    return {"message": f"Menu item with id '{menu_id}' has been Deleted."}    



