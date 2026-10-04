from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func
from sqlalchemy import desc

from src.database import get_session
from src.auth import get_current_user

from models.user import UserTable
from models.menu import MenuTable

from models.addon import AddonTable

from models.order import (
    OrderTable,
    OrderMenuTable,
    OrderAddonTable,
    CreateOrder,
    UpdateOrderStatus,
    ReadOrderWithItems,
    ReadOrderItem,
    ReadOrderAddon,
    OrderStatus,
    ReadOrder
)

from src.auth import (
    get_current_user,
    verify_api_key
)

from datetime import datetime, timezone


## helper function 
def get_order_with_items(
    order: OrderTable,
    session: Session
):

    order_items = session.exec(
        select(OrderMenuTable).where(
            OrderMenuTable.order_id == order.order_id
        )
    ).all()

    response_items = []

    for order_item in order_items:

        addons = session.exec(
            select(OrderAddonTable).where(
                OrderAddonTable.order_item_id
                == order_item.id
            )
        ).all()

        addon_response = [
            ReadOrderAddon(
                id=addon.id,
                addon_id=addon.addon_id,
                addon_name=addon.addon_name,
                price=addon.price
            )
            for addon in addons
        ]

        addon_total = sum(
            addon.price
            for addon in addons
        )

        item_total = (
            (order_item.price + addon_total)
            * order_item.quantity
        )

        response_items.append(
            ReadOrderItem(
                id=order_item.id,
                menu_id=order_item.menu_id,
                menu_name=order_item.menu_name,
                quantity=order_item.quantity,
                price=order_item.price,
                special_instructions=(
                    order_item.special_instructions
                ),
                addons=addon_response,
                item_total=item_total
            )
        )

    return ReadOrderWithItems(
        order_id=order.order_id,
        user_id=order.user_id,
        total_amount=order.total_amount,
        status=order.status,
        created_at=order.created_at,
        items=response_items
    )


router = APIRouter(
    prefix="/orders",
    tags=["Backend: Admin Orders Management"]
)



# ENDPOINT 6: List all orders, admin only
@router.get(
    "/admin/list/all",
    response_model=list[ReadOrderWithItems],
    description="List all orders. Admin access only.",
    response_description="Returns a list of all orders in the system."
)    
def list_all_orders(
    api_key: str = Depends(verify_api_key),
    session: Session = Depends(get_session)
):

    orders = session.exec(
        select(OrderTable)
    ).all()

    return [
        get_order_with_items(
            order,
            session
        )
        for order in orders
    ]



# users/summary: endpoint for the user to see their own order summary, requires user authentication
@router.get(
        "/user/summary",
        description="Get the currently authenticated user's order summary.",
        response_description="Returns the order summary of the currently authenticated user.",
        tags=["Frontend: For Users"]
)
def get_user_order_summary(
    current_user: UserTable = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Get the user's order summary
    total_orders = session.exec(
        select(func.count(OrderTable.order_id)).where(OrderTable.user_id == current_user.user_id)
    ).first()

    pending_orders = session.exec(
        select(func.count(OrderTable.order_id)).where(
            OrderTable.user_id == current_user.user_id,
            OrderTable.status == "PENDING"
        )
    ).first()

    completed_orders = session.exec(
        select(func.count(OrderTable.order_id)).where(
            OrderTable.user_id == current_user.user_id,
            OrderTable.status == "DELIVERED"
        )
    ).first()

    cancelled_orders = session.exec(
        select(func.count(OrderTable.order_id)).where(
            OrderTable.user_id == current_user.user_id,
            OrderTable.status == "CANCELED"
        )
    ).first()

    total_spent = session.exec(
        select(func.sum(OrderTable.total_amount)).where(OrderTable.user_id == current_user.user_id)
    ).first() or 0

    return {
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "completed_orders": completed_orders,
        "cancelled_orders": cancelled_orders,
        "total_spent": total_spent
    }



# ENDPOINT 1: Create Order, user must be logged in to create an order
@router.post(
    "/create",
    response_model=ReadOrderWithItems,
    description="Create an order for the currently authenticated user.",
    response_description="Returns the created order details."
)
def create_order(
    order_data: CreateOrder,
    current_user: UserTable = Depends(get_current_user),
    session: Session = Depends(get_session)
):

    try:

        # ==========================================
        # 1. CHECK DUPLICATE MENU ITEMS
        # ==========================================

        menu_ids = [
            item.menu_id
            for item in order_data.items
        ]

        if len(menu_ids) != len(set(menu_ids)):
            raise HTTPException(
                status_code=400,
                detail="Duplicate menu items are not allowed in the same order."
            )


        # ==========================================
        # 2. CREATE ORDER
        # ==========================================

        new_order = OrderTable(
            user_id=current_user.user_id,
            total_amount=0
        )

        session.add(new_order)
        session.flush()


        # ==========================================
        # 3. VARIABLES
        # ==========================================

        total_amount = 0

        response_items = []

        order_addons = []


        # ==========================================
        # 4. PROCESS EACH ORDER ITEM
        # ==========================================

        for item in order_data.items:

            # --------------------------------------
            # Find menu
            # --------------------------------------

            menu = session.exec(
                select(MenuTable).where(
                    MenuTable.menu_id == item.menu_id
                )
            ).first()

            if not menu:
                raise HTTPException(
                    status_code=404,
                    detail=f"Menu item {item.menu_id} not found."
                )


            # --------------------------------------
            # Create order item
            # --------------------------------------

            order_item = OrderMenuTable(
                order_id=new_order.order_id,
                menu_id=menu.menu_id,

                # IMPORTANT:
                menu_name=menu.menu_name,

                quantity=item.quantity,

                # IMPORTANT:
                price=menu.menu_price,

                special_instructions=item.special_instructions
            )

            session.add(order_item)
            session.flush()


            # ======================================
            # 5. BASE MENU PRICE
            # ======================================

            base_total = (
                menu.menu_price * item.quantity
            )


            # ======================================
            # 6. PROCESS ADD-ONS
            # ======================================

            addon_total = 0

            addon_response = []


            # Check duplicate add-ons
            if len(item.addon_ids) != len(
                set(item.addon_ids)
            ):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Duplicate add-ons are not allowed "
                        f"for '{menu.menu_name}'."
                    )
                )


            for addon_id in item.addon_ids:

                addon = session.exec(
                    select(AddonTable).where(
                        AddonTable.addon_id == addon_id
                    )
                ).first()


                # Add-on doesn't exist
                if not addon:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Add-on {addon_id} not found."
                    )


                # ==================================
                # Make sure addon belongs to menu
                # ==================================

                if addon.menu_id != menu.menu_id:

                    raise HTTPException(
                        status_code=400,
                        detail=(
                            f"Add-on '{addon.name}' "
                            f"is not available for "
                            f"'{menu.menu_name}'."
                        )
                    )


                # ==================================
                # Add-on price
                # ==================================

                addon_total += addon.price


                # ==================================
                # Create order addon snapshot
                # ==================================

                new_order_addon = OrderAddonTable(
                    order_item_id=order_item.id,
                    addon_id=addon.addon_id,
                    addon_name=addon.name,
                    price=addon.price
                )

                order_addons.append(
                    new_order_addon
                )


                # ==================================
                # Response data
                # ==================================

                addon_response.append(
                    {
                        "addon_id": addon.addon_id,
                        "addon_name": addon.name,
                        "price": addon.price
                    }
                )


            # ======================================
            # 7. CALCULATE ITEM TOTAL
            # ======================================

            item_total = (
                menu.menu_price + addon_total
            ) * item.quantity


            total_amount += item_total


            # ======================================
            # 8. SAVE RESPONSE ITEM
            # ======================================

            response_items.append(
                {
                    "order_item": order_item,
                    "addons": addon_response,
                    "item_total": item_total
                }
            )


        # ==========================================
        # 9. SAVE ORDER ADD-ONS
        # ==========================================

        for order_addon in order_addons:
            session.add(order_addon)


        # ==========================================
        # 10. UPDATE ORDER TOTAL
        # ==========================================

        new_order.total_amount = total_amount

        session.add(new_order)

        session.commit()
        session.refresh(new_order)


        # ==========================================
        # 11. BUILD FINAL RESPONSE
        # ==========================================

        final_items = []

        for item_data in response_items:

            order_item = item_data["order_item"]


            addons = session.exec(
                select(OrderAddonTable).where(
                    OrderAddonTable.order_item_id
                    == order_item.id
                )
            ).all()


            addon_response = [
                ReadOrderAddon(
                    id=addon.id,
                    addon_id=addon.addon_id,
                    addon_name=addon.addon_name,
                    price=addon.price
                )
                for addon in addons
            ]


            final_items.append(
                ReadOrderItem(
                    id=order_item.id,
                    menu_id=order_item.menu_id,
                    menu_name=order_item.menu_name,
                    quantity=order_item.quantity,
                    price=order_item.price,
                    special_instructions=(
                        order_item.special_instructions
                    ),
                    addons=addon_response,
                    item_total=item_data["item_total"]
                )
            )


        # ==========================================
        # 12. RETURN ORDER
        # ==========================================

        return ReadOrderWithItems(
            order_id=new_order.order_id,
            user_id=new_order.user_id,
            total_amount=new_order.total_amount,
            status=new_order.status,
            created_at=new_order.created_at,
            items=final_items
        )


    except HTTPException:
        session.rollback()
        raise


    except Exception as e:

        session.rollback()

        print("ORDER CREATION ERROR:", repr(e))

        raise HTTPException(
            status_code=500,
            detail="Failed to create order."
        )


