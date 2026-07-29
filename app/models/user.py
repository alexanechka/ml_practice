from dataclasses import dataclass, field
import re
from enum import Enum


class Role(Enum):
    ADMIN = "admin"
    USER = "user"


@dataclass
class Wallet:
    """
    Класс для описания баланса пользователя

    Attributes:
        balance (float): Остаток кредитов
    """

    balance: float = 0

    def top_up(self, amount: float) -> None:
        self.balance += amount

    def write_off(self, amount: float) -> None:
        if amount > self.balance:
            raise ValueError("Недостаточно средств")
        self.balance -= amount


@dataclass
class User:
    """
    Класс для представления пользователя в системе.

    Attributes:
        id (int): Уникальный идентификатор пользователя
        email (str): Email пользователя
        password (str): Пароль пользователя
        wallet (Wallet): кошелек
    """

    id: int
    email: str
    password: str
    wallet: Wallet
    role: Role = Role.USER

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

    @property
    def balance(self):
        return self.wallet.balance

    def topup_balance(self, amount: float):
        self.wallet.top_up(amount)

    def write_off_balance(self, amount: float):
        self.wallet.write_off(amount)
