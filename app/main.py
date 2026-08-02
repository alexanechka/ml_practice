from dataclasses import dataclass, field
import re
from enum import Enum
from datetime import datetime
import langid
from models.user import User, Wallet
from models.ml_models import SummarizationModelEn, SummarizationModelRu
from models.ml_task import MLTask, TaskStatus


def main() -> None:
    try:

        user_wallet = Wallet()
        user = User(
            id=1,
            email="test@mail.ru",
            password="secure_password123",
            wallet=user_wallet,
        )

        user.topup_balance(10.0)
        print(f"Created user: {user}, balance: {user.balance}")

        sum_model_ru = SummarizationModelRu(
            id=1,
            model_description="Модель для подготовки краткого описания по тексту на русском языке",
        )

        sum_model_en = SummarizationModelEn(
            id=1,
            model_description="Модель для подготовки краткого описания по тексту на английском языке",
        )

        input_data = (
            "Практическое задание №1: Проектирование объектной модели ML-сервиса. "
        )
        # answer_ru = langid.classify(input_data)
        # print(answer_ru[0] == InputLanguages.RU.value)

        input_data_en = (
            "Practical Assignment No. 1: Designing the Object Model of an ML Service"
        )

        task_ru = MLTask(
            input_data=input_data,
            status=TaskStatus.PENDING,
            user=user,
            model=sum_model_en,
        )

        result_1 = sum_model_ru.predict(prompt=task_ru.input_data)
        print(result_1)

        result_2 = sum_model_en.predict(prompt=task_ru.input_data)
        print(result_2)

        result_3 = sum_model_en.predict(prompt=input_data_en)
        print(result_3)

    except ValueError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
