import streamlit as st
import requests
from utils import API_BASE_URL, format_error_detail

st.title("Вход / Регистрация")

if "token" in st.session_state:
    st.success(f"Вы вошли как {st.session_state.get('email')}")
    if st.button("Выйти"):
        st.session_state.clear()
        st.switch_page("views/home.py")

else:
    tab_login, tab_signup = st.tabs(["Войти", "Зарегистрироваться"])

    with tab_login:
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Пароль", type="password", key="login_password")

        if st.button("Войти"):
            response = requests.post(
                f"{API_BASE_URL}/auth/signin",
                json={"email": login_email, "password": login_password},
            )
            if response.status_code == 200:
                st.session_state["token"] = response.json()["access_token"]
                st.session_state["email"] = login_email
                st.switch_page("views/home.py")
            else:
                st.error(format_error_detail(response, "Ошибка входа"))

    with tab_signup:
        signup_email = st.text_input("Email", key="signup_email")
        signup_password = st.text_input(
            "Пароль", type="password", key="signup_password"
        )

        if st.button("Зарегистрироваться"):
            response = requests.post(
                f"{API_BASE_URL}/auth/signup",
                json={"email": signup_email, "password": signup_password},
            )
            if response.status_code == 201:
                login_response = requests.post(
                    f"{API_BASE_URL}/auth/signin",
                    json={"email": signup_email, "password": signup_password},
                )
                if login_response.status_code == 200:
                    st.session_state["token"] = login_response.json()["access_token"]
                    st.session_state["email"] = signup_email
                    st.switch_page("views/home.py")
                else:
                    st.error("Регистрация прошла, но не удалось войти автоматически")
            else:
                st.error(format_error_detail(response, "Ошибка регистрации"))
