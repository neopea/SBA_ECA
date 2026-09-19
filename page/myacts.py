import streamlit as st
from database import db , app , Teacher , Activity
def display_act(acts):
    with st.container(horizontal=True , vertical_alignment="center"):
        st.markdown(f'<p style="font-size:24px;">{acts.name}</p>', unsafe_allow_html=True)

    with st.container(border=True , horizontal=True):
        with st.container(width= 250):
            st.write("Categories: ")
            st.write("Responsive Teachers:")
            st.write("Captain: ")
            st.write("Description: ")
            view_detail = st.button("View details" , key=acts.activity_id)


        with st.container():
            st.write(acts.category)
            teachers = [x.name for x in acts.teachers_in_charge]
            st.write(' , '.join(teachers))
            captain = []
            for enroll in acts.enrollments:
                if enroll.activity_id == acts.activity_id and enroll.position_tier == "Leader":
                    captain.append(enroll.student.class_form + ' ' + enroll.student.name)
            
            if captain == '':
                st.write("--no captain--")
            else:
                st.write(" , ".join(captain))

            st.write(acts.description)

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

