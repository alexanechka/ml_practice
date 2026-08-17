import streamlit as st
import requests
import time
from utils import API_BASE_URL, get_headers, get_balance

headers = get_headers()

st.title("Пересказ текста")
balance_response = requests.get(f"{API_BASE_URL}/balance/get", headers=headers)
if balance_response.status_code == 200:
    balance = balance_response.json()
    st.info(f"💰 Баланс: {balance} кредитов")


text = st.text_area("Вставьте текст для пересказа", height=200)

if st.button("Отправить"):
    if not text.strip():
        st.error("Введите текст перед отправкой")
        st.stop()

    start = time.monotonic()

    with st.status("Отправляем запрос...", expanded=True) as status:
        response = requests.post(
            f"{API_BASE_URL}/predict",
            json={"input_data": text},
            headers=headers,
        )

        if response.status_code != 202:
            status.update(label="Ошибка при отправке запроса", state="error")
            st.error(response.json().get("detail", "Ошибка при отправке запроса"))
            st.stop()

        task_id = response.json()["task_id"]
        st.toast("Запрос отправлен на обработку", icon="📨")
        status.update(label=f"Запрос принят, ID: {task_id}")

        attempts = 0
        while True:
            attempts += 1
            status_response = requests.get(
                f"{API_BASE_URL}/predict/{task_id}", headers=headers
            )
            task_status = status_response.json()

            status.update(label=f"Статус: {task_status} (попытка {attempts})")

            if task_status == "done":
                status.update(label="Готово!", state="complete")
                break
            if task_status == "failed":
                status.update(label="Обработка завершилась ошибкой", state="error")
                st.error("Не удалось обработать запрос")
                st.caption(f"ID задачи: `{task_id}`")
                st.stop()

            time.sleep(1)

    result_response = requests.get(
        f"{API_BASE_URL}/predict/result/{task_id}", headers=headers
    )

    elapsed = time.monotonic() - start

    if result_response.status_code == 200:
        result_text = result_response.json()["responce"]
        st.success("Готово!")
        st.write(result_text)
        st.caption(f"ID задачи: `{task_id}` · обработано за {elapsed:.1f} сек.")
        st.rerun()
    else:
        st.error("Не удалось получить результат")
        st.caption(f"ID задачи: `{task_id}`")
