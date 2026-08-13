from fastapi import APIRouter, HTTPException, status, Depends
from database.database import get_session
from models.user import User
from services.crud import user as UserService
from services.auth.security import create_access_token
from typing import List, Dict
import logging
from services.auth.hash_password import HashPassword


# Configure logging
logger = logging.getLogger(__name__)

auth_route = APIRouter()
hash_password = HashPassword()

@auth_route.post(
    "/signup",
    response_model=Dict[str, str],
    status_code=status.HTTP_201_CREATED,
    summary="User Registration",
    description="Register a new user with email and password",
)
async def signup(data: User, session=Depends(get_session)) -> Dict[str, str]:
    """
    Create new user account.

    Args:
        data: User registration data
        session: Database session

    Returns:
        dict: Success message

    Raises:
        HTTPException: If user already exists
    """
    try:
        if UserService.get_user_by_email(data.email, session):
            logger.warning(f"Signup attempt with existing email: {data.email}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )

        UserService.create_user(
            email=data.email, password=data.password, session=session
        )
        logger.info(f"New user registered: {data.email}")
        return {"message": "User successfully registered"}

    except Exception as e:
        logger.error(f"Error during signup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user",
        )


@auth_route.post("/signin")
async def signin(data: User, session=Depends(get_session)) -> Dict[str, str]:
    """
    Authenticate existing user.

    Args:
        form_data: User credentials
        session: Database session

    Returns:
        dict: Success message

    Raises:
        HTTPException: If authentication fails
    """
    user = UserService.get_user_by_email(data.email, session)
    if user is None:
        logger.warning(f"Login attempt with non-existent email: {data.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist"
        )

    if not hash_password.verify_hash(data.password, user.password):
        logger.warning(f"Failed login attempt for user: {data.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Wrong credentials passed"
        )

    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer"}


