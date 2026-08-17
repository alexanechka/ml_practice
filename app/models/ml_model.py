from sqlmodel import SQLModel, Field, Relationship
from dataclasses import dataclass, field
import re
import os
import json
import logging
import requests
from enum import Enum
from datetime import datetime
import langid
from typing import Optional

logger = logging.getLogger(__name__)

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://ollama:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma3:1b")
OLLAMA_TIMEOUT = 60  # seconds


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

    def _build_prompt(self, text: str) -> str:
        if self.language == InputLanguages.RU:
            return (
                "Кратко перескажи следующий текст на русском языке "
                "в 2-3 предложениях, без вступлений и пояснений:\n\n" + text
            )
        return (
            "Summarize the following text in English in 2-3 sentences, "
            "with no introduction or explanation:\n\n" + text
        )

    def predict(self, prompt: str) -> str:
        if not self.validate_task_language(prompt):
            raise ValueError("language is wrong")

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": self._build_prompt(prompt),
                "stream": False,
            },
            timeout=OLLAMA_TIMEOUT,
        )
        response.raise_for_status()
        result = response.json()["response"].strip()

        if not result:
            raise ValueError("Empty response from model")

        return result

