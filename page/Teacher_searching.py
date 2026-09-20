import streamlit as st
from sqlalchemy import or_, desc, asc
from sqlalchemy.orm import selectinload
from database import Student, Activity, Attendance , Skill, Teacher, app, db , TeacherHighlight
from page.Student_display import current_year
if "student_selected" not in st.session_state:
    st.session_state.student_selected = {}
if "activity_selected" not in st.session_state:    
    st.session_state.activity_selected = {}


def add_highlights(values,  identity): #see if already added
    with app.app_context():
        if identity == "student":
            new_highlight = TeacherHighlight(teacher_id = st.session_state.teacher_id , student_ssid = values)
        else:
            new_highlight = TeacherHighlight(teacher_id = st.session_state.teacher_id , activity_id = values)
        db.session.add(new_highlight)
        db.session.commit()

def get_participation_rate(student):
    records = student.attendance_records
    if not records:
        return 0.0
    counter = 0
    for record in records:
        if record.status == "Present":
            counter += 1
    return (counter / len(records)) * 100

def change_checkbox(ssid, student : Student):
    if st.session_state[f"{ssid}checkbox"]:
        st.session_state.student_selected[ssid] = student
    else:
        del st.session_state.student_selected[ssid]

def change_teacher_checkbox(activity_id , activity):
    if st.session_state[f"{activity_id}checkbox"]:
        st.session_state.activity_selected[activity_id] = activity
    else:
        del st.session_state.activity_selected[activity_id]

def display_student(student : Student):
    with st.container(border= True):
        check_box_col , student_info_col  ,  view_detail_col = st.columns([1,7,2] , vertical_alignment='center')

        with check_box_col:
            st.checkbox('checkbox' ,  label_visibility='collapsed',width=320, key=student.ssid + "checkbox" , on_change=change_checkbox , args=(student.ssid , student) , persist_state="session")
        with student_info_col:
            with st.container(gap=0):
                st.markdown(f"__{student.name}__ ")
                st.markdown(f"Class: {student.class_form} | SSID: {student.ssid}")

        with view_detail_col:
            if st.button("View Details" , key=student.ssid + "button" , width="content"):
                st.session_state.ssid = student.ssid
                st.switch_page("page/Student_display.py")


def display_act(acts):
    with st.container(horizontal=True , vertical_alignment="center"):
        st.checkbox(label="activity" , label_visibility="collapsed" , key=f"{acts.activity_id}checkbox" , on_change=change_teacher_checkbox , args=(acts.activity_id , acts) , persist_state="session")
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



