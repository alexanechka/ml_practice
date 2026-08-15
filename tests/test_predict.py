import requests

from conftest import BASE_URL, get_balance, poll_task_status, topup

EN_TEXT = (
    "The quick brown fox jumps over the lazy dog. This is a simple English "
    "paragraph written specifically to make sure the language detector "
    "confidently recognizes English text during automated end-to-end testing."
)

UNSUPPORTED_LANGUAGE_TEXT = (
    "Dit is een voorbeeldtekst geschreven in het Nederlands, gebruikt om te "
    "controleren hoe het systeem omgaat met een taal zonder beschikbaar model."
)


def _submit(headers: dict, text: str) -> str:
    response = requests.post(
        f"{BASE_URL}/predict", json={"input_data": text}, headers=headers
    )
    assert response.status_code == 202, response.text
    return response.json()["task_id"]


def test_successful_predict_charges_balance_and_returns_result(auth_session):
    headers = auth_session["headers"]
    topup(headers, 100)
    balance_before = get_balance(headers)

    task_id = _submit(headers, EN_TEXT)
    status = poll_task_status(task_id, headers)
    assert status == "done"

    result = requests.get(f"{BASE_URL}/predict/result/{task_id}", headers=headers)
    assert result.status_code == 200
    assert result.json()["responce"]

    balance_after = get_balance(headers)
    assert balance_after < balance_before


def test_predict_with_insufficient_balance_fails_without_charge(auth_session):
    headers = auth_session["headers"]
    balance_before = get_balance(headers)
    assert balance_before == 0

    task_id = _submit(headers, EN_TEXT)
    status = poll_task_status(task_id, headers)
    assert status == "failed"

    assert get_balance(headers) == balance_before


def test_predict_with_unsupported_language_fails_without_charge(auth_session):
    headers = auth_session["headers"]
    topup(headers, 100)
    balance_before = get_balance(headers)

    task_id = _submit(headers, UNSUPPORTED_LANGUAGE_TEXT)
    status = poll_task_status(task_id, headers)
    assert status == "failed"

    assert get_balance(headers) == balance_before


def test_predict_rejects_empty_input(auth_session):
    response = requests.post(
        f"{BASE_URL}/predict",
        json={"input_data": ""},
        headers=auth_session["headers"],
    )
    assert response.status_code == 422


def test_predict_requires_authorization():
    response = requests.post(f"{BASE_URL}/predict", json={"input_data": EN_TEXT})
    assert response.status_code in (401, 403)
