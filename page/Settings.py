import streamlit as st
import time


if 'ssid' in st.session_state:
    st.info(f"currently log in as {st.session_state.ssid}")
else:
    st.info(f"currently log in as {st.session_state.teacher_id}")

change = st.button("change password")
logout = st.button("log out")
if logout:
    st.session_state.clear()
    st.session_state.login = False
    st.success("log out successfully")
    time.sleep(0.65)
    st.rerun()

if change:
    st.switch_page("page/ChangePassword.py")