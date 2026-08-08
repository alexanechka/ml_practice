from models.ml_task import MLTask, MLResponce, MLTaskHistory, TaskStatus
from models.ml_model import MLModel
from models.user import User
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from services.crud import user as UserService
from services.crud import ml_model as MLModelService
from services.crud import balance as BalanceService
from services.crud import history as HistoryService


def get_all_ml_tasks(session: Session) -> List[MLTask]:
    """
    Retrieve all ml_tasks.

    Args:
        session: Database session

    Returns:
        List[ml_task]: List of all ml_tasks
    """
    try:
        statement = select(MLTask).limit(5000)
        ml_tasks = session.exec(statement).all()
        return ml_tasks
    except Exception as e:
        raise


def get_ml_task_by_id(ml_task_id: int, session: Session) -> Optional[MLTask]:
    """
    Get ml_task by ID.

    Args:
        ml_task_id: ml_task ID to find
        session: Database session

    Returns:
        Optional[ml_task]: Found ml_task or None
    """
    try:
        statement = select(MLTask).where(MLTask.id == ml_task_id)
        ml_task = session.exec(statement).first()
        return ml_task
    except Exception as e:
        raise


def get_user_ml_task(user_id: int, session: Session) -> Optional[MLTask]:
    """
    Get ml_task by ID.

    Args:
        ml_task_id: ml_task ID to find
        session: Database session

    Returns:
        Optional[ml_task]: Found ml_task or None
    """
    try:
        statement = (
            select(MLTask)
            .where(MLTask.user_id == user_id)
            .limit(100)
            .order_by(MLTask.id.desc())
        )
        ml_task = session.exec(statement).all()
        return ml_task
    except Exception as e:
        raise


def create_update_ml_task(ml_task: MLTask, session: Session) -> MLTask:
    """
    Create new ml_task.

    Args:
        ml_task: ml_task to create
        session: Database session

    Returns:
        ml_task: Created ml_task with ID
    """
    try:
        session.add(ml_task)
        session.commit()
        session.refresh(ml_task)
        return ml_task
    except Exception as e:
        session.rollback()
        raise


def delete_ml_task(ml_task_id: int, session: Session) -> bool:
    """
    Delete ml_task by ID.

    Args:
        ml_task_id: ml_task ID to delete
        session: Database session

    Returns:
        bool: True if deleted, False if not found
    """
    try:
        ml_task = get_ml_task_by_id(ml_task_id, session)
        if not ml_task:
            return False

        session.delete(ml_task)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise


def predict(user: User, input_data: str, session: Session) -> MLResponce:

    request_language = MLModelService.get_request_language(input_data)
    if type(request_language) == str:
        return {
            "Status": 404,
            "Details": f"No model to language: {request_language}",
        }

    ml_model = MLModelService.get_ml_model_by_language(
        language=request_language, session=session
    )
    if ml_model == None:
        return {
            "Status": 404,
            "Details": f"No model to get summary of text on language",
        }

    request_cost = ml_model.request_cost
    balance = user.balance
    if request_cost > user.balance:

        return {
            "Status": 400,
            "Details": f"Not enough money to predict: balance={balance}, request cost={request_cost}",
        }

    ml_task = MLTask(
        input_data=input_data,
        status=TaskStatus.PROCESSING,
        user=user,
        model=ml_model,
    )

    create_update_ml_task(ml_task=ml_task, session=session)
    balance_after = None

    try:

        balance_after = BalanceService.write_off_balance(
            user=user, amount=request_cost, session=session, ml_task=ml_task
        )

        responce = ml_model.predict(prompt=input_data)
        ml_responce = MLResponce(ml_task=ml_task, responce=responce)

        ml_task.status = TaskStatus.DONE
        create_update_ml_task(ml_task=ml_task, session=session)

        code = 200

    except Exception as e:
        session.rollback()

        ml_task.status = TaskStatus.FAILED
        create_update_ml_task(ml_task=ml_task, session=session)
        code = 500
        responce = str(e)

        if balance_after != None:
            BalanceService.write_off_balance(
                user=user, amount=-request_cost, session=session, ml_task=ml_task
            )

    ml_task_history = MLTaskHistory(
        ml_task=ml_task,
        cost=request_cost,
        user=user,
        model=ml_model,
        status=ml_task.status,
    )
    HistoryService.create_history_record(
        ml_task_history_record=ml_task_history, session=session
    )

    return {
        "Status": code,
        "Details": responce,
    }
