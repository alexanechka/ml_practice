from models.ml_task import MLTask, MLResponce, MLTaskHistory
from models.ml_model import MLModel
from models.transaction import Transaction
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from services.crud import transaction


def get_user_ml_task_history(user_id: int, session: Session) -> Optional[List[MLTaskHistory]]:

    try:
        statement = (
            select(MLTaskHistory)
            .where(MLTaskHistory.user_id == user_id)
            .limit(100)
            .order_by(MLTaskHistory.h_date.desc())
        )
        ml_task_history = session.exec(statement).all()
        return ml_task_history
    except Exception as e:
        raise


def create_history_record(
    ml_task_history_record: MLTaskHistory, session: Session
) -> MLTaskHistory:
    """
    Create new record of ml_task history.
    """
    try:
        session.add(ml_task_history_record)
        session.commit()
        session.refresh(ml_task_history_record)
        return ml_task_history_record
    except Exception as e:
        session.rollback()
        raise


def get_user_transaction_history(user_id: int, session: Session) -> Optional[List[Transaction]]:

    return transaction.get_user_transaction(user_id, session)
    
