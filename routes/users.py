from fastapi import APIRouter, Depends, HTTPException, Query
from models.user import UserTable, UserResponseModel, RegisterResponseModel, LoginResponseModel, RegisterUser, LoginUser, ListUsers, UpdateUser
from sqlmodel import Session, select
from src.database import get_session
from src.auth import verify_api_key, get_current_user
import secrets
import string

# utily function to generate a 12 character random password
def generate_secret_key(length: int = 12):
    characters = string.ascii_letters + string.digits
    return ''.join(
        secrets.choice(characters)
        for _ in range(length)
    )


router = APIRouter(prefix="/users", tags=["User Management"])



@router.post(
    "/register",
    response_model=RegisterResponseModel,
    description="Register a new user.",
    response_description="Returns the registered user details.",
)
def register_user(
    user_data: RegisterUser,
    session: Session = Depends(get_session)
):

    # Check if username already exists
    existing_username = session.exec(
        select(UserTable).where(
            UserTable.username == user_data.username
        )
    ).first()

    if existing_username:
        raise HTTPException(
            status_code=409,
            detail="Username already exists"
        )

    # Check if email already exists
    existing_email = session.exec(
        select(UserTable).where(
            UserTable.email == user_data.email
        )
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    # Generate unique secret key
    secret_key = generate_secret_key()

    # Create user
    new_user = UserTable.model_validate(
        user_data,
        update={
            "secret_key": secret_key
        }
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return {
        "status": "success",
        "message": f"User {new_user.username} registered successfully.",
        "user": new_user,
        "secret_key": secret_key
    }


@router.post(
    "/login", 
    response_model=LoginResponseModel,
    description="Login a user.",
    response_description="Returns the logged-in user details.",
)
def login_user(
    user_data: LoginUser,
    session: Session = Depends(get_session)
):  
    # check if the username is correct or not
    existing_user = session.exec(
        select(UserTable).where(
            UserTable.username == user_data.username
        )
    ).first()

    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    # check if the password is correct or not
    # Replace this with password hash verification.
    if existing_user.password != user_data.password:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    return {
        "status": "success",
        "message": f"Welcome Back, {existing_user.username}",
        "user": existing_user
    }


# list all users
@router.get(
    "/list",
    response_model=ListUsers,
    description="List all registered users.",
    response_description="Returns a list of all registered users.",
)
def list_users(session: Session = Depends(get_session), api_key: str = Depends(verify_api_key)):
    users = session.exec(select(UserTable)).all()
    return {
        "status": "success",
        "count": len(users),
        "users": users
    }


# list usernames only
@router.get(
    "/list/usernames",
    description="List all registered usernames.",
    response_description="Returns a list of all registered usernames.",
)
def list_usernames(session: Session = Depends(get_session), api_key: str = Depends(verify_api_key)):
    usernames = session.exec(select(UserTable.username)).all()
    return usernames


# get user by id
@router.get(
    "/{user_id}",
    response_model=UserResponseModel,
    description="Get user details by user ID.",
    response_description="Returns the user details for the specified user ID.",
)
def get_user_by_id(user_id: int, session: Session = Depends(get_session), api_key: str = Depends(verify_api_key)):
    user = session.exec(
        select(UserTable).where(UserTable.user_id == user_id)
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


@router.patch(
    "/update",
    response_model=UserResponseModel,
    description="Update the currently authenticated user's details.",
    response_description="Returns the updated user details."
)
def update_user(
    update_data: UpdateUser,
    current_user: UserTable = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Get only the fields provided by the user
    update_fields = update_data.model_dump(
        exclude_unset=True
    )

    # Check if at least one field was provided
    if not update_fields:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update"
        )

    # Check username uniqueness
    if "username" in update_fields:
        existing_username = session.exec(
            select(UserTable).where(
                UserTable.username == update_fields["username"]
            )
        ).first()

        if (
            existing_username
            and existing_username.user_id != current_user.user_id
        ):
            raise HTTPException(
                status_code=409,
                detail="Username already exists"
            )

    # Check email uniqueness
    if "email" in update_fields:
        existing_email = session.exec(
            select(UserTable).where(
                UserTable.email == update_fields["email"]
            )
        ).first()

        if (
            existing_email
            and existing_email.user_id != current_user.user_id
        ):
            raise HTTPException(
                status_code=409,
                detail="Email already registered"
            )

    # Update user details
    for key, value in update_fields.items():
        setattr(current_user, key, value)

    # Save changes
    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return current_user


# delete user by id
@router.delete(
    "/{user_id}",
    description="Delete a user by user ID. Admin access required.",
    response_description="Returns a success message upon successful deletion.",
)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    api_key: str = Depends(verify_api_key)
):
    user = session.exec(
        select(UserTable).where(
            UserTable.user_id == user_id
        )
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    username = user.username

    session.delete(user)
    session.commit()

    return {
        "status": "success",
        "message": "User deleted successfully.",
        "id": user_id,
        "username": username
    }