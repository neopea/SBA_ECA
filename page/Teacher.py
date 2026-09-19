import streamlit as st



if st.session_state.login == True:
    pass
else:
    st.warning("This page is only avaliable to TEACHERS, please log in. ")
    st.stop()