# ENDPOINT 2: Update Order Status, admin only
@router.patch(
    "/admin/{order_id}/status",
    response_model=ReadOrderWithItems,
    description="Update order status. Requires admin API key.",
    response_description="Returns the updated order details."
)
def update_order_status(
    order_id: int,
    update_data: UpdateOrderStatus,
    session: Session = Depends(get_session),
    api_key: str = Depends(verify_api_key)
):

    order = session.exec(
        select(OrderTable).where(
            OrderTable.order_id == order_id
        )
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    order.status = update_data.status

    session.add(order)
    session.commit()
    session.refresh(order)

    return get_order_with_items(
        order,
        session
    )



# ENDPOINT 3: Get all orders of the currently authenticated user
@router.get(
    "/my-orders",
    response_model=list[ReadOrderWithItems],
    description="Get all orders of the currently authenticated user.",
    response_description="Returns a list of orders for the currently authenticated user.",
    tags=["Frontend: For Users"]
)
def get_my_orders(
    current_user: UserTable = Depends(get_current_user),
    session: Session = Depends(get_session)
):

    orders = session.exec(
        select(OrderTable).where(
            OrderTable.user_id == current_user.user_id
        )
    ).all()

    return [
        get_order_with_items(
            order,
            session
        )
        for order in orders
    ]



# multi parameter filtering for users.
# user can filter their orders by status of order with pagination.
@router.get(
    "/my-orders/filter",
    response_model=list[ReadOrderWithItems],
    description="Filter the currently authenticated user's orders by status.",
    response_description="Returns a list of orders filtered by the specified status.",
    tags=["Frontend: For Users"]
)
def filter_my_orders(
    status: OrderStatus = Query(
        ...,
        description="The status to filter orders by."
    ),
    skip: int = Query(
        default=0,
        ge=0,
        description="Number of records to skip for pagination."
    ),
    limit: int = Query(
        default=10,
        le=50,
        description="Maximum number of records to return for pagination."
    ),
    current_user: UserTable = Depends(get_current_user),
    session: Session = Depends(get_session)
):

    orders = session.exec(
        select(OrderTable)
        .where(
            OrderTable.user_id == current_user.user_id,
            OrderTable.status == status
        )
        .offset(skip)
        .limit(limit)
    ).all()

    return [
        get_order_with_items(
            order,
            session
        )
        for order in orders
    ]



# multi parameter filtering for admin.
# admin can filter all orders by status of order with pagination.
@router.get(
        "/admin/list/filter",
        response_model=list[ReadOrderWithItems],
        description="Filter all orders by status.",
        response_description="Returns a list of orders filtered by the specified status.",
)
def filter_all_orders(
    status: OrderStatus = Query(
        ...,
        description="The status to filter orders by."
    ),
    skip: int = Query(
        default=0,
        ge=0,
        description="Number of records to skip for pagination."
    ),
    limit: int = Query(
        default=10,
        le=50,
        description="Maximum number of records to return for pagination."
    ),
    api_key: str = Depends(verify_api_key),
    session: Session = Depends(get_session)
):

    orders = session.exec(
        select(OrderTable)
        .where(OrderTable.status == status)
        .offset(skip)
        .limit(limit)
    ).all()

    return [
            get_order_with_items(
                order,
                session
            )
            for order in orders
        ]


# GET /orders/admin/today Returns today's orders.
@router.get(
    "/admin/today",
    response_model=list[ReadOrderWithItems],
    description="Returns today's orders.",
    response_description="Returns a list of orders created today."
)
def get_todays_orders(
    api_key: str = Depends(verify_api_key),
    session: Session = Depends(get_session)
):

    today = datetime.now(timezone.utc).date()

    orders = session.exec(
        select(OrderTable).where(
            func.date(OrderTable.created_at) == today
        )
    ).all()

    return [
        get_order_with_items(
            order,
            session
        )
        for order in orders
    ]   



# Admin Dashboard Statistics
@router.get(
    "/admin/dashboard",
    response_model=dict,
    description="Returns admin dashboard statistics.",
    response_description="Returns a dictionary containing various statistics for the admin dashboard."
)
def get_admin_dashboard_statistics(
    api_key: str = Depends(verify_api_key),
    session: Session = Depends(get_session)
):

    today = datetime.now(timezone.utc).date()

    total_orders = session.exec(
        select(func.count(OrderTable.order_id))
    ).first()

    today_orders = session.exec(
        select(func.count(OrderTable.order_id)).where(
            func.date(OrderTable.created_at) == today
        )
    ).first()

    pending_orders = session.exec(
        select(func.count(OrderTable.order_id)).where(
            OrderTable.status == "PENDING"
        )
    ).first()

    completed_orders = session.exec(
        select(func.count(OrderTable.order_id)).where(
            OrderTable.status == "DELIVERED"
        )
    ).first()

    cancelled_orders = session.exec(
        select(func.count(OrderTable.order_id)).where(
            OrderTable.status == "CANCELED"
        )
    ).first()

    total_revenue = session.exec(
        select(func.sum(OrderTable.total_amount))
    ).first() or 0

    today_revenue = session.exec(
        select(func.sum(OrderTable.total_amount)).where(
            func.date(OrderTable.created_at) == today
        )
    ).first() or 0

    total_users = session.exec(
        select(func.count(UserTable.user_id))
    ).first()

    return {
        "total_orders": total_orders,
        "today_orders": today_orders,
        "pending_orders": pending_orders,           
        "completed_orders": completed_orders,
        "cancelled_orders": cancelled_orders,
        "total_revenue": total_revenue,
        "today_revenue": today_revenue,
        "total_users": total_users
    }



# ENDPOINT 4: Get order by ID, admin can view any order by order id.
@router.get(
    "/admin/list/{order_id}",
    response_model=ReadOrderWithItems,
    description="Get order details by order ID. Admin access only.",
    response_description="Returns the order details for the specified order ID."
)
def get_order(
    order_id: int,
    api_key: str = Depends(verify_api_key),
    session: Session = Depends(get_session)
):

    order = session.exec(
        select(OrderTable).where(
            OrderTable.order_id == order_id
        )
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return get_order_with_items(
        order,
        session
    )



# ENdPOINT 5: Cancel Order, user must be logged in to cancel their own pending order
@router.patch(
    "/{order_id}/cancel",
    response_model=ReadOrderWithItems,
    description="Cancel the currently authenticated user's pending order.",
    response_description="Returns the updated order details after cancellation.",
    tags=["Frontend: For Users"]
)
def cancel_order(
    order_id: int,
    current_user: UserTable = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # 1. Find the order
    order = session.exec(
        select(OrderTable).where(
            OrderTable.order_id == order_id
        )
    ).first()

    # 2. Order doesn't exist
    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    # 3. Make sure this order belongs to current user
    if order.user_id != current_user.user_id:
        raise HTTPException(
            status_code=403,
            detail="You cannot cancel this order."
        )

    # 4. Only pending orders can be cancelled
    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail="Only pending orders can be canceled."
        )

    # 5. Change status
    order.status = OrderStatus.CANCELED

    session.add(order)
    session.commit()
    session.refresh(order)

    # 6. Return updated order
    return get_order_with_items(
        order,
        session
    )




from datetime import datetime, timedelta, timezone  
from sqlmodel import Session, select, func


@router.get(
    "/analytics/revenue",
    description="Get revenue analytics. Admin access only.",
    response_description="Returns revenue statistics."
)
def revenue_analytics(
    period: str = Query(
        default="daily",
        description="The period for which to fetch revenue data. Must be 'daily', 'weekly', or 'monthly'."
    ),
    api_key: str = Depends(verify_api_key),
    session: Session = Depends(get_session)
):

    now = datetime.now(timezone.utc)

    if period == "daily":

        start_date = now.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

    elif period == "weekly":

        start_date = now - timedelta(days=7)

    elif period == "monthly":

        start_date = now - timedelta(days=30)

    else:

        raise HTTPException(
            status_code=400,
            detail="Period must be daily, weekly or monthly."
        )

    revenue = session.exec(
        select(
            func.sum(OrderTable.total_amount)
        )
        .where(
            OrderTable.created_at >= start_date,
            OrderTable.status == OrderStatus.DELIVERED
        )
    ).one()

    return {
        "period": period,
        "revenue": float(revenue or 0)
    }



# order analytics endpoint for admin to see order statistics by status.
@router.get(
    "/analytics/orders",
    description="Get order statistics by status. Admin access only.",
    response_description="Returns order statistics."
)
def order_analytics(
    api_key: str = Depends(verify_api_key),
    session: Session = Depends(get_session)
):

    pending = session.exec(
        select(func.count(OrderTable.order_id))
        .where(OrderTable.status == OrderStatus.PENDING)
    ).one()

    confirmed = session.exec(
        select(func.count(OrderTable.order_id))
        .where(OrderTable.status == OrderStatus.CONFIRMED)
    ).one()

    preparing = session.exec(
        select(func.count(OrderTable.order_id))
        .where(OrderTable.status == OrderStatus.PREPARING)
    ).one()

    on_the_way = session.exec(
        select(func.count(OrderTable.order_id))
        .where(OrderTable.status == OrderStatus.ON_THE_WAY)
    ).one()

    delivered = session.exec(
        select(func.count(OrderTable.order_id))
        .where(OrderTable.status == OrderStatus.DELIVERED)
    ).one()

    canceled = session.exec(
        select(func.count(OrderTable.order_id))
        .where(OrderTable.status == OrderStatus.CANCELED)
    ).one()

    return {
        "pending": pending,
        "confirmed": confirmed,
        "preparing": preparing,
        "on_the_way": on_the_way,
        "delivered": delivered,
        "canceled": canceled
    }





# top 3 customers based on total spending with customer name and total orders.
@router.get(
    "/analytics/top-customers",
    description="Get top 3 customers based on total spending. Admin access only.",
    response_description="Returns a list of top 3 customers with their total spending."
)
def top_customers(
    api_key: str = Depends(verify_api_key),
    session: Session = Depends(get_session)
):
    results = session.exec(
        select(
            OrderTable.user_id,
            UserTable.username,
            func.sum(OrderTable.total_amount).label("total_spent"),
            func.count(OrderTable.order_id).label("total_orders")
        )
        .join(UserTable, UserTable.user_id == OrderTable.user_id)
        .group_by(UserTable.user_id)
        .order_by(desc("total_spent"))
        .limit(3)
    ).all()

    return [
        {
            "customer_id": user_id, 
            "customer_name": name,
            "total_spent": float(total_spent),
            "total_orders": total_orders
        }
        for user_id, name, total_spent, total_orders in results
    ]



# Top Selling Items
@router.get(
    "/analytics/top-items",
    description="Get top 5 selling menu items. Admin access only.",
    response_description="Returns the top 5 selling menu items."
)
def top_selling_items(
    api_key: str = Depends(verify_api_key),
    session: Session = Depends(get_session)
):

    results = session.exec(
        select(
            OrderMenuTable.menu_name,
            func.sum(OrderMenuTable.quantity).label("quantity_sold"),
            func.sum(
                OrderMenuTable.price * OrderMenuTable.quantity
            ).label("revenue")
        )
        .join(
            OrderTable,
            OrderTable.order_id == OrderMenuTable.order_id
        )
        .where(
            OrderTable.status == OrderStatus.DELIVERED
        )
        .group_by(
            OrderMenuTable.menu_id,
            OrderMenuTable.menu_name
        )
        .order_by(
            func.sum(OrderMenuTable.quantity).desc()
        )
        .limit(5)
    ).all()

    return [
        {
            "menu_name": menu_name,
            "quantity_sold": int(quantity_sold),
            "revenue": float(revenue or 0)
        }
        for menu_name, quantity_sold, revenue in results
    ]