import streamlit as st 
from database import app , db , Student , Teacher , Activity , Notification , StudentActivity
from datetime import datetime , date
import pandas as pd
st.set_page_config(layout="wide")
def get_attendance(student:Student):
    counter = 0
    if len(student.attendance_records) == 0:
        return 0.0
    for i in student.attendance_records:
        if i.status == "Present":
            counter += 1
    return round(counter / len(student.attendance_records) * 100)


def send_message(activity_id , student_ssid , teacher_id, title  , category, message):
    with app.app_context():
        new_notification = Notification(
        teacher_id=teacher_id,
        student_ssid=student_ssid,
        activity_id=activity_id,
        title=title,      
        message=message,
        is_read=False,
        category = category,
        create_time=date.today()
    )
    
    db.session.add(new_notification)
    db.session.commit()

with app.app_context():
    all_acts = db.session.execute(db.select(Activity.name).order_by(Activity.name)).scalars().all()
    all_students = db.session.execute(db.select(Student).distinct().order_by(Student.name)).scalars().all()

    all_class = db.session.execute(db.select(Student.class_form).distinct().order_by(Student.class_form)).scalars().all()
    student_df = [{
        "SSID" : i.ssid,
        "Name" : i.name,
        "Class" : i.class_form,
        "Attendance Rate (%)" : get_attendance(i)
        
    } for i in all_students]
    student_df = pd.DataFrame(student_df)
    st.title("Message")

    tab1, tab2 = st.tabs(["📤 Send Notification", "🗂️ Sent History"])

    with tab1:
        cola , colb = st.columns([6,4])
        with cola:
            if "message_from_searching" not in st.session_state:
                st.session_state.message_from_searching = False
            if not st.session_state.message_from_searching:
                st.subheader("Send message")
                col1 , col2 = st.columns(2)
                with col1:
                    act_filter = st.selectbox(label="Filter by Activity" , options=["--All--"] + all_acts )
                with col2:
                    class_filter = st.selectbox(label="Filter by Class" , options=["--All--"] + all_class )
                with st.container():
                    display_df = student_df
                    if act_filter != "--All--":
                        act_selected = db.session.execute(db.select(Activity).where(Activity.name == act_filter)).scalars().first()
                        ssid_joined = [x.student_ssid for x in act_selected.enrollments]
                        display_df = display_df[display_df["SSID"].isin(ssid_joined)]
                    if class_filter != "--All--":
                        display_df = display_df[display_df["Class"] == class_filter]    
                    student_options = display_df["SSID"]
            else: # from searching
                li = []
                for key in st.session_state.student_selected.keys():
                    i = db.session.get(Student , key)
                    li.append({
                    "SSID" : i.ssid,
                    "Name" : i.name,
                    "Class" : i.class_form,
                    "Attendance Rate (%)" : get_attendance(i)})
                display_df = pd.DataFrame(li)
                
            






            display_df = display_df.sort_values(by=["Class" , "Name"]).reset_index(drop=True)
            result = st.dataframe(display_df , hide_index=True , on_select="rerun" ,selection_mode="multi-row")
            indexs = result.selection["rows"]


            if st.session_state.message_from_searching:
                act_filter = st.selectbox(label="Add related Activity" , options=all_acts )
                act_id = db.session.execute(db.select(Activity.activity_id).where(Activity.name == act_filter)).scalars().all()[0]

                if st.button("CANCEL , go back to searching"):
                    st.session_state.message_from_searching = False
                    st.switch_page("page/Teacher_searching.py")
            with colb:
                category = st.selectbox(label="Category" , options=["General", "Activity Update", "Warning"])
                title = st.text_input("Title")
                content = st.text_area(label="Content")
                act_checkbox = act_filter == "--All--"
                if act_filter == "--All--" or "act_checkbox" not in st.session_state:
                    st.session_state.act_checkbox = False
                include_id = st.checkbox("Include Activities ID"  , key="act_checkbox" , disabled=act_checkbox)
                if st.button("Sent Message" , disabled= (indexs==  [] or content == "") ):
                    for i in indexs:
                        ssid = display_df.iloc[i]["SSID"]
                        act_id = db.session.execute(db.select(Activity.activity_id).where(Activity.name == act_filter)).scalars().first()
                        send_message(activity_id= act_id if include_id else None ,category=category , student_ssid=ssid ,  title=title , message=content, teacher_id= st.session_state.teacher_id)
                    st.toast(f"Message sent successfully to {len(indexs)} student(s)")

    with tab2:
        stmt = db.select(Notification).where(Notification.teacher_id == st.session_state.teacher_id)

        col4 , col5 , col6 = st.columns(3)
        with col4:
            search_text = st.text_input("Search by keyword")
        with col5:
            act_filter = st.selectbox("Filter by activity" , options=["--All--"] + all_acts)
        with col6:
            start_date = st.date_input("Start from" , value="20250901")
            end_date = st.date_input("Until")

        if search_text != "":
            stmt = stmt.where(Notification.message.like(f"%{search_text}%"))
        if act_filter != "--All--":
            act_id = db.session.execute(db.select(Activity.activity_id).where(Activity.name == act_filter)).scalars().first()
            stmt = stmt.where(Notification.activity_id == act_id)

        stmt = stmt.where( start_date <= Notification.create_time, Notification.create_time <= end_date)
        def display_message(message : Notification):
            with st.expander(f"Message to {message.student_ssid} at {message.create_time.date()} "):
                st.write(message.message)
        all_message = db.session.execute(stmt).scalars().all()
        print(all_message)

        if all_message != []:
            for i in range(len(all_message)):
                display_message(all_message[i])
        else:
            st.info("NO MESSAGE FOUND")