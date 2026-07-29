from dataclasses import dataclass, field
import re
from enum import Enum
from datetime import datetime
import langid


class InputLanguages(Enum):
    EN = "en"
    RU = "ru"


@dataclass
class MLModel:
    """
    Класс для описания модели.

    Attributes:
        id (int): Уникальный идентификатор модели
        model_description: Описание модели
        request_cost (float): Cтоимость одного предсказания
        request_metod (str): Метод выполнения предсказания
    """

    id: int
    model_description: str
    request_cost: float
    language: InputLanguages

    def validate_task_language(self, input_data: str):
        answer = langid.classify(input_data)[0]
        return answer == self.language.value


@dataclass
class SummarizationModelEn(MLModel):
    """
    Класс для описания модели, разбирающей тексты на английском языке
    """

    request_cost: float = 2.0
    language: InputLanguages = InputLanguages.EN

    def predict(self, prompt: str) -> str:
        if super().validate_task_language(prompt):
            # ok
            return "something predicted"
        else:
            return "language is wrong"


@dataclass
class SummarizationModelRu(MLModel):
    """
    Класс для описания модели, разбирающей тексты на русском языке
    """

    request_cost: float = 7.0
    language: InputLanguages = InputLanguages.RU

    def predict(self, prompt: str) -> str:
        if super().validate_task_language(prompt):
            # ok
            return "something predicted"
        else:
            return "language is wrong"
