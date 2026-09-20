import streamlit as st
import pandas as pd
from sqlalchemy.orm import selectinload
from database import app, db, Student, Activity, StudentActivity, Award, Attendance, Teacher , TeacherHighlight
import time
from page.Student_display import current_year
st.set_page_config(layout="wide")
def display_student(student : Student):
    with st.container(border= True):
        check_box_col , student_info_col  ,  view_detail_col = st.columns([1,7,2] , vertical_alignment='center')

        with check_box_col:
            check = st.checkbox('checkbox' ,  label_visibility='collapsed',width=320, key=student.ssid + "checkbox" )
        with student_info_col:
            with st.container(gap=0):
                st.markdown(f"__{student.name}__ ")
                st.markdown(f"Class: {student.class_form} | SSID: {student.ssid}")

        with view_detail_col:
            if st.button("View Details" , key=student.ssid + "button" , width="content"):
                st.session_state.ssid = student.ssid
                st.switch_page("page/Student_display.py")

    return check

def display_act(acts):
    with st.container(horizontal=True , vertical_alignment="center"):
        check = st.checkbox(label="activity" , label_visibility="collapsed" , key=f"{acts.activity_id}checkbox")
        st.markdown(f'<p style="font-size:24px;">{acts.name}</p>', unsafe_allow_html=True)
    with st.container(border=True):
        teachers = [x.name for x in acts.teachers_in_charge]
        captain = ''
        for enroll in acts.enrollments:
            if (enroll.activity_id == acts.activity_id
                and enroll.position_tier == "Leader"
                and int(enroll.academic_year[:4]) == current_year):
                captain += enroll.student.class_form + ' ' + enroll.student.name + " | "

        captain_display = captain if captain else "--no captain--"

        st.markdown(f"""
                | Field | Value |
                |---|---|
                | Category | {acts.category} |
                | Responsive Teachers | {', '.join(teachers)} |
                | Captain | {captain_display} |
                | Description | {acts.description} |
                """)
        view_detail = st.button("View details" , key=acts.activity_id)


    

    if view_detail:
        st.session_state.activity_id = acts.activity_id
        st.switch_page("page/Teacher_activityinfo.py")

    return check
    

with app.app_context():
    teacher =  db.session.get(Teacher , st.session_state.teacher_id)
    tab1 , tab2 =  st.tabs(['STUDENTS' , 'ACTIVITIES'])




    with tab1:
        student_check_dict = {}
        for highlight in teacher.highlights:
            ssid = highlight.student_ssid
            if ssid != None:
                x = db.session.get(Student , ssid)
                student_check_dict[ssid] = display_student(x)
        
        if st.button("Remove Highlight" , key="student_remove" , disabled=True not in student_check_dict.values()):
            counter = 0
            for key , value in student_check_dict.items():
                if value: 
                    stmt = db.select(TeacherHighlight).where(TeacherHighlight.student_ssid == key , 
                                                            TeacherHighlight.teacher_id == st.session_state.teacher_id)
                    highlight = db.session.execute(stmt).scalars().first()
                    db.session.delete(highlight)
                    counter += 1
            db.session.commit()
            st.success(f"Removed {counter} Student(s) from highlight")
            time.sleep(20.65)
            st.rerun()



    with tab2:
        check_dict = {}
        for highlight in teacher.highlights:
            id = highlight.activity_id
            if id != None:
                x = db.session.get(Activity , id)
                check_dict[id] = display_act(x)

        if st.button("Remove Highlight" , key="act_remove"):
            counter = 0
            for key , value in check_dict.items():
                if value: 
                    stmt = db.select(TeacherHighlight).where(TeacherHighlight.activity_id == key , TeacherHighlight.teacher_id == st.session_state.teacher_id)
                    highlight = db.session.execute(stmt).scalars().first()
                    db.session.delete(highlight)
                    counter += 1
            db.session.commit()
            st.success(f"Removed {counter} Student(s) from highlight")
            time.sleep(0.65)
            st.rerun()