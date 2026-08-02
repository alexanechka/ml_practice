from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import langid
from models.user import User
from models.ml_task import MLTask


class TransactionType(Enum):
    IN = "in"
    OUT = "out"


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
    t_type: TransactionType = TransactionType.OUT
    t_date: datetime = field(default_factory=datetime.now)
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
