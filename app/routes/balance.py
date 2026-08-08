from fastapi import APIRouter, HTTPException, status, Depends
from database.database import get_session
from models.user import User
from services.auth.security import get_current_user
from services.crud import user as UserService
from services.crud import balance as BalanceService
from typing import List, Dict
import logging

# Configure logging
logger = logging.getLogger(__name__)

balance_route = APIRouter()


@balance_route.get("/get")
async def get_user_balance(
    current_user: User = Depends(get_current_user), session=Depends(get_session)
) -> float:
    """
    Balance information

    Args:
        session: Database session

    Returns:
        wallet balance of user
    """

    try:
        balance = BalanceService.user_balance(current_user.id, session)
        logger.info(f"Get user balance")
        return balance
    except Exception as e:
        logger.error(f"Error getting balance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving users",
        )


@balance_route.post(
    "/topup",
    status_code=status.HTTP_202_ACCEPTED,
    summary="User balance top up",
)
async def topup_balance(
    amount: float, current_user: User = Depends(get_current_user), session=Depends(get_session), 
) -> Dict[str, str]:
    """
    Top up user wallet balance.

    Args:
        user_id: int
        amount: topup sum
        session: Database session

    Returns:
        dict: Success message

    Raises:
        HTTPException: If something goes wrong
    """
    try:

        balance = BalanceService.topup_balance(
            user=current_user, amount=amount, session=session
        )
        logger.info(f"Balance is updated.")
        return {"message": f"Balance is updated, balance = {balance}"}

    except Exception as e:
        logger.error(f"Error during signup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating balance",
        )
