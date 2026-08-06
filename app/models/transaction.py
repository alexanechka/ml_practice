from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from models.user import User
from models.ml_task import MLTask
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional


class TransactionType(Enum):
    IN = "in"
    OUT = "out"


class Transaction(SQLModel, table=True):
    """
    Класс для описания Транзакций.

    Attributes:
        t_type (TransactionType): Тип транзакции;
        amount (float): Сумма;
        t_date (datetime): Дата и время;
        user (User): Связанный пользователь;
        ml_task (MLTask): связанная ML-задача (если применимо)
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.id")
    user: User = Relationship(sa_relationship_kwargs={"lazy": "selectin"})
    amount: float
    t_type: TransactionType = TransactionType.OUT
    t_date: datetime = Field(default_factory=datetime.utcnow)
    ml_task_id: Optional[int] = Field(default=None, foreign_key="mltask.id")
    ml_task: Optional[MLTask] = Relationship(
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    def apply(self) -> None:
        if self.t_type == TransactionType.OUT:
            self.user.write_off_balance(self.amount)
        elif self.t_type == TransactionType.IN:
            self.user.topup_balance(self.amount)
