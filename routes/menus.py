from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func
from models.menu import MenuTable, ReadMenu, CreateMenu, UpdateMenu, DeleteMenu
from src.database import get_session
from src.auth import verify_api_key


router = APIRouter(prefix="/menu", tags=["menus"])


# ENDPOINT 1: create new menu
@router.post("/create", response_model=ReadMenu)
def create_menu(
    menu_data: CreateMenu,
    admin_key: str = Depends(verify_api_key),
    session: Session = Depends(get_session)
):

    existing_item = session.exec(
        select(MenuTable).where(
            MenuTable.menu_name == menu_data.menu_name
        )
    ).first()

    if existing_item:
        raise HTTPException(
            status_code=409,
            detail="Menu item with this name already exists"
        )

    new_menu = MenuTable.model_validate(menu_data)

    session.add(new_menu)
    session.commit()
    session.refresh(new_menu)

    return new_menu


# ENDPOINT 2: List all menu
@router.get("/list", response_model=list[ReadMenu])
def list_menu(
    session : Session = Depends(get_session)
):
    query = select(MenuTable)

    result = session.exec(query).all()

    return result


# ENDPOINT 3: update item by id
@router.patch("/update/{menu_id}", response_model=ReadMenu)
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


# ENDPOINT 4: delete item by id
@router.delete("/delete/{menu_id}")
def delete_menu(menu_id: int, session: Session = Depends(get_session), admin_key: str = Depends(verify_api_key)):
    existing_data = session.get(MenuTable, menu_id)

    if not existing_data:
        raise HTTPException(
            status_code=404, detail=f"No menu found for item id: {menu_id}")

    session.delete(existing_data)
    session.commit()

    return {"message": f"Menu item with id '{menu_id}' has been Deleted."}    



