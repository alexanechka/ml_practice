from sqlmodel import SQLModel, Field, Relationship
from dataclasses import dataclass, field
from typing import Optional
import re
from enum import Enum


class Role(Enum):
    ADMIN = "admin"
    USER = "user"


class Wallet(SQLModel, table = True):
    """
    Класс для описания баланса пользователя

    Attributes:
        id (int): Идентификатор
        balance (float): Остаток кредитов
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    balance: float = 0

    def top_up(self, amount: float) -> None:
        self.balance += amount

    def write_off(self, amount: float) -> None:
        if amount > self.balance:
            raise ValueError("Недостаточно средств")
        self.balance -= amount


class User(SQLModel, table = True):
    """
    Класс для представления пользователя в системе.

    Attributes:
        id (int): Уникальный идентификатор пользователя
        email (str): Email пользователя
        password (str): Пароль пользователя
        wallet (Wallet): кошелек
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(
        ...,  # Required field
        unique=True,
        index=True,
        min_length=5,
        max_length=255
    )
    password: str = Field(..., min_length=8) 

    wallet_id: Optional[int] = Field(default=None, foreign_key="wallet.id")
    wallet: Optional[Wallet] = Relationship(
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    role: Role = Role.USER

    def _validate_email(self) -> bool:
        
        """Проверяет корректность email."""
        email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        if not email_pattern.match(self.email):
            raise ValueError("Invalid email format")
        return True

    def _validate_password(self) -> bool:
        """Проверяет минимальную длину пароля."""
        if len(self.password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return True

    @property
    def balance(self):
        return self.wallet.balance

    def topup_balance(self, amount: float):
        self.wallet.top_up(amount)

    def write_off_balance(self, amount: float):
        self.wallet.write_off(amount)
