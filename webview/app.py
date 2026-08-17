import streamlit as st

st.set_page_config(page_title="ML Service", page_icon="🤖")

home_page = st.Page("views/home.py", title="Главная", icon="🤖")
login_page = st.Page("views/login.py", title="Вход / Регистрация", icon="🔑")
balance_page = st.Page("views/balance.py", title="Личный кабинет", icon="💼")
history_page = st.Page("views/history.py", title="История операций", icon="📋")
predict_page = st.Page("views/predict.py", title="Обработка текста", icon="🤖")
admin_page = st.Page("views/admin.py", title="Админ-панель", icon="🛠️")

if "token" in st.session_state:
    pages = [home_page, predict_page, balance_page, history_page]
    if st.session_state.get("role") == "admin":
        pages.append(admin_page)
else:
    pages = [home_page, login_page]

pg = st.navigation(pages)

if "token" in st.session_state:
    with st.sidebar:
        st.divider()
        st.caption(f"Вы вошли как {st.session_state.get('email')}")
        if st.button("Выйти", use_container_width=True):
            st.session_state.clear()
            st.switch_page("views/home.py")

pg.run()
