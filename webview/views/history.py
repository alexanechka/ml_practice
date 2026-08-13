import streamlit as st
import requests
import pandas as pd

API_BASE_URL = "http://localhost/api"

if "token" not in st.session_state:
    st.warning("Сначала войдите в раздел «Вход»")
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state['token']}"}

st.title("История операций")

tab_ml, tab_transactions = st.tabs(["ML-запросы", "Транзакции"])

with tab_ml:
    response = requests.get(f"{API_BASE_URL}/history/ml_task/get", headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data:
            st.dataframe(pd.DataFrame(data))
        else:
            st.info("Пока нет обработанных запросов")
    else:
        st.error("Не удалось загрузить историю запросов")

with tab_transactions:
    response = requests.get(f"{API_BASE_URL}/history/transaction/get", headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data:
            st.dataframe(pd.DataFrame(data))
        else:
            st.info("Пока нет транзакций")
    else:
        st.error("Не удалось загрузить историю транзакций")
