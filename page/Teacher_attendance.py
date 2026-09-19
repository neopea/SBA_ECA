import streamlit as st
import pandas as pd
from sqlalchemy.orm import selectinload
from database import app, db, Student, Activity, StudentActivity, Award, Attendance, Teacher
from page.Teacher_searching import display_student , display_act
from datetime import datetime

def color_df(status):
    colors = {
        "Present": "background-color: #4bd43b; color: #155724",
        "Absent": "background-color: #f8d7da; color: #721c24",
        "Sick Leave": "background-color: #ffecb3; color: #7a5c00",
        "Personal Leave": "background-color: #fffde7; color: #6b5c33"
    }
    return colors[status]

st.title("Attendance")
year = datetime.today().year
if datetime.today() > datetime(datetime.today().year , 9 ,1 ):
    current_academic_year = f"{year}-{year+1}"
else:
    current_academic_year = f"{year-1}-{year}"
with app.app_context():
    teacher = db.session.get(Teacher, st.session_state.teacher_id)
    acts = teacher.activities_in_charge
    if not acts:
        st.info("No activities in charge")
        st.stop()
    act_selected = st.selectbox("Select Activity", options=acts , format_func= lambda x : x.name)
    date = st.date_input("Attendance Date" , value=datetime.today())

    if "current_act_id" not in st.session_state:
        st.session_state.current_act_id = act_selected.activity_id

        
    if "student_df" not in st.session_state or  st.session_state.current_act_id != act_selected.activity_id:
        act = db.session.get(Activity, act_selected.activity_id)
        student_li = []
        for x in act.enrollments:
            if x.academic_year == current_academic_year:
                student_li.append(x.student )
        student_df = [{
            "SSID" : i.ssid,
            "Name" : i.name,
            "Class" : i.class_form,
            "Status" : "Present"
        } for i in student_li]        
        student_df = pd.DataFrame(student_df)
        student_df = student_df.sort_values(by=["Class" , "Name"] , ascending=[True , True]).reset_index(drop=True )
        print(student_df)
        st.session_state.student_df = student_df
        st.session_state.current_act_id = act_selected.activity_id

    col1 , col2, col3 , col4 , col5 = st.columns(5)
    
    display_df = st.session_state.student_df.copy()
    display_df = display_df.style.map(color_df , subset=["Status"])

    result = st.dataframe(display_df , hide_index=True , on_select="rerun" ,selection_mode="multi-row")

    indexs = result.selection["rows"]

    with col1:
        if st.button("Mark As Absent" , width="stretch" , disabled=indexs == []):
            for index in indexs:
                st.session_state.student_df.at[index ,"Status"] = "Absent" 
            st.rerun()
    with col2:
        if st.button("Mark As Sick Leave", width="stretch" , disabled=indexs == []):
            for index in indexs:
                st.session_state.student_df.at[index ,"Status"] = "Sick Leave" 
            st.rerun()
    with col3:
        if st.button("Mark As Personal Leave", width="stretch", disabled=indexs == []):
            for index in indexs:
                st.session_state.student_df.at[index ,"Status"] = "Personal Leave" 
            st.rerun()
    with col4:
        if st.button("Mark As Present", width="stretch", disabled=indexs == []):
            for index in indexs:
                st.session_state.student_df.at[index ,"Status"] = "Present" 
            st.rerun()
            
    with col5:
        if st.button("Submit Record", width="stretch"):
            counter = 0
            for i in st.session_state.student_df.itertuples():
                counter += 1
                new_record = Attendance(
                    student_ssid = i.SSID ,
                    activity_id = st.session_state.current_act_id,
                    session_date = date, 
                    status= i.Status
                )
                db.session.add(new_record)
            db.session.commit()
            st.toast(f"{counter} attendance record of {act_selected.name} at {date}")