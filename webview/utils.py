import streamlit as st
import requests
import os

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost/api")

def get_headers() -> dict:
    """Проверяет авторизацию и возвращает заголовок с токеном.
    Если токена нет — сразу показывает предупреждение и останавливает страницу."""
    if "token" not in st.session_state:
        st.warning("Сначала войдите в раздел «Вход»")
        st.stop()
    return {"Authorization": f"Bearer {st.session_state['token']}"}


def get_balance(headers: dict):
    response = requests.get(f"{API_BASE_URL}/balance/get", headers=headers)
    if response.status_code == 200:
        return response.json()
    return None


def get_current_user_info(headers: dict):
    """Возвращает профиль текущего пользователя (id, email, role, balance) или None."""
    response = requests.get(f"{API_BASE_URL}/users/me", headers=headers)
    if response.status_code == 200:
        return response.json()
    return None


def format_error_detail(response, fallback: str = "Неизвестная ошибка") -> str:
    """Достаёт понятное текстовое сообщение из ответа FastAPI.
    detail бывает строкой (наши HTTPException) или списком ошибок валидации pydantic (422)."""
    try:
        detail = response.json().get("detail", fallback)
    except ValueError:
        return fallback

    if isinstance(detail, list):
        return "; ".join(item.get("msg", str(item)) for item in detail)
    return str(detail)