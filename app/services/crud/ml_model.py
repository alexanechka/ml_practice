from models.ml_model import MLModel, InputLanguages
from sqlmodel import Session, select
from typing import List, Optional
import langid


def get_ml_model_by_language(language: int, session: Session) -> Optional[MLModel]:
    """
    Get ml_task by ID.

    Args:
        ml_task_id: ml_task ID to find
        session: Database session

    Returns:
        Optional[ml_task]: Found ml_task or None
    """

    try:

        statement = select(MLModel).where(MLModel.language == language)
        ml_model = session.exec(statement).first()
        return ml_model
    except Exception as e:
        raise


def get_request_language(input_data: str):
    answer = langid.classify(input_data)[0]
    return InputLanguages[answer.upper()]
