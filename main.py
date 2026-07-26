from dataclasses import dataclass, field
import re
from enum import Enum
from datetime import datetime
import langid


class Role(Enum):
    ADMIN = "admin"
    USER = "user"


class TransactionType(Enum):
    INN = "inn"
    OUT = "out"


class InputLanguages(Enum):
    EN = "en"
    RU = "ru"


class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


@dataclass
class User:
    """
    Класс для представления пользователя в системе.

    Attributes:
        id (int): Уникальный идентификатор пользователя
        email (str): Email пользователя
        password (str): Пароль пользователя
        balance (float): Остаток кредитов
    """

    id: int
    email: str
    password: str
    role: Role = Role.USER
    balance: float = 0

    def __post_init__(self) -> None:
        self._validate_email()
        self._validate_password()

    def _validate_email(self) -> None:
        """Проверяет корректность email."""
        email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        if not email_pattern.match(self.email):
            raise ValueError("Invalid email format")

    def _validate_password(self) -> None:
        """Проверяет минимальную длину пароля."""
        if len(self.password) < 8:
            raise ValueError("Password must be at least 8 characters long")

    def topup_balance(self, amount: float):
        self.balance += amount

    def write_off_balance(self, amount: float):
        self.balance -= amount


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
            return "somethimg predicted"
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
            return "somethimg predicted"
        else:
            return "language is wrong"


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
    h_date: datetime = datetime.now


@dataclass
class MLResponce:
    pass


@dataclass
class Transaction:
    """
    Класс для описания Транзакций.

    Attributes:
        t_type (TransactionType): Тип транзакции;
        amount (float): Сумма;
        t_date (datetime): Дата и время;
        user (User): Связанный пользователь;
        ml_task (MLTask): связанная ML-задача (если применимо)
    """

    user: User
    amount: float
    t_type: TransactionType.OUT
    t_date: datetime = datetime.now
    ml_task: MLTask = None

    def apply(self):
        raise NotImplementedError


@dataclass
class DebitTransaction(Transaction):
    def apply(self):
        # списание средств
        self.user.write_off_balance(self.amount)


@dataclass
class TopUpTransaction(Transaction):
    def apply(self):
        # пополнение баланса
        self.user.topup_balance(self.amount)


def main() -> None:
    try:
        user = User(id=1, email="test@mail.ru", password="secure_password123")

        user.topup_balance(10)
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
            model=SummarizationModelEn,
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
