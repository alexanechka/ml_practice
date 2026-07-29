from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from models.user import User
from models.ml_models import SummarizationModelEn, SummarizationModelRu


class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


@dataclass
class MLTask:
    """Класс для описания ML-задачи

    Attributes:
        input_data (str): входные данные;
        status (Status): статус выполнения;
        user (User): ссылка на пользователя;
        model (SummarizationModelEn | SummarizationModelRu): ссылка на ML-модель;
    """

    input_data: str
    status: TaskStatus
    user: User
    model: SummarizationModelEn | SummarizationModelRu


@dataclass
class MLTaskHistory:
    """Класс для описания Истории запросов

    Attributes:
        task (MLTask): связанная ML-задача;
        cost (float): стоимость запроса;
        user (User): ссылка на пользователя;
        model (SummarizationModelEn | SummarizationModelRu): ссылка на ML-модель;
        status (Status): статус выполнения;
        h_date (datetime): Дата и время;
    """

    ml_task: MLTask
    cost: float
    user: User
    model: SummarizationModelEn | SummarizationModelRu
    status: TaskStatus
    h_date: datetime = field(default_factory=datetime.now)


@dataclass
class MLResponce:
    pass
