from fastapi import APIRouter, Body, HTTPException, status, Depends
from database.database import get_session
from models.ml_task import MLTask, MLResponce
from typing import List, Dict
from pydantic import BaseModel, Field
from models.user import User
from services.auth.security import get_current_user
from services.crud import ml_task as PredictService

predict_route = APIRouter()


class PredictRequest(BaseModel):
    input_data: str = Field(..., min_length=1)


class PredictResponse(BaseModel):
    result: str


@predict_route.post("/predict")
async def predict(
    data: PredictRequest,
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
) -> PredictResponse:

    responce = PredictService.predict(
        user=current_user, input_data=data.input_data, session=session
    )

    if responce["Status"] == 400:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=responce["Details"],
        )

    elif responce["Status"] == 404:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=responce["Details"],
        )

    elif responce["Status"] == 500:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=responce["Details"],
        )
    else:
        return PredictResponse(result=responce["Details"])
