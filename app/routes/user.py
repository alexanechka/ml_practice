from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Dict
import logging
from pydantic import BaseModel
from database.database import get_session
from models.user import User
from services.crud import user as UserService
from services.auth.security import get_current_user, require_admin

# Configure logging
logger = logging.getLogger(__name__)

user_route = APIRouter()


class UserPublic(BaseModel):
    id: int
    email: str
    role: str
    balance: float


def _to_public(user: User) -> UserPublic:
    return UserPublic(
        id=user.id,
        email=user.email,
        role=user.role.value,
        balance=user.balance,
    )


@user_route.get(
    "/get_all_users",
    response_model=List[UserPublic],
    summary="Get all users (admin only)",
    response_description="List of all users",
)
async def get_all_users(
    admin: User = Depends(require_admin), session=Depends(get_session)
) -> List[UserPublic]:
    """
    Get list of all users. Admin only.

    Args:
        session: Database session

    Returns:
        List[UserPublic]: List of users without sensitive fields
    """
    try:
        users = UserService.get_all_users(session)
        logger.info(f"Retrieved {len(users)} users")
        return [_to_public(user) for user in users]
    except Exception as e:
        logger.error(f"Error retrieving users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving users",
        )


@user_route.get(
    "/me",
    response_model=UserPublic,
    summary="Get current user profile",
)
async def get_me(current_user: User = Depends(get_current_user)) -> UserPublic:
    return _to_public(current_user)
