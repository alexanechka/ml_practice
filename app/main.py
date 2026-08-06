from sqlmodel import Session
from database.database import init_db, get_database_engine
from database.config import get_settings
from models.user import User, Wallet
from models.ml_models import MLModel, InputLanguages
from services.crud.user import create_user, get_user_by_id, get_user_by_email, user_balance
from services.crud.transaction import top_up, write_off, get_user_transaction


def main() -> None:
    settings = get_settings()
    print(f"{settings.APP_NAME} v{settings.API_VERSION}")

    init_db()
    print("БД инициализирована")

    engine = get_database_engine()
    with Session(engine) as session:
        existing = get_user_by_email("test@mail.ru", session)
        if existing:
            print(f"Пользователь уже существует (id={existing.id}), используем его")
            user = existing
        else:
            wallet = Wallet(balance=0)
            user = User(email="test1@mail.ru", password="secure_password123", wallet=wallet)
            user = create_user(user, session)
            print(f"Пользователь создан: id={user.id}, email={user.email}, баланс={user.balance}")

        top_up(user.id, 100, session)
        print(f"После пополнения: баланс={get_user_by_id(user.id, session).balance}")

        write_off(user.id, 30, session)
        print(f"После списания: баланс={get_user_by_id(user.id, session).balance}")

        history = get_user_transaction(user.id, session)
        print(f"История транзакций ({len(history)}):")
        for t in history:
            print(f"  {t.t_date} | {t.t_type} | {t.amount}")

        try:
            write_off(user.id, 10000, session)
        except ValueError as e:
            print(f"Проверка баланса перед списанием сработала: {e}")

        balance = user_balance(user.id, session)
        print(balance)


if __name__ == "__main__":
    main()