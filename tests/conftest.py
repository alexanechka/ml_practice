import os
import time
import uuid

import psycopg
import pytest
import requests

BASE_URL = os.environ.get("TEST_BASE_URL", "http://localhost/api")
ROOT_URL = BASE_URL.removesuffix("/api")
DB_DSN = os.environ.get(
    "TEST_DB_DSN",
    "postgresql://ml_service:secret_password_123@localhost:5432/ml_service_db",
)

POLL_INTERVAL = 1
# Реальная генерация через Ollama (gemma3:1b) может занимать десятки секунд,
# особенно на первом запросе, пока модель прогревается в памяти — 30с было мало
# для инстанс-заглушки, для настоящей модели нужен запас побольше.
POLL_TIMEOUT = 120


@pytest.fixture(scope="session", autouse=True)
def wait_for_api():
    """Smoke-тест: система вообще поднята и отвечает, прежде чем гонять остальные тесты.
    Соответствует Шагу 1 плана задания №7 ('Убедиться, что все сервисы запущены')."""
    try:
        response = requests.get(f"{ROOT_URL}/health", timeout=5)
    except requests.exceptions.ConnectionError:
        pytest.exit(
            f"Не удалось подключиться к {ROOT_URL}. Убедитесь, что 'docker compose up -d' выполнен.",
            returncode=1,
        )
    assert response.status_code == 200, f"API не готово: {response.status_code} {response.text}"
    assert response.json().get("status") == "healthy"


@pytest.fixture(scope="session", autouse=True)
def ensure_models_seeded(wait_for_api):
    """Гарантирует, что в БД есть модель хотя бы для EN и RU перед прогоном тестов —
    без этого любой ML-запрос падает с 'No model to get summary of text on language'."""
    with psycopg.connect(DB_DSN, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT language FROM mlmodel")
            existing = {row[0] for row in cur.fetchall()}
            if "EN" not in existing:
                cur.execute(
                    "INSERT INTO mlmodel (model_description, request_cost, language) "
                    "VALUES (%s, %s, %s)",
                    ("test EN model", 5, "EN"),
                )
            if "RU" not in existing:
                cur.execute(
                    "INSERT INTO mlmodel (model_description, request_cost, language) "
                    "VALUES (%s, %s, %s)",
                    ("test RU model", 5, "RU"),
                )
    yield


def unique_email() -> str:
    return f"test_{uuid.uuid4().hex[:12]}@test.ru"


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_data(wait_for_api):
    """После прогона удаляет всех тестовых пользователей (email вида test_<hex>@test.ru)
    и все связанные с ними записи, чтобы БД не засорялась тестовыми данными."""
    yield
    with psycopg.connect(DB_DSN, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, wallet_id FROM \"user\" WHERE email ~ %s",
                (r"^test_[0-9a-f]{12}@test\.ru$",),
            )
            rows = cur.fetchall()
            if not rows:
                return

            user_ids = [row[0] for row in rows]
            wallet_ids = [row[1] for row in rows if row[1] is not None]

            cur.execute(
                "DELETE FROM mlresponce WHERE ml_task_id IN "
                "(SELECT id FROM mltask WHERE user_id = ANY(%s))",
                (user_ids,),
            )
            cur.execute("DELETE FROM mltaskhistory WHERE user_id = ANY(%s)", (user_ids,))
            cur.execute("DELETE FROM transaction WHERE user_id = ANY(%s)", (user_ids,))
            cur.execute("DELETE FROM mltask WHERE user_id = ANY(%s)", (user_ids,))
            cur.execute('DELETE FROM "user" WHERE id = ANY(%s)', (user_ids,))
            if wallet_ids:
                cur.execute("DELETE FROM wallet WHERE id = ANY(%s)", (wallet_ids,))


@pytest.fixture
def new_user():
    """Регистрирует нового пользователя со случайным email на каждый тест."""
    email = unique_email()
    password = "TestPass123"
    response = requests.post(
        f"{BASE_URL}/auth/signup", json={"email": email, "password": password}
    )
    assert response.status_code == 201, response.text
    return {"email": email, "password": password}


@pytest.fixture
def auth_session(new_user):
    """Регистрирует и логинит пользователя, возвращает данные + заголовок авторизации."""
    response = requests.post(
        f"{BASE_URL}/auth/signin",
        json={"email": new_user["email"], "password": new_user["password"]},
    )
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {
        **new_user,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
    }


def poll_task_status(task_id: str, headers: dict, timeout: int = POLL_TIMEOUT) -> str:
    """Опрашивает статус ML-задачи, пока она не завершится (done/failed) или не истечёт таймаут."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        response = requests.get(f"{BASE_URL}/predict/{task_id}", headers=headers)
        assert response.status_code == 200, response.text
        status = response.json()["status"]
        if status in ("done", "failed"):
            return status
        time.sleep(POLL_INTERVAL)
    raise TimeoutError(f"Задача {task_id} не завершилась за {timeout} секунд")


def topup(headers: dict, amount: float) -> None:
    response = requests.post(
        f"{BASE_URL}/balance/topup", params={"amount": amount}, headers=headers
    )
    assert response.status_code == 202, response.text


def get_balance(headers: dict) -> float:
    response = requests.get(f"{BASE_URL}/balance/get", headers=headers)
    assert response.status_code == 200, response.text
    return response.json()
