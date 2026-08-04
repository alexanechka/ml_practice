from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Optional
from models.user import User
from models.ml_models import MLModel
from sqlmodel import SQLModel, Field, Relationship


class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class MLTask(SQLModel, table = True):
    """Класс для описания ML-задачи

    Attributes:
        input_data (str): входные данные;
        status (Status): статус выполнения;
        user (User): ссылка на пользователя;
        model (SummarizationModelEn | SummarizationModelRu): ссылка на ML-модель;
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    input_data: str
    status: TaskStatus
    user_id: int = Field(default=None, foreign_key="user.id")
    user: User = Relationship(
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    model_id: Optional[int] = Field(default=None, foreign_key="mlmodel.id")
    model: Optional[MLModel] = Relationship(
        sa_relationship_kwargs={"lazy": "selectin"}
    )


class MLTaskHistory(SQLModel, table = True):
    """Класс для описания Истории запросов

    Attributes:
        task (MLTask): связанная ML-задача;
        cost (float): стоимость запроса;
        user (User): ссылка на пользователя;
        model (SummarizationModelEn | SummarizationModelRu): ссылка на ML-модель;
        status (Status): статус выполнения;
        h_date (datetime): Дата и время;
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    ml_task_id: int = Field(default=None, foreign_key="mltask.id")
    ml_task: MLTask = Relationship(
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    cost: float
    user_id: int = Field(default=None, foreign_key="user.id")
    user: User = Relationship(
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    model_id: Optional[int] = Field(default=None, foreign_key="mlmodel.id")
    model: Optional[MLModel] = Relationship(
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    status: TaskStatus
    h_date: datetime = Field(default_factory=datetime.utcnow)


class MLResponce(SQLModel, table = True):
    """Класс для хранения ответов на запросы запросов

    Attributes:
        task (MLTask): связанная ML-задача;
        responce: ответ
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    ml_task_id: int = Field(default=None, foreign_key="mltask.id")
    ml_task: MLTask = Relationship(
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    responce: str
