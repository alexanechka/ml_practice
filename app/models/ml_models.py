from sqlmodel import SQLModel, Field, Relationship
from dataclasses import dataclass, field
import re
from enum import Enum
from datetime import datetime
import langid
from typing import Optional


class InputLanguages(Enum):
    EN = "en"
    RU = "ru"


class MLModel(SQLModel, table = True):
    """
    Класс для описания модели.

    Attributes:
        id (int): Уникальный идентификатор модели
        model_description: Описание модели
        request_cost (float): Cтоимость одного предсказания 7 - ru, 2 - en
        request_metod (str): Метод выполнения предсказания
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    model_description: str
    request_cost: float
    language: InputLanguages

    def validate_task_language(self, input_data: str):
        answer = langid.classify(input_data)[0]
        return answer == self.language.value

    def predict(self, prompt: str) -> str:
        if self.validate_task_language(prompt):
            # ok
            return "something predicted"
        else:
            return "language is wrong"

