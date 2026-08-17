import streamlit as st
import requests
import pandas as pd

from utils import API_BASE_URL, get_headers, format_error_detail

headers = get_headers()

if st.session_state.get("role") != "admin":
    st.error("Доступ только для администратора")
    st.stop()

st.title("Админ-панель")

TYPE_LABELS = {
    "in": "⬆️ Пополнение",
    "out": "⬇️ Списание",
}

tab_users, tab_transactions = st.tabs(["Пользователи", "Все транзакции"])

with tab_users:
    response = requests.get(f"{API_BASE_URL}/users/get_all_users", headers=headers)
    if response.status_code == 200:
        users = response.json()
        if users:
            df = pd.DataFrame(users)[["id", "email", "role", "balance"]]
            df.columns = ["ID", "Email", "Роль", "Баланс"]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Пользователей пока нет")
    else:
        st.error(format_error_detail(response, "Не удалось загрузить список пользователей"))

    st.divider()
    st.subheader("Пополнить баланс пользователю")

    target_email = st.text_input("Email пользователя")
    amount = st.number_input("Сумма пополнения", min_value=20.0, step=5.0)

    if st.button("Пополнить"):
        topup_response = requests.post(
            f"{API_BASE_URL}/admin/balance/topup",
            params={"email": target_email, "amount": amount},
            headers=headers,
        )
        if topup_response.status_code == 202:
            st.success(topup_response.json().get("message", "Баланс пополнен"))
            st.rerun()
        else:
            st.error(format_error_detail(topup_response, "Ошибка пополнения"))

with tab_transactions:
    response = requests.get(f"{API_BASE_URL}/admin/transactions", headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data:
            df = pd.DataFrame(data)
            df["t_date"] = pd.to_datetime(df["t_date"])
            df = df.sort_values("t_date", ascending=False)
            table = pd.DataFrame(
                {
                    "Дата": df["t_date"].dt.strftime("%d.%m.%Y %H:%M"),
                    "ID пользователя": df["user_id"],
                    "Тип": df["t_type"].map(TYPE_LABELS).fillna(df["t_type"]),
                    "Сумма": df["amount"],
                }
            )
            st.dataframe(table, use_container_width=True, hide_index=True)
        else:
            st.info("Транзакций пока нет")
    else:
        st.error(format_error_detail(response, "Не удалось загрузить транзакции"))
