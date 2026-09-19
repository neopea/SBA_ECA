import streamlit as st
from database import Student , Activity , StudentActivity ,app , db , Teacher , Notification
import pandas as pd
from datetime import datetime , date
import time
import streamlit as st
import pandas as pd
from sqlalchemy.orm import selectinload
from database import app, db, Activity, StudentActivity, Student, Teacher, Award, Attendance
def send_message(activity_id , student_ssid , teacher_id, title  , category, message):
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

def promote_student(activity_id ,  ssid , role , position ):
    stmt = db.select(StudentActivity).where(StudentActivity.activity_id == activity_id  , StudentActivity.student_ssid == ssid ,StudentActivity.academic_year == current_academic_year)
    link = db.session.execute(stmt).scalars().first()
    link.role = role
    link.position_tier = position
    print(link)
    send_message(activity_id=activity_id
                , student_ssid= ssid , 
                teacher_id=st.session_state.teacher_id ,
                title= f"Promotion of activity {act.name} ",
                category="Activity Update",
                message=f"Promote to position {role} , postion tier: {position}"
                )
    db.session.commit()

def enroll_student(activity_id , ssid , operation : str): #operation = "Accept" / "Reject"
    link = db.session.execute(db.select(StudentActivity).where(StudentActivity.activity_id == activity_id , StudentActivity.student_ssid == ssid , StudentActivity.academic_year == current_academic_year)).scalars().first()
    print(link)
    if operation == "Reject":
        link.status = "Rejected"    
    elif operation == "Accept":
        link.status = "Joined"
        link.role = "Member"
    send_message(
                activity_id=activity_id
                , student_ssid= ssid , 
                teacher_id=st.session_state.teacher_id ,
                title= f"Promotion of activity {act.name}",
                category="Activity Update",
                message=f"Joining of activity {act.name} request approved  "
                )
    
    db.session.commit()
def check_in_time(date : datetime , year : int):
    return datetime(year , 9 , 1) <= date <= datetime(year+1 , 8, 31 )

def display_student(student : Student):
    
    with st.container(border= True):
        check_box_col , student_info_col  ,  view_detail_col = st.columns([1,4,2] , vertical_alignment='center')

        with check_box_col:
            checked = st.checkbox('checkbox' ,label_visibility='collapsed',width=320, key=student.ssid + "checkbox")

        with student_info_col:
            st.markdown(f"__{student.name}__ | Class: {student.class_form} | SSID: {student.ssid}")

        with view_detail_col:
            if st.button("View Details" , key=student.ssid + "button" , width="content"):
                st.session_state.ssid = student.ssid
                st.switch_page("page/Student_display.py")
    return checked


def get_act_data(enrollments_li):
    members = []
    captains = []
    joined_students = []

    enrollment_year = enrollments_li[0].academic_year
    for enrollment in enrollments_li:
        if enrollment.status == "Joined":
            if enrollment.position_tier != "Leader":
                joined_students.append((enrollment.student , enrollment.role , enrollment.position_tier))
            else:
                captains.append([enrollment.student , enrollment.role , enrollment.position_tier])

    captain_df = [{
    "Name": x[0].name,
    "Class" : x[0].class_form ,
    "SSID" : x[0].ssid,
    "Role" : x[1],
    "Tier" : x[2]}
for x in captains]
    if captain_df != []:
        captain_df = pd.DataFrame(captain_df).sort_values(by=["SSID"])
    else:
        captain_df = pd.DataFrame(captain_df)
    member_df = [{
    "Name": x[0].name,
    "SSID" : x[0].ssid,
    "Class" : x[0].class_form ,
    "Role" : x[1],
    "Tier" : x[2]}
for x in joined_students]
    member_df = pd.DataFrame(member_df).sort_values(by=["Tier" , "Role" , "SSID"] , ascending=[True , True , True ])
    display_df = pd.concat([captain_df , member_df])
    if enrollment_year == current_academic_year:
        display_df = display_df.drop(columns="Tier")
    else:
        display_df = display_df.drop(columns=["Tier" , "Class"])

    return  display_df

with app.app_context():
    act = db.session.get(Activity , st.session_state.activity_id)
    total_members = 0
    students = []
    members = []
    teachers = act.teachers_in_charge

    year = datetime.today().year
    if datetime.today() > datetime(datetime.today().year , 9 ,1 ):
        current_academic_year = f"{year}-{year+1}"
    else:
        current_academic_year = f"{year-1}-{year}"

    all_act_data = {} #year : datas 
    interested_student = []
    for i in act.enrollments:
        if i.academic_year == current_academic_year:
            total_members += 1
            if i.status == "Interested":
                interested_student.append(i.student)
            elif i.status == "Joined":
                members.append(i.student)
        if i.academic_year not in all_act_data:
            all_act_data[i.academic_year] = [i]
        else:
            all_act_data[i.academic_year].append(i)







    st.title(f"🏆 {act.name}")
    st.caption(f"Category: {act.category}")


    col1, col2, col3 = st.columns(3)
    col1.metric("Total Members: " , total_members)
    col2.metric("Awards Won: " , len(act.awards_given))

    with col3:
        st.write("Teachers in charge: ")
        for x in teachers:
            st.caption("• " + x.name)


    st.divider()

    tab1 , tab2 , tab3  , tab4 = st.tabs(["Overview" , "Members" , "Awards & Attendance" , "History"])

    with tab1:
        st.info(act.description)


    with tab2:
        
        st.subheader(f"Applications ({len(interested_student)})")
        
        if not interested_student:
            st.info("No pending applications.")

        else:
            with st.container(border=True):
                st.write("Select students to approve")

                display_data = [{
                    "Name": e.name,
                    "Class": e.class_form,
                    "Status": "Interested"
                } for e in interested_student]
            
                df_display = st.dataframe(pd.DataFrame(display_data), 
                                        width="stretch",on_select="rerun" , hide_index=True , selection_mode="multi-row")
                #df_display.selection
                with st.container(horizontal=True):
                    if st.button("✅ Approve Selected", type="primary" , disabled=df_display.selection.rows == []):
                        for index in df_display.selection.rows :
                            enroll_student(ssid=interested_student[index].ssid , activity_id=st.session_state.activity_id , operation="Accept")
                        st.rerun()

                            #print(interested_students[index].ssid)
                    if st.button("❌ Reject Selected", type="primary" , disabled=df_display.selection.rows == []):
                        for index in df_display.selection.rows :
                            enroll_student(ssid=interested_student[index].ssid , activity_id=st.session_state.activity_id , operation="Reject")
                        st.rerun()

        st.divider()

        display_df = get_act_data(all_act_data[current_academic_year])
        st.subheader(f"Enrollment data at {year}  ({len(all_act_data[current_academic_year])} Members)")
        if len(all_act_data[current_academic_year]) == 0:
            st.info(f"No members in {act.name}")
        else:
            df_member_display = st.dataframe(display_df,
                                            width= "stretch" , hide_index=True, 
                                            )
        st.divider()

        st.subheader("Student Promotion")
        members.sort(key=lambda x:x.ssid , reverse=True)
        with st.form("Student Promotio" , clear_on_submit=True):
            student_selected = st.multiselect("Select Students" , options= members , format_func= lambda x : x.name + f" ({x.class_form}  {x.class_number})")
            student_role = st.text_input("Role:")
            student_postion = st.selectbox("Tier" , options=["Leader" , "Committee" , "Member"])
            submit = st.form_submit_button("Promote Members")
        if submit:
            if student_role == "":
                st.warning("The Role cannot be empty")
            else:
                for student in student_selected:
                    promote_student(st.session_state.activity_id , student.ssid , student_role , student_postion)
                st.rerun()
                st.toast(f"{len(student_selected)}  student promoted to {student_role}")

        
    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"Awards ({len(act.awards_given)})")
            if act.awards_given:
                for a in act.awards_given:
                    with st.expander(f"🏅 {a.award_name}"):
                        st.write(a.student_ssid , a.student.name , a.date_awarded)
            else:
                st.info("No awards recorded.")
        
        with col2:
            st.subheader("Attendance Log")
            attendance_dict = {}
            if act.attendance_logs:
                for l in act.attendance_logs:
                    if l.session_date not in attendance_dict:
                        attendance_dict[l.session_date] = [l]
                    else:
                        attendance_dict[l.session_date].append(l)

                for key, value in attendance_dict.items():
                    with st.expander(f"Attendance record on {str(key)[:11]}"):
                        present_logs = [{"Student": x.student.name, "Class" : x.student.class_form , "Status": x.status} for x in value if x.status == "Present"]
                        absent_logs = [{"Student": x.student.name, "Class" : x.student.class_form , "Status": x.status} for x in value if x.status != "Present"]
                        if absent_logs != []:
                            df_non_present = pd.DataFrame(absent_logs).sort_values(by=["Status" , "Class" , "Student"])
                        else:
                            df_non_present = pd.DataFrame()
                        if present_logs != []:
                            df_present = pd.DataFrame(present_logs).sort_values(by=["Class" , "Student"])
                        else:
                            df_present = pd.DataFrame()
                        
                        #order by 1.non present, 2. non-present name 3. class 4. student name 

                        df_logs = pd.concat([df_non_present,df_present] ,sort=False )
                        #lambda x : 1 if x != "Present" else 0
                        st.dataframe(df_logs, width="stretch" , hide_index=True)
            else:
                st.info("No attendance records.")

    with tab4:    
        options = list(all_act_data.keys())
        options.sort(key=lambda x : x[:4])

        result = st.segmented_control("Select Years" , options=options , selection_mode="multi" )
        year_li= result 
        year_li.sort(key=lambda x : x[:4])
        for year in year_li:
            display_df = get_act_data(all_act_data[year])
            st.subheader(f"Enrollment data at {year}  ({len(all_act_data[year])} Members)")
            if len(all_act_data[year]) == 0:
                st.info(f"No members in {act.name}")
            else:
                df_member_display = st.dataframe(display_df,
                                                width= "stretch" , hide_index=True, 
                                                )
            st.divider()