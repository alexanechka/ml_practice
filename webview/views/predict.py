import streamlit as st
import requests
import time

API_BASE_URL = "http://localhost/api"

if "token" not in st.session_state:
    st.warning("Сначала войдите в раздел «Вход»")
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state['token']}"}

st.title("Пересказ текста")

text = st.text_area("Вставьте текст для пересказа", height=200)

if st.button("Отправить"):
    if not text.strip():
        st.error("Введите текст перед отправкой")
        st.stop()

    response = requests.post(
        f"{API_BASE_URL}/predict",
        json={"input_data": text},
        headers=headers,
    )

    if response.status_code != 202:
        st.error(response.json().get("detail", "Ошибка при отправке запроса"))
        st.stop()

    task_id = response.json()["task_id"]

    with st.spinner("Обрабатываем запрос..."):
        while True:
            status_response = requests.get(
                f"{API_BASE_URL}/predict/{task_id}", headers=headers
            )
            task_status = status_response.json()

            if task_status == "done":
                break
            if task_status == "failed":
                st.error("Не удалось обработать запрос")
                st.stop()

            time.sleep(1)

    result_response = requests.get(
        f"{API_BASE_URL}/predict/result/{task_id}", headers=headers
    )

    if result_response.status_code == 200:
        result_text = result_response.json()["responce"]
        st.success("Готово!")
        st.write(result_text)
    else:
        st.error("Не удалось получить результат")