from models.transaction import Transaction, TransactionType
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from .user import get_user_by_id

def get_all_transactions(session: Session) -> List[Transaction]:
    """
    Retrieve all transactions.
    
    Args:
        session: Database session
    
    Returns:
        List[transaction]: List of all transactions
    """
    try:
        statement = select(Transaction).limit(5000)
        transactions = session.exec(statement).all()
        return transactions
    except Exception as e:
        raise

def get_transaction_by_id(transaction_id: int, session: Session) -> Optional[Transaction]:
    """
    Get transaction by ID.
    
    Args:
        transaction_id: transaction ID to find
        session: Database session
    
    Returns:
        Optional[transaction]: Found transaction or None
    """
    try:
        statement = select(Transaction).where(Transaction.id == transaction_id)
        transaction = session.exec(statement).first()
        return transaction
    except Exception as e:
        raise

def get_user_transaction(user_id: int, session: Session) -> Optional[Transaction]:
    """
    Get transaction by ID.
    
    Args:
        transaction_id: transaction ID to find
        session: Database session
    
    Returns:
        Optional[transaction]: Found transaction or None
    """
    try:
        statement = select(Transaction).where(Transaction.user_id == user_id).limit(100).order_by(Transaction.t_date.desc())
        transaction = session.exec(statement).all()
        return transaction
    except Exception as e:
        raise

def create_transaction(transaction: Transaction, session: Session) -> Transaction:
    """
    Create new transaction.
    
    Args:
        transaction: transaction to create
        session: Database session
    
    Returns:
        transaction: Created transaction with ID
    """
    try:
        session.add(transaction)
        session.commit()
        session.refresh(transaction)
        return transaction
    except Exception as e:
        session.rollback()
        raise
    
    
def delete_transaction(transaction_id: int, session: Session) -> bool:
    """
    Delete transaction by ID.
    
    Args:
        transaction_id: transaction ID to delete
        session: Database session
    
    Returns:
        bool: True if deleted, False if not found
    """
    try:
        transaction = get_transaction_by_id(transaction_id, session)
        if not transaction:
            return False
            
        session.delete(transaction)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise


def top_up(user_id: int, amount: float, session: Session) -> Transaction:
    user = get_user_by_id(user_id, session)
    transaction = Transaction(user=user, amount=amount, t_type=TransactionType.IN)
    transaction.apply()          # реально меняет user.wallet.balance
    session.add(user)
    session.add(transaction)
    session.commit()             # оба изменения — одним коммитом, атомарно
    session.refresh(transaction)
    return transaction

def write_off(user_id: int, amount: float, session: Session) -> Transaction:
    user = get_user_by_id(user_id, session)
    if user.balance < amount:
        raise ValueError("Недостаточно средств")
    transaction = Transaction(user=user, amount=amount, t_type=TransactionType.OUT)
    transaction.apply()
    session.add(user)
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction