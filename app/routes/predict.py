from fastapi import APIRouter, Body, HTTPException, status, Depends
from database.database import get_session
from models.ml_task import MLTask, MLResponce, TaskStatus
from typing import List, Dict
from pydantic import BaseModel, Field
from models.user import User
from services.auth.security import get_current_user
from services.crud import ml_task as PredictService
from services.queue.publisher import publish_task
import uuid
import logging

# Configure logging
logger = logging.getLogger(__name__)

predict_route = APIRouter()


class PredictRequest(BaseModel):
    input_data: str = Field(..., min_length=1)


class PredictAcceptedResponse(BaseModel):
    task_id: str


@predict_route.post("", status_code=202)
async def predict(
    data: PredictRequest,
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
) -> PredictAcceptedResponse:

    task_id = str(uuid.uuid4())
    result = PredictService.create_pending_task(
        task_id=task_id, user=current_user, input_data=data.input_data, session=session
    )

    if result != True:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request error. Failed to register the request.",
        )

    try:
        publish_task(
            task_id=task_id, user_id=current_user.id, input_data=data.input_data
        )
    except Exception as e:
        PredictService.mark_task_failed(task_id=task_id, session=session)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to queue prediction task",
        )

    return {"task_id": task_id}


@predict_route.get("/result/{task_id}")
async def get_task_result(
    task_id: str,
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
) -> MLResponce:

    try:
        task_result = PredictService.get_task_result(
            user=current_user, task_id=task_id, session=session
        )
        logger.info(f"Get task result")
        return task_result
    except Exception as e:
        logger.error(f"Error getting task result: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting task result",
        )

@predict_route.get("/{task_id}")
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
) -> TaskStatus:

    try:
        task_status = PredictService.get_task_status(
            user=current_user, task_id=task_id, session=session
        )
        logger.info(f"Get task status")
        return task_status
    except Exception as e:
        logger.error(f"Error getting task status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting task status",
        )
