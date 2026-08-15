from models.ml_task import MLTask, MLResponce, MLTaskHistory, TaskStatus
from models.ml_model import MLModel
from models.user import User
from sqlmodel import Session, select
from typing import List, Optional, Dict
from datetime import datetime
from services.crud import user as UserService
from services.crud import ml_model as MLModelService
from services.crud import balance as BalanceService
from services.crud import history as HistoryService
import uuid


# postgres
# ml_tasks
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


def get_ml_task_by_task_id(task_id: str, session: Session) -> Optional[MLTask]:
    """
    Get ml_task by ID.

    Args:
        ml_task_id: ml_task ID to find
        session: Database session

    Returns:
        Optional[ml_task]: Found ml_task or None
    """
    try:
        statement = select(MLTask).where(MLTask.task_id == task_id)
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


def create_update_ml_task(ml_task: MLTask, session: Session) -> bool:
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
        return True
    except Exception as e:
        session.rollback()
        raise


def delete_ml_task(ml_task_id: str, session: Session) -> bool:
    """
    Delete ml_task by ID.

    Args:
        ml_task_id: ml_task ID to delete
        session: Database session

    Returns:
        bool: True if deleted, False if not found
    """
    try:
        ml_task = get_ml_task_by_task_id(ml_task_id, session)
        if not ml_task:
            return False

        session.delete(ml_task)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        return False


# ml_responce
def get_ml_responce_by_task_id(task_id: str, session: Session) -> Optional[MLResponce]:
    try:
        statement = select(MLResponce).where(MLResponce.task_id == task_id)
        ml_responce = session.exec(statement).first()
        return ml_responce
    except Exception as e:
        raise


def create_update_ml_responce(ml_responce: MLResponce, session: Session) -> bool:
    """
    Create new ml_responce.

    Args:
        ml_responce: ml_responce to create
        session: Database session

    Returns:
        bool: True if created, False if error
    """
    try:
        session.add(ml_responce)
        session.commit()
        session.refresh(ml_responce)
        return True
    except Exception as e:
        session.rollback()
        raise


def delete_ml_responce(task_id: str, session: Session) -> bool:
    """
    Delete ml_responce by task_id.

    Args:
        task_id: responce of task_id to delete
        session: Database session

    Returns:
        bool: True if deleted, False if not found
    """
    try:
        ml_responce = get_ml_responce_by_task_id(task_id=task_id, session=session)
        if not ml_responce:
            return False

        session.delete(ml_responce)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        return False


# services
# predict
def predict(task_id: str, session: Session) -> MLResponce:

    ml_task = get_ml_task_by_task_id(task_id=task_id, session=session)

    if ml_task == None:
        return {
            "Status": 404,
            "Details": f"No task with id: {task_id}",
        }

    if ml_task.status != TaskStatus.PENDING:
        return {
            "Status": 404,
            "Details": f"Task is already processed id: {task_id}",
        }

    input_data = ml_task.input_data
    user = ml_task.user

    request_language = MLModelService.get_request_language(input_data)
    if type(request_language) == str:
        mark_task_failed(
            task_id=task_id,
            session=session,
            error_message=f"Язык текста не поддерживается (определён как: {request_language})",
        )
        return {
            "Status": 404,
            "Details": f"No model to language: {request_language}",
        }

    ml_model = MLModelService.get_ml_model_by_language(
        language=request_language, session=session
    )
    if ml_model == None:
        mark_task_failed(
            task_id=task_id,
            session=session,
            error_message="Для языка текста нет доступной модели",
        )
        return {
            "Status": 404,
            "Details": f"No model to get summary of text on language",
        }

    request_cost = ml_model.request_cost
    balance = user.balance
    if request_cost > user.balance:
        mark_task_failed(
            task_id=task_id,
            session=session,
            error_message=f"Недостаточно средств: баланс {balance}, стоимость запроса {request_cost}",
        )
        return {
            "Status": 400,
            "Details": f"Not enough money to predict: balance={balance}, request cost={request_cost}",
        }

    ml_task.model = ml_model
    ml_task.status = TaskStatus.PROCESSING

    create_update_ml_task(ml_task=ml_task, session=session)
    balance_after = None

    try:

        balance_after = BalanceService.write_off_balance(
            user=user, amount=request_cost, session=session, ml_task=ml_task
        )

        responce = ml_model.predict(prompt=input_data)

        ml_responce = MLResponce(ml_task=ml_task, task_id=task_id, responce=responce)
        create_update_ml_responce(ml_responce=ml_responce, session=session)

        ml_task.status = TaskStatus.DONE
        create_update_ml_task(ml_task=ml_task, session=session)

        code = 200

    except Exception as e:
        session.rollback()

        mark_task_failed(
            task_id=task_id,
            session=session,
            error_message="Внутренняя ошибка при обработке запроса",
        )

        code = 500
        responce = str(e)

        delete_ml_responce(task_id=task_id, session=session)

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


# ml_task
def create_pending_task(
    task_id: str, user: User, input_data: str, session: Session
) -> bool:
    ml_task = MLTask(
        input_data=input_data,
        status=TaskStatus.PENDING,
        user=user,
        task_id=task_id,
    )
    return create_update_ml_task(ml_task=ml_task, session=session)


def mark_task_failed(task_id: str, session: Session, error_message: str = None) -> bool:
    ml_task = get_ml_task_by_task_id(task_id=task_id, session=session)

    ml_task.status = TaskStatus.FAILED
    ml_task.error_message = error_message
    return create_update_ml_task(ml_task=ml_task, session=session)


def get_task_status(user: User, task_id: str, session: Session):
    ml_task = get_ml_task_by_task_id(task_id=task_id, session=session)
    if ml_task == None:
        raise LookupError(f"No task with task_id {task_id}")
    if ml_task.user != user:
        raise PermissionError("Task belongs to another user")

    return {"status": ml_task.status, "error_message": ml_task.error_message}


# ml_responce
def get_task_result(user: User, task_id: str, session: Session) -> Optional[MLResponce]:
    ml_responce = get_ml_responce_by_task_id(task_id=task_id, session=session)
    if ml_responce == None:
        raise LookupError(f"No result with task_id {task_id}")
    if ml_responce.ml_task.user != user:
        raise PermissionError("Task belongs to another user")

    return ml_responce




