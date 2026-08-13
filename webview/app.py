import streamlit as st

st.set_page_config(page_title="ML Service", page_icon="🤖")

home_page = st.Page("views/home.py", title="Главная", icon="🤖")
login_page = st.Page("views/login.py", title="Вход / Регистрация", icon="🔑")
balance_page = st.Page("views/balance.py", title="Личный кабинет", icon="💼")
history_page = st.Page("views/history.py", title="История операций", icon="📋")
predict_page = st.Page("views/predict.py", title="Обработка текста", icon="🤖")

pg = st.navigation([home_page, login_page, balance_page, history_page, predict_page])
pg.run()
