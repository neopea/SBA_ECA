import streamlit as st 
from database import app , db , Student , Teacher , Activity , Notification , StudentActivity
from datetime import datetime , date
import pandas as pd
st.set_page_config(layout="wide")


def display_message(message : Notification):
    with st.container(border=True):
        col1 , col2 , col3= st.columns([0.5,8 , 4])
        with col1:
            if message.is_read:
                st.markdown("➤")
            else:
                st.markdown("🔔")
        with col2:
            if message.activity == None:
                st.markdown(f"From : {message.teacher.name}")
            else:
                st.markdown(f"From : {message.teacher.name} | {message.activity.name }")
            st.markdown(f"{message.title}")
            st.markdown(str(message.create_time.strftime("%Y-%m-%d %H:%M:%S")))
        with col3:
            with st.container(vertical_alignment="top"):
                if st.button("View Content", key=message.notification_id):
                    st.session_state.selected_message_id = message.notification_id


with app.app_context():
    student = db.session.get(Student , st.session_state.ssid)
    stmt = db.select(Notification).where(Notification.student_ssid == st.session_state.ssid)
    all_acts = db.session.execute(db.select(Activity)).scalars().all()
    all_acts.sort(key=lambda x : x.name)
    all_teachers = db.session.execute(db.select(Teacher)).scalars().all()
    all_teachers.sort(key=lambda x : x.name)

    st.title("📨 INBOX")
    st.subheader(f"{student.name} {student.class_form} ({student.class_number})")

    col1 , col2 , col3  = st.columns(3)
    total_message = db.session.execute(db.select(Notification).where(Notification.student_ssid == st.session_state.ssid)).scalars().all()
    new_message = 0
    unread_message = 0
    warning_message = 0
    new_warning_message = 0
    new_unread_message = 0

    for i in total_message:
        new = False
        if (i.create_time.date() - date.today()).days < 3:
            new_message += 1
            new = True
        if not i.is_read:
            unread_message += 1
            if new:
                new_unread_message += 1
        if i.title == "Warning":
            warning_message += 1
            if new:
                new_warning_message += 1

        
    col1.metric("📬Total message" , len(total_message) , delta=new_message)
    col2.metric("🔔Unread message" , unread_message , delta=new_unread_message)
    col3.metric("🚨Warnings" , 0 , delta=new_warning_message)


    with st.container(border=True , horizontal=True , vertical_alignment="bottom"):
        searching_text = st.text_input("Search by text:")
        act_filter = st.selectbox("Filter by Activity:" , options=["--All--"] + all_acts , format_func= lambda x : x.name if x != "--All--" else x)
        if act_filter != "--All--":
            act_id = act_filter.activity_id
            stmt= stmt.where(Notification.activity_id == act_id )
        teacher_filter = st.selectbox("Filter by Teacher:" , options=["--All--"] +all_teachers , format_func= lambda x : x.name if x != "--All--" else x)
        if teacher_filter != "--All--":
            teacher_id = teacher_filter.teacher_id
            stmt = stmt.where(Notification.teacher_id == teacher_id)



        if st.checkbox("Unread Message Only"):
            stmt = stmt.where(Notification.is_read == False)


    cola , colb = st.columns([4 , 6])

    with cola:
        with st.container(border=True):
            st.markdown("### Messages")
            stmt = stmt.where(Notification.message.like(f"%{searching_text}%"))
            all_message = db.session.execute(stmt).scalars().all()
            for i in all_message:
                display_message(i)


    with colb:
        with st.container(border=True):
            st.markdown("### Reading pane")
            if "selected_message_id" not in st.session_state:
                st.info("Select message to view details")
            else:
                message = db.session.get(Notification , st.session_state.selected_message_id)
                with st.container(border=True):
                    colx , coly = st.columns([3,7])
                    with colx:
                        st.markdown(f"Title :")
                        st.markdown("Activity :")
                        st.markdown("From    : ")
                        st.markdown(f"Send At :")
                        st.markdown("Status:")

                    with coly:
                        st.markdown(f"{message.title}")
                        if message.activity_id != None:
                            st.markdown(f"{message.activity.name}")
                        else:
                            st.markdown("N/A")
                        st.markdown(f"{message.teacher.name}  ({message.teacher.teacher_id})")
                        st.markdown(message.create_time.strftime('%Y-%m-%d %H:%M:%S'))
                        if message.is_read:
                            st.badge("Read", icon=":material/check:", color="green")
                        else:
                            st.badge("Unread" , icon="✉️" , color="yellow")

                    st.divider()
                    st.info(message.message)
                    if not message.is_read:
                        if st.button("Mark As Read"):
                            message.is_read = True
                            db.session.commit()
                            print(all_message[0].is_read)
                            st.rerun()
                    