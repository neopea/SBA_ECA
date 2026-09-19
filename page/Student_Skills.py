import streamlit as st
from database import Student , Activity , StudentActivity ,app , db , Teacher , Skill
import pandas as pd
import time
from sqlalchemy.orm import selectinload 


def add_skills(skills):
    with app.app_context():
        student = db.session.get(Student , st.session_state.ssid)
        for i in skills:
            student.skills.append(skill_dict[i])
            db.session.commit()

def del_skills(skills):
    with app.app_context():
        student = db.session.get(Student , st.session_state.ssid)

        targets = [
            s for s in student.skills 
            if s.skill_name in skills 
        ]

        for target_skill in targets:
            student.skills.remove(target_skill)
            
        db.session.commit()
        
st.session_state.selected = []
with app.app_context():
    student = db.session.get(Student , st.session_state.ssid)
    present_skills = student.skills

    st.title("Update Skills")
    col1 , col2 = st.columns(2)



    all_skills = Skill.query.order_by(Skill.skill_name).all()
    skill_dict = {skill.skill_name: skill for skill in all_skills}

    options = [x.skill_name for x in all_skills if x not in present_skills ]
    with col1:
        st.subheader("Add Skills")

        selected_skills = st.multiselect(label="Select new skills to add" , options=options)
        if st.button("Add skills" , disabled=selected_skills == []):
            if not selected_skills:
                st.warning("please select skills to add")
            else:
                @st.dialog("Confirm add")
                def confirm_add():
                    st.write(f"Confirm add skills {' , '.join(selected_skills)}")
                    col1 , col2 = st.columns(2)
                    with col1:
                        Yes_button = st.button("Yes" , width = 'stretch')

                    with col2:
                        No_button =  st.button("No" , width = 'stretch')
                    if Yes_button:
                        add_skills(selected_skills)
                        st.success(f"Skills added : {", ".join(selected_skills)}")
                        time.sleep(0.75)
                        st.rerun()
                    if No_button:
                        st.rerun()
                confirm_add()





    with col2:
        st.subheader("Delete Skills")
        for i in present_skills:
            with st.container(horizontal=True):
                if st.checkbox(label = i.skill_name , key = i):
                    st.session_state.selected.append(i.skill_name)


                    
        if st.button("Delete" , disabled=st.session_state.selected == []):
            @st.dialog("Confirm delete")
            def confirm_del():
                st.write(f"Confirm delete skills {', '.join(st.session_state.selected)}")
                col1 , col2 = st.columns(2)
                with col1:
                    Yes_button = st.button("Yes" , width = 'stretch')

                with col2:
                    No_button =  st.button("No" , width = 'stretch')

                if Yes_button:
                    del_skills(st.session_state.selected)
                    st.success(f"Skills deleted : {", ".join(st.session_state.selected)}")
                    time.sleep(0.75)
                    st.rerun()
                if No_button:
                    st.rerun()
                
            confirm_del()