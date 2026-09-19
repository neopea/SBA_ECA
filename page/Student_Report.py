import streamlit as st 
from database import app , db , Student , Teacher , Activity , Notification , StudentActivity , Award , Attendance
from datetime import datetime , date
import pandas as pd
import io
import streamlit as st

st.title("Activity Tracker")
# Streamlit Download Button Handler
with app.app_context():
    student = db.session.get(Student , st.session_state.ssid)
    result = db.session.execute(db.select(StudentActivity).where(StudentActivity.student_ssid == st.session_state.ssid , StudentActivity.status != "Rejected"
                                                                )).scalars().all()
    st.subheader("Activities")
    act_dict= {}
    for student_act in result:
        act_id = student_act.activity_id
        if act_id not in act_dict.keys():
            act_dict[act_id] = [student_act]
        else:
            act_dict[act_id].append(student_act)
            act_dict[act_id].sort(key=lambda x : x.academic_year[0:3])

    for keys , values in act_dict.items():
        act = db.session.get(Activity , keys)
        with st.expander(act.name):
            col1 , col2 , col3 = st.columns(3)
            with col1:
                st.subheader(f"{act.name} Records")
                for student_act in values:
                    st.write(student_act.academic_year , student_act.role)


            with col2:
                st.subheader("Awards")
                award_li = db.session.execute(db.select(Award).where(Award.student_ssid == st.session_state.ssid , 
                                                                    Award.activity_id == keys)).scalars().all()
                if award_li == []:
                    st.info("No Related Awards")
                for award in award_li:
                    if award.activity_id == keys:
                        with st.container(border=True):
                            st.write(award.award_name , award.date_awarded )
                            st.write(f"Level : {award.level}")
                            st.write(f"Rank : {award.rank}")

            with col3:
                st.subheader("Lesson Time")
                stmt = db.select(Attendance).where(Attendance.student_ssid == st.session_state.ssid , 
                                                Attendance.activity_id == keys,
                                                Attendance.status == "Present")
                counter = len(db.session.execute(stmt).scalars().all()) * 2
                st.subheader(str(counter) + " hours")


