from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from src.database import get_session
from src.auth import verify_api_key

from models.addon import (
    AddonTable,
    CreateAddon,
    UpdateAddon,
    ReadAddon
)

from models.menu import MenuTable


router = APIRouter(
    prefix="/addons",
    tags=["Backend: Admin Add-ons Management"]
)


# =====================================================
# CREATE ADD-ON
# =====================================================

@router.post(
    "/admin/create",
    response_model=ReadAddon,
    description="Create an add-on for a menu item. Requires admin API key.",
    response_description="Returns the created add-on details.",
)
def create_addon(
    addon_data: CreateAddon,
    session: Session = Depends(get_session),
    api_key: str = Depends(verify_api_key)
):

    menu = session.exec(
        select(MenuTable).where(
            MenuTable.menu_id == addon_data.menu_id
        )
    ).first()

    if not menu:
        raise HTTPException(
            status_code=404,
            detail="Menu item not found"
        )

    new_addon = AddonTable.model_validate(
        addon_data
    )

    session.add(new_addon)
    session.commit()
    session.refresh(new_addon)

    return new_addon


# =====================================================
# GET ADD-ONS FOR MENU
# =====================================================

@router.get(
    "/menu/{menu_id}",
    response_model=list[ReadAddon],
    description="Get all add-ons available for a menu item.",
    response_description="Returns a list of add-ons for the specified menu item.",
    tags=["Frontend: For Users"]
)
def get_menu_addons(
    menu_id: int,
    session: Session = Depends(get_session)
):

    menu = session.exec(
        select(MenuTable).where(
            MenuTable.menu_id == menu_id
        )
    ).first()

    if not menu:
        raise HTTPException(
            status_code=404,
            detail="Menu item not found"
        )

    addons = session.exec(
        select(AddonTable).where(
            AddonTable.menu_id == menu_id
        )
    ).all()

    return addons


# =====================================================
# UPDATE ADD-ON
# =====================================================

@router.patch(
    "/admin/update/{addon_id}",
    response_model=ReadAddon,
    description="Update an add-on. Requires admin API key."
)
def update_addon(
    addon_id: int,
    update_data: UpdateAddon,
    session: Session = Depends(get_session),
    api_key: str = Depends(verify_api_key)
):

    addon = session.exec(
        select(AddonTable).where(
            AddonTable.addon_id == addon_id
        )
    ).first()

    if not addon:
        raise HTTPException(
            status_code=404,
            detail="Add-on not found"
        )

    update_fields = update_data.model_dump(
        exclude_unset=True
    )

    if not update_fields:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update"
        )

    for key, value in update_fields.items():
        setattr(addon, key, value)

    session.add(addon)
    session.commit()
    session.refresh(addon)

    return addon


# =====================================================
# DELETE ADD-ON
# =====================================================

@router.delete(
    "/admin/delete/{addon_id}",
    description="Delete an add-on. Requires admin API key."
)
def delete_addon(
    addon_id: int,
    session: Session = Depends(get_session),
    api_key: str = Depends(verify_api_key)
):

    addon = session.exec(
        select(AddonTable).where(
            AddonTable.addon_id == addon_id
        )
    ).first()

    if not addon:
        raise HTTPException(
            status_code=404,
            detail="Add-on not found"
        )

    session.delete(addon)
    session.commit()

    return {
        "status": "success",
        "message": "Add-on deleted successfully.",
        "addon_id": addon_id
    }