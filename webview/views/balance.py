import streamlit as st
import requests

API_BASE_URL = "http://localhost/api"

if "token" not in st.session_state:
    st.warning("Сначала войдите в раздел «Вход»")
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state['token']}"}

st.title("Баланс")

response = requests.get(f"{API_BASE_URL}/balance/get", headers=headers)
if response.status_code == 200:
    balance = response.json()
else:
    st.error(response.json().get("detail", "Не удалось получить баланс"))
    st.stop()

col1, col2 = st.columns([2, 1])
with col1:
    st.metric("Текущий баланс", f"{balance} кредитов")
with col2:
    st.write("")  # небольшой отступ, чтобы кнопка визуально совпала по высоте с metric
    if st.button("Пополнить баланс"):
        st.session_state["show_topup"] = not st.session_state.get("show_topup", False)

if st.session_state.get("show_topup", False):
    amount = st.number_input("Сумма пополнения", min_value=20.0, step=5.0)
    if st.button("Подтвердить пополнение"):
        topup_response = requests.post(
            f"{API_BASE_URL}/balance/topup",
            params={"amount": amount},
            headers=headers,
        )
        if topup_response.status_code == 202:
            st.success("Баланс пополнен!")
            st.session_state["show_topup"] = False
            st.rerun()
        else:
            st.error(topup_response.json().get("detail", "Ошибка пополнения"))