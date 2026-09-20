import streamlit as st
from database import Student , Activity , StudentActivity ,app , db , Teacher
import pandas as pd
import time
from sqlalchemy.orm import selectinload 
from datetime import datetime
current_year = datetime.today().year

def enroll_student(student_ssid, activity_id, activity_name ,academic_year):
    with app.app_context():
        new_acts = StudentActivity(
            student_ssid=student_ssid,
            activity_id=activity_id,
            academic_year = academic_year,
            role="Applicant",
            status="Interested"
        )
        
        db.session.add(new_acts)
        db.session.commit()
        return True, f"{activity_name} joined successfully!"
            
            #db.session.rollback()
            #print(f"Error: {e}")
            #return False, "Database error during join."
        

def display_act(acts: Activity):
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

        join_button = st.button("Join Now", key=acts.activity_id)

            

        existing = db.session.execute(db.select(StudentActivity).where(StudentActivity.student_ssid == st.session_state.ssid , StudentActivity.activity_id == acts.activity_id , StudentActivity.academic_year == f"{current_year}-{current_year+1}")).scalars().all()
        if join_button:
            if existing:
                existing = existing[0]
                if existing.status == "Joined":
                    title = "Activity already joined"
                    s = f"You are already a member of {acts.name}"
                elif existing.status == "Interested":
                    title ="Activity already added to interested"
                    s = f"Request of {acts.name} already sent "
                else:
                    title = "Request of the activity is already rejected"
                    s = f"Please find the teachers in charge of {acts.name} for more information"

                @st.dialog(title)
                def warning():
                    st.warning(s)
                warning()
            else:
                @st.dialog("Confirm submition")
                def confirm_submit(text : str , success_msg : str):
                    st.write(text)
                    col1 , col2 = st.columns(2)
                    with col1:
                        Yes_button = st.button("Yes" , width = 'stretch')
                    with col2:
                        No_button =  st.button("No" , width = 'stretch')
                    if Yes_button:
                        #try:
                        enroll_student(student_ssid=st.session_state.ssid,
                                        activity_id=acts.activity_id,
                                        activity_name=acts.name,
                                        academic_year = f"{current_year}-{current_year+1}"
                                        )
                        st.success(f"Activity {acts.name} request sent")
                        #except:
                        #    st.warning(f"{acts.name} already joined")
                        #finally:
                        #    time.sleep(0.5)
                        #    st.rerun()
                    if No_button:
                        time.sleep(0.5)
                        st.rerun()
                confirm_submit("Join acts?" , "Acts joined")



def viewacts():
    #eager load the datas 
    base_stmt = db.select(Activity).options(
    selectinload(Activity.teachers_in_charge),
    selectinload(Activity.enrollments).selectinload(StudentActivity.student)
    )
    with app.app_context():
        categories = db.session.execute(db.select(Activity.category).distinct().order_by(Activity.category)).scalars().all()
        teachers = db.session.execute(db.select(Teacher).order_by(Teacher.name)).scalars().all()
    
    #result = c.search("PRAGMA table_info(activity);")
    #li = c.search("select * from activity")
    st.title("ACTIVITIES")
    st.write("Search activity")
    #add direct search by name.
    #query = 'select name, categories, Teachers, captain, requirements from activity '
    #data = pd.read_sql(query , c.conn) #turns to df 
    #select the categories , and the options to search for things

    activities = db.session.execute(db.select(Activity)).scalars().all()
    display_activities = activities
    col1 , col2 = st.columns(2)
    with col1:
        filter = st.selectbox(label="select filter by:" , options=['name' , 'category' , 'teachers in charge'] , key="filter1")

    with col2:
        if filter == "name":
            x = "A-Z" , "Z-A"
        elif filter == "category":
            x = db.session.execute(db.select(getattr(Activity , filter)).distinct().order_by(Activity.category)).scalars().all()
            print(x)
        else:
            x = Teacher.query.order_by(Teacher.name).all()
        sort_by = st.selectbox(label="select filter" , options=x , key="sort_by1")


    final_stmt = base_stmt


    if filter == "name":
        if sort_by == 'A-Z':
            final_stmt = final_stmt.order_by(Activity.name)
        else:
            final_stmt = final_stmt.order_by(Activity.name.desc())

    elif filter == 'teachers in charge':
        selected_teacher = sort_by
        if selected_teacher:
            teacher_id = selected_teacher.teacher_id 
            final_stmt = final_stmt.join(Activity.teachers_in_charge).where(Teacher.teacher_id == teacher_id).order_by(Activity.name)


    elif filter == "category":
        final_stmt = final_stmt.where(Activity.category == sort_by).order_by(Activity.name)

    display_activities = db.session.execute(final_stmt).scalars().all()

    for i in display_activities:
        display_act(i)


with app.app_context():
    student = db.session.get(Student , st.session_state.ssid)
    viewacts()