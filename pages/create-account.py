import streamlit as st
import bcrypt

st.set_page_config(
    page_title="Create an Adventure Board account"
)

import sqlite3
from db import get_connection, is_empty
import re
from time import sleep

if "current_user" not in st.session_state:
    st.session_state.current_user = None

account_form = st.form(key="account")
name = account_form.text_input("Name", placeholder="John Smith")
username = account_form.text_input("Username", max_chars=36)
profile_picture = account_form.camera_input("Take a picture of your beautiful face!")
password = account_form.text_input("Password", type="password")
create = account_form.form_submit_button("Create Account")
valid_username_regex = "^[A-Za-z][A-Za-z0-9_]{7,36}$"
st.write("Have an account?")
st.page_link("pages/login.py", label="Login")
if create:   
    if is_empty(name):
        st.error("Please write your real name. We swear, we won't use it for anything else.")
    elif is_empty(username):
        st.error("Please provide a unique username.")
    elif len(username) < 7:
        st.error("Your username is too short.")
    elif not re.search(valid_username_regex, username):
        st.error("Your username should not contain any special characters. You're special enough!")
    elif profile_picture is None:
        st.error("Please take a picture of your (beautiful/handsome/any compliment you prefer) face so we can know you're a real person.")
    elif is_empty(password):
        st.error("Please provide a password.")
    else:
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        picture_data = profile_picture.read()
        with get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO Accounts VALUES (?, ?, ?, ?)", (name, username, picture_data, hashed))
                conn.commit()
                st.session_state.current_user = username
                st.success("Created your new account!")
                with st.spinner("Logging in..."):
                    sleep(5)
                st.switch_page("pages/home.py")
            except sqlite3.IntegrityError as e:
                error_msg = str(e)
                if "Accounts.username" in error_msg:
                    st.error("That username is already in use.")
                elif "Accounts.profile_pic" in error_msg:
                    st.error("That profile picture is already in use. Is someone stealing your face or are you stealing theirs? :face_with_raised_eyebrow:")
