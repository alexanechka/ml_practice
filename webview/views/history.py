import streamlit as st
import requests
import pandas as pd

from utils import API_BASE_URL, get_headers, format_error_detail

headers = get_headers()

st.title("История операций")

STATUS_LABELS = {
    "pending": "⏳ Ожидает обработки",
    "processing": "⚙️ В обработке",
    "done": "✅ Готово",
    "failed": "❌ Ошибка",
}

TYPE_LABELS = {
    "in": "⬆️ Пополнение",
    "out": "⬇️ Списание",
}


def format_ml_history(records: list) -> pd.DataFrame:
    df = pd.DataFrame(records)
    df["h_date"] = pd.to_datetime(df["h_date"])
    df = df.sort_values("h_date", ascending=False)
    return pd.DataFrame(
        {
            "Дата": df["h_date"].dt.strftime("%d.%m.%Y %H:%M"),
            "ID задачи": df["ml_task_id"],
            "Модель": df["model_id"].apply(lambda x: f"#{int(x)}" if pd.notna(x) else "—"),
            "Стоимость": df["cost"],
            "Статус": df["status"].map(STATUS_LABELS).fillna(df["status"]),
        }
    )


def format_transactions(records: list) -> pd.DataFrame:
    df = pd.DataFrame(records)
    df["t_date"] = pd.to_datetime(df["t_date"])
    df = df.sort_values("t_date", ascending=False)
    return pd.DataFrame(
        {
            "Дата": df["t_date"].dt.strftime("%d.%m.%Y %H:%M"),
            "Тип": df["t_type"].map(TYPE_LABELS).fillna(df["t_type"]),
            "Сумма": df["amount"],
            "Связанная задача": df["ml_task_id"].apply(lambda x: int(x) if pd.notna(x) else "—"),
        }
    )


tab_ml, tab_transactions = st.tabs(["ML-запросы", "Транзакции"])

with tab_ml:
    response = requests.get(f"{API_BASE_URL}/history/ml_task/get", headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data:
            st.dataframe(format_ml_history(data), use_container_width=True, hide_index=True)
        else:
            st.info("Пока нет обработанных запросов")
    else:
        st.error(format_error_detail(response, "Не удалось загрузить историю запросов"))

with tab_transactions:
    response = requests.get(f"{API_BASE_URL}/history/transaction/get", headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data:
            st.dataframe(format_transactions(data), use_container_width=True, hide_index=True)
        else:
            st.info("Пока нет транзакций")
    else:
        st.error(format_error_detail(response, "Не удалось загрузить историю транзакций"))
