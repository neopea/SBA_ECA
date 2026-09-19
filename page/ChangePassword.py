import streamlit as st
from  database import Student ,Teacher, app , db 





def ChangePassword():

    current = st.text_input("current password" , type= "password")
    new = st.text_input("new password" , type= "password")
    verify = st.text_input("confirm again new password", type= "password")
    submit = st.button("Submit")


    if st.session_state.identity == "student":
        user = db.session.get(Student , st.session_state.ssid)

    else:
        user = db.session.get(Teacher ,st.session_state.teacher_id)

    if submit:
        if not user.check_password(current):
            st.warning("Wrong current password")
        elif new == '':
            st.warning("new password cannot be empty")
        elif new == verify:
            st.success("Password updated")
            user.set_password(new)
            db.session.add(user)
            db.session.commit()
        else:
            st.warning("verify New password not same as new password")

with app.app_context():
    ChangePassword()