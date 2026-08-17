import requests

from conftest import BASE_URL, unique_email


def test_signup_creates_new_user():
    email = unique_email()
    response = requests.post(
        f"{BASE_URL}/auth/signup", json={"email": email, "password": "TestPass123"}
    )
    assert response.status_code == 201


def test_signup_with_existing_email_is_rejected(new_user):
    response = requests.post(
        f"{BASE_URL}/auth/signup",
        json={"email": new_user["email"], "password": "AnotherPass123"},
    )
    assert response.status_code == 409


def test_signin_with_correct_credentials(new_user):
    response = requests.post(
        f"{BASE_URL}/auth/signin",
        json={"email": new_user["email"], "password": new_user["password"]},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_signin_with_wrong_password_is_rejected(new_user):
    response = requests.post(
        f"{BASE_URL}/auth/signin",
        json={"email": new_user["email"], "password": "WrongPassword1"},
    )
    assert response.status_code == 403


def test_signin_with_nonexistent_email_is_rejected():
    response = requests.post(
        f"{BASE_URL}/auth/signin",
        json={"email": unique_email(), "password": "SomePassword1"},
    )
    assert response.status_code == 404


def test_repeated_signin_keeps_working(new_user):
    """Повторная авторизация тем же пользователем не должна ломаться."""
    for _ in range(2):
        response = requests.post(
            f"{BASE_URL}/auth/signin",
            json={"email": new_user["email"], "password": new_user["password"]},
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
