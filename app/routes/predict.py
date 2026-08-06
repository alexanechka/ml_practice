from fastapi import APIRouter, Body, HTTPException, status, Depends
from database.database import get_session
from models.ml_task import MLTask, MLResponce
from typing import List, Dict
from services.crud import ml_task as PredictService
from pydantic import BaseModel, Field

predict_route = APIRouter()

class PredictRequest(BaseModel):
    user_id: int
    input_data: str = Field(..., min_length=1)


class PredictResponse(BaseModel):
    result: str



@predict_route.post("/predict")
async def predict(data: PredictRequest, session=Depends(get_session)) -> PredictResponse:

    responce = PredictService.predict(
        user_id=data.user_id, input_data=data.input_data, session=session
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
    else:
        return PredictResponse(result=responce["Details"])
