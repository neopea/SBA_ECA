import streamlit as st
from database import db , app , Teacher , Activity
from datetime import datetime
current_year = datetime.today().year

def display_act(acts):
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


st.title("Activities in charge")

#activity = st.session_state.info[4].split(",")
#result = []
#for i in range(len(activity)):
#    result.append(c.search(f"select * from activity where name = '{activity[i].strip()}' ")[0])





with app.app_context():
    teacher = db.session.get(Teacher, st.session_state.teacher_id)
    acts = teacher.activities_in_charge
    for i in acts:
        display_act(i)

    if st.button("Create new activity"):
        st.switch_page("page/createActivity.py")

