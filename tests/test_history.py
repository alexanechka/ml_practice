import requests

from conftest import BASE_URL, poll_task_status, topup, unique_email

EN_TEXT = (
    "Automated testing helps teams catch regressions early and ship "
    "features with more confidence across the whole system end to end."
)


def test_transaction_history_records_topup(auth_session):
    headers = auth_session["headers"]
    topup(headers, 50)

    response = requests.get(f"{BASE_URL}/history/transaction/get", headers=headers)
    assert response.status_code == 200
    transactions = response.json()
    assert any(t["amount"] == 50 and t["t_type"] == "in" for t in transactions)


def test_ml_task_history_records_successful_request(auth_session):
    headers = auth_session["headers"]
    topup(headers, 100)

    response = requests.post(
        f"{BASE_URL}/predict", json={"input_data": EN_TEXT}, headers=headers
    )
    task_id = response.json()["task_id"]
    poll_task_status(task_id, headers)

    history = requests.get(f"{BASE_URL}/history/ml_task/get", headers=headers)
    assert history.status_code == 200
    records = history.json()
    assert len(records) == 1
    assert records[0]["status"] == "done"


def test_ml_task_history_records_failed_request(auth_session):
    headers = auth_session["headers"]
    # баланс не пополняем — запрос гарантированно провалится

    response = requests.post(
        f"{BASE_URL}/predict", json={"input_data": EN_TEXT}, headers=headers
    )
    task_id = response.json()["task_id"]
    poll_task_status(task_id, headers)

    history = requests.get(f"{BASE_URL}/history/ml_task/get", headers=headers)
    assert history.status_code == 200
    records = history.json()
    assert len(records) == 1
    assert records[0]["status"] == "failed"


def test_failed_predict_creates_no_out_transaction(auth_session):
    """При провале ML-запроса (например, из-за нехватки средств) в истории
    транзакций не должно появляться списание (OUT)."""
    headers = auth_session["headers"]
    # баланс не пополняем — запрос гарантированно провалится из-за нехватки средств

    response = requests.post(
        f"{BASE_URL}/predict", json={"input_data": EN_TEXT}, headers=headers
    )
    task_id = response.json()["task_id"]
    status = poll_task_status(task_id, headers)
    assert status == "failed"

    history = requests.get(f"{BASE_URL}/history/transaction/get", headers=headers)
    assert history.status_code == 200
    transactions = history.json()
    assert not any(t["t_type"] == "out" for t in transactions)


def test_history_is_isolated_per_user(auth_session):
    """История одного пользователя не должна быть видна другому."""
    headers = auth_session["headers"]
    topup(headers, 20)

    other_email = unique_email()
    other_password = "TestPass123"
    signup = requests.post(
        f"{BASE_URL}/auth/signup",
        json={"email": other_email, "password": other_password},
    )
    assert signup.status_code == 201

    other_login = requests.post(
        f"{BASE_URL}/auth/signin",
        json={"email": other_email, "password": other_password},
    )
    assert other_login.status_code == 200
    other_headers = {
        "Authorization": f"Bearer {other_login.json()['access_token']}"
    }

    response = requests.get(
        f"{BASE_URL}/history/transaction/get", headers=other_headers
    )
    assert response.status_code == 200
    assert response.json() == []
