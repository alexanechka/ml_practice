import requests

from conftest import BASE_URL, get_balance, topup


def test_initial_balance_is_zero(auth_session):
    assert get_balance(auth_session["headers"]) == 0


def test_topup_increases_balance(auth_session):
    headers = auth_session["headers"]
    before = get_balance(headers)

    topup(headers, 100)

    after = get_balance(headers)
    assert after == before + 100


def test_multiple_topups_accumulate(auth_session):
    headers = auth_session["headers"]

    for _ in range(3):
        topup(headers, 10)

    assert get_balance(headers) == 30


def test_topup_with_non_positive_amount_is_rejected(auth_session):
    response = requests.post(
        f"{BASE_URL}/balance/topup",
        params={"amount": 0},
        headers=auth_session["headers"],
    )
    assert response.status_code == 500
