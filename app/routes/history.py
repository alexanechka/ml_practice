from fastapi import APIRouter, HTTPException, status, Depends
from database.database import get_session
from models.ml_task import MLTaskHistory
from models.transaction import Transaction
from services.crud import history as HistoryService
from typing import List, Dict
import logging

# Configure logging
logger = logging.getLogger(__name__)

history_route = APIRouter()

@history_route.get("/ml_task/{user_id}/get")
async def get_user_history(user_id: int, session=Depends(get_session)) -> List[MLTaskHistory]:
    
    try:
        history = HistoryService.get_user_ml_task_history(user_id, session)
        logger.info(f"Get user history")
        return history
    except Exception as e:
        logger.error(f"Error getting history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving history",
        )

@history_route.get("/transaction/{user_id}/get")
async def get_transaction_history(user_id: int, session=Depends(get_session)) -> List[Transaction]:
    
    try:
        history = HistoryService.get_user_transaction_history(user_id, session)
        logger.info(f"Get user history")
        return history
    except Exception as e:
        logger.error(f"Error getting history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving history",
        )

