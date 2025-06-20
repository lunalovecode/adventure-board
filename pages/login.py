import streamlit as st

st.set_page_config(
    page_title="Log in to Adventure Board"
)

import startup
import bcrypt
import sqlite3
from db import get_connection
from time import sleep

if "current_user" not in st.session_state:
    st.session_state.current_user = None

login_form = st.form(key="login")
username = login_form.text_input("Username", max_chars=50)
password = login_form.text_input("Password", type="password")
log_in = login_form.form_submit_button("Log in")
st.write("New here?")
st.page_link("pages/create-account.py", label="Create an account")
if log_in:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM Accounts WHERE username = ?", (username,))
        conn.commit()
        exists = cursor.fetchone()
        if exists:
            stored_hash = exists[0]
            if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
                st.success("Logged in!")
                st.session_state.current_user = username
                with st.spinner("Redirecting to home page..."):
                    sleep(5)
                    st.switch_page("pages/home.py")
            else:
                st.error("Username or password is incorrect")
        else:
            st.error("Username or password is incorrect")