if __name__ == "__main__":
    with app.app_context():
        col1, col2, col3 = st.columns(3)

        search_text = st.text_input("Search by name/SSID")
        with col1:
            table_filter = st.selectbox(label="Select filter by:", options=["Students", "Activity"])

        if table_filter == "Students":
            stmt = db.select(Student)

            filter_options = ["Name", "Class", "Skills", "Participation Rate"]
        else:
            stmt = db.select(Activity)
            filter_options = ["Name", "Category", "Teachers"]

        with col2:
            criteria = st.selectbox(label="Filter by", options=filter_options)

        with col3:
            participation_sort = None
            if table_filter == "Students":
                if criteria == "Participation Rate":
                    sort_order = st.selectbox("Order", options=["High to Low", "Low to High"])
                    participation_sort = sort_order


                elif criteria == "Skills":
                    all_skills = db.session.execute(db.select(Skill.skill_name)).scalars().all()
                    skill_select = st.selectbox("Select Skill", options=all_skills)
                    stmt = stmt.where(Skill.skill_name == skill_select)

                elif criteria == "Class":
                    all_class = db.session.execute(db.select(Student.class_form).order_by(Student.class_form)).unique().scalars().all()
                    class_select = st.selectbox("Select Class", options=all_class)
                    stmt = stmt.where(Student.class_form == class_select)

                elif criteria == "Name":
                    sort_order = st.selectbox("Sort", options=["A-Z", "Z-A"])
                    if sort_order == "A-Z":
                        stmt = stmt.order_by(Student.name.asc())
                    else:
                        stmt = stmt.order_by(Student.name.desc())

            else: # Activity
                if criteria == "Name":
                    sort_order = st.selectbox("Sort", options=["A-Z", "Z-A"])
                    if sort_order == "A-Z":
                        stmt = stmt.order_by(Activity.name.asc())
                    else:
                        stmt = stmt.order_by(Activity.name.desc())
                
                elif criteria == "Category":
                    cats = db.session.execute(db.select(Activity.category).distinct()).scalars().all()
                    cat_select = st.selectbox("Select Category", options=cats)
                    stmt = stmt.where(Activity.category == cat_select)

                elif criteria == "Teachers":
                    teachers = db.session.execute(db.select(Teacher.name).order_by(Teacher.name)).scalars().all()
                    teach_select = st.selectbox("Select Teacher", options=teachers)
                    stmt = stmt.join(Activity.teachers_in_charge).where(Teacher.name == teach_select)


        if search_text:
            if table_filter == "Students":
                stmt = stmt.where((Student.name.ilike(f"%{search_text}%")) | (Student.ssid.ilike(f"%{search_text}%")))
            else:
                stmt = stmt.where(Activity.name.ilike(f"%{search_text}%")) 

        cola ,  colc = st.columns(2)
        with cola:
            if st.button("Add to highlight" , width = 'stretch'):
                counter = 0
                if table_filter == "Students":
                    highlighted = db.session.execute(db.select(TeacherHighlight.student_ssid).where(TeacherHighlight.teacher_id == st.session_state.teacher_id)).scalars().all()
                    for keys , values in st.session_state.student_selected.items():
                        if st.session_state.student_selected[keys]:
                            if keys in highlighted:
                                st.toast(f":yellow-background[Student {keys} already highlighted]" , icon="🚨")
                            else:
                                add_highlights(keys , "student")
                                counter += 1
                            st.session_state[f"{keys}checkbox"] = False              
                            st.session_state.student_selected[keys] = False
                    if counter:
                        st.toast(f":green-background[{counter} student is successfully highlighted]" , icon="🔔")
                else:
                    highlighted = db.session.execute(db.select(TeacherHighlight.activity_id).where(TeacherHighlight.teacher_id == st.session_state.teacher_id)).scalars().all()
                    for keys , values in st.session_state.activity_selected.items():
                        if st.session_state.activity_selected[keys]:
                            if keys in highlighted:
                                st.toast(f":yellow-background[Activity {values.name} already highlighted]" , icon="🚨")
                            else:
                                add_highlights(keys , "activity")
                                counter += 1
                            st.session_state[f"{keys}checkbox"] = False              
                            st.session_state.activity_selected[keys] = False
                    if counter:
                        st.toast(f":green-background[{counter} activity is successfully highlighted]" , icon="🔔")                    


        with colc:
            if st.button("Send message" , disabled=table_filter!= "Students" , width = 'stretch' ):
                st.session_state.message_from_searching = True
                st.switch_page("page/Teacher_message.py")



        if table_filter == "Students" and criteria == "Participation Rate":
            results = db.session.execute(stmt).scalars().all()
            for i in results:
                print(get_participation_rate(i))
            if participation_sort == "High to Low":
                results = sorted(results, key=get_participation_rate, reverse=True)
            else:
                results = sorted(results, key=get_participation_rate)

            print("SORTED RATES:", [f"{s.name}: {get_participation_rate(s)}%" for s in results])
            
            results = results[:50]
            
        else:
            final_stmt = stmt.limit(50)
            results = db.session.execute(final_stmt).scalars().all()


        colx , coly = st.columns([2,1.3])

        if not results:
            st.markdown("NO ITEMS FOUND")
        else:
            if table_filter == "Students":
                with coly:
                    with st.container(border=True):
                        st.markdown(f'<p style="font-size:24px;">Students Selected</p>', unsafe_allow_html=True , text_alignment="center" , width="stretch")
                        for keys , values in st.session_state.student_selected.items():
                            if values:
                                with st.container(horizontal=True , gap=20 , vertical_alignment="center"):
                                    st.write(keys)
                                    if st.button("⛌" , type="tertiary" , key=f"{keys}"):
                                        st.session_state.student_selected[keys] = False
                                        st.session_state[f"{keys}checkbox"] = False
                                        st.rerun()
                with colx:
                    for stu in results:
                        display_student(stu)



            else:
                for act in results:
                    display_act(act)

