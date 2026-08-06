from models.user import User, Wallet
from models.transaction import Transaction, TransactionType
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from services.crud import user as UserService
from services.crud import transaction as TransactionService


def user_balance(user_id: int, session: Session) -> bool:
    """
    Get user balance by id.

    Args:
        user_id: User ID to delete
        session: Database session

    Returns:
        bool: True if deleted, False if not found
    """
    try:
        user = UserService.get_user_by_id(user_id, session)
        if user:
            statement = (
                select(User.id, Wallet.balance).where(User.id == user_id).join(Wallet)
            )
            wallet = session.exec(statement).first()
            return wallet.balance
        return 0
    except Exception as e:
        session.rollback()
        raise


def topup_balance(user: User, amount: float, session: Session):
    try:
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной")
        transaction = Transaction(t_type=TransactionType.IN, amount=amount, user=user)
        TransactionService.create_transaction(transaction, session)
        return user_balance(user.id, session)
    except Exception as e:
        session.rollback()
        raise


def write_off_balance(user: User, amount: float, session: Session):
    try:
        if amount > 0 and user.balance < amount:
            raise ValueError("Недостаточно средств")
        transaction = Transaction(t_type=TransactionType.OUT, amount=amount, user=user)
        TransactionService.create_transaction(transaction, session)
        return user_balance(user.id, session)
    except Exception as e:
        session.rollback()
        raise
