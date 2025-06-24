import streamlit as st

if "current_user" not in st.session_state:
    st.session_state.current_user = None

st.set_page_config(
    page_title=f"{st.session_state.current_user}'s Profile - Adventure Board"
)

from db import get_connection, side_bar, is_empty
from time import sleep
import sqlite3

if st.session_state.current_user is None:
    st.switch_page("startup.py")

if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = False

from PIL import Image
import numpy as np
from io import BytesIO
from insightface.app import FaceAnalysis

side_bar()

st.title(f"{st.session_state.current_user}'s Profile")

col1, col2, col3 = st.columns(3)
with get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT name, profile_pic FROM Accounts WHERE username = ?", (st.session_state.current_user,))
    data = cursor.fetchone()
    name, pic_data = [x for x in data]
    with col1:
        image = st.image(pic_data, use_container_width="never")
    new_details = st.form(key="new-details")
    new_name = new_details.text_input("Name", placeholder="John Smith", value=name)
    new_username = new_details.text_input("Username", max_chars=36, value=st.session_state.current_user)
    new_pfp = new_details.file_uploader("Upload new profile picture?", type=["jpg", "jpeg", "png"])
    new_password = new_details.text_input("Password", type="password")
    update_details = new_details.form_submit_button("Update profile details")
    with col2:
        if update_details:
            if new_username != st.session_state.current_user and not is_empty(new_username):
                try:
                    cursor.execute("UPDATE Accounts SET username = ? WHERE username = ?", (new_username, st.session_state.current_user))
                    conn.commit()
                    st.session_state.current_user = new_username
                except sqlite3.IntegrityError as e:
                    msg = str(e)
                    if "Accounts.username" in msg:
                        st.error("Someone is already using this username.")
            if new_name != name and not is_empty(new_name):
                cursor.execute("UPDATE Accounts SET name = ? WHERE username = ?", (new_name, st.session_state.current_user))
                conn.commit()
            if not is_empty(new_password):
                cursor.execute("UPDATE Accounts SET password = ? WHERE username = ?", (new_password, st.session_state.current_user))
                conn.commit()
            if new_pfp:
                new_pfp_data = new_pfp.getvalue()
                img1 = np.array(Image.open(BytesIO(pic_data)).convert("RGB"))
                img2 = np.array(Image.open(BytesIO(new_pfp_data)).convert("RGB"))
                app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
                app.prepare(ctx_id=0)
                faces1 = app.get(img1)
                faces2 = app.get(img2)

                if faces1 and faces2:
                    emb1 = faces1[0].embedding
                    emb2 = faces2[0].embedding
                    similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
                    if similarity > 0.5:
                        try:
                            cursor.execute("UPDATE Accounts SET profile_pic = ? WHERE username = ?", (new_pfp_data, st.session_state.current_user))
                            conn.commit()
                            with st.spinner("Updating profile picture..."):
                                sleep(3)
                                st.rerun()
                        except sqlite3.IntegrityError as e:
                            error_msg = str(e)
                            if "Accounts.profile_pic" in error_msg:
                                st.error("That profile picture is already in use. Is someone stealing your face or are you stealing theirs? :face_with_raised_eyebrow:")
                    else:
                        st.error("Faces don't match.")
                else:
                    st.error("Could not detect faces in one or both images.")

def delete_account():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Accounts WHERE username = ?", (st.session_state.current_user,))
        conn.commit()

st.markdown("""<style>.element-container:has(.red) + div button {
                  background-color: red;
                  color: white;
}</style>""", unsafe_allow_html=True)
st.markdown("""<style>.element-container:has(#normal) + div button {
                  color: white;
}</style>""", unsafe_allow_html=True)

st.markdown("<span class='red'></span>", unsafe_allow_html=True)
delete_1 = st.button("Delete Account")
if delete_1:
    st.session_state.confirm_delete = True

if st.session_state.confirm_delete:
    st.warning("Are you sure you want to delete your account? This cannot be undone.")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<span id='normal'></span>", unsafe_allow_html=True)
        yes_delete = st.button("Yes, delete my account")
        if yes_delete:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Accounts WHERE username = ?", (st.session_state.current_user,))
                conn.commit()
            st.session_state.current_user = None
            st.session_state.confirm_delete = False

    if yes_delete:
        with st.spinner("Deleted account. Redirecting to home page..."):
            sleep(3)
            st.switch_page("startup.py")

    with col2:
        st.markdown("<span class='red'></span>", unsafe_allow_html=True)
        if st.button("Cancel"):
            st.session_state.confirm_delete = False
