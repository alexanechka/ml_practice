from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Dict
import logging
from database.database import get_session
from models.user import User
from models.transaction import Transaction
from services.crud import user as UserService
from services.crud import balance as BalanceService
from services.crud import transaction as TransactionService
from services.auth.security import require_admin

logger = logging.getLogger(__name__)

admin_route = APIRouter()


@admin_route.post(
    "/balance/topup",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Top up balance for any user (admin only)",
)
async def admin_topup_balance(
    email: str,
    amount: float,
    admin: User = Depends(require_admin),
    session=Depends(get_session),
) -> Dict[str, str]:
    target_user = UserService.get_user_by_email(email, session)
    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {email} not found",
        )

    try:
        balance = BalanceService.topup_balance(
            user=target_user, amount=amount, session=session
        )
        logger.info(f"Admin {admin.email} topped up balance for {email}")
        return {"message": f"Balance for {email} updated, balance = {balance}"}
    except Exception as e:
        logger.error(f"Error during admin topup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating balance",
        )


@admin_route.get(
    "/transactions",
    response_model=List[Transaction],
    summary="Get all transactions across all users (admin only)",
)
async def get_all_transactions(
    admin: User = Depends(require_admin), session=Depends(get_session)
) -> List[Transaction]:
    try:
        transactions = TransactionService.get_all_transactions(session)
        logger.info(f"Admin {admin.email} retrieved {len(transactions)} transactions")
        return transactions
    except Exception as e:
        logger.error(f"Error retrieving all transactions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving transactions",
        )
