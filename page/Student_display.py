import streamlit as st
from database import Student , db , app ,Skill
import pandas as pd 
from datetime import datetime
st.session_state.editing = False



st.session_state.show_stats = True
student = db.session.get(Student , st.session_state.ssid)

current_year = datetime.today().year
new_sku_year = datetime(current_year , 9,  1, 0)

def check_in_time(date : datetime , year : int):
    return datetime(year , 9 , 1) <= date <= datetime(year+1 , 8, 31 )

def get_student_data(time_li):

    joined_activities = []
    rejected_activities = []
    interested_activities = []

    for enrollment in student.enrollments:
        act_year = int(enrollment.academic_year[:4])
        in_range = (act_year in time_li)
        if not in_range:
            continue
        activity_info = {
            "Activity": enrollment.activity.name,
            "Category": enrollment.activity.category,
            "Role": enrollment.role,
            "Academic Year" : enrollment.academic_year
        }
        if enrollment.status == 'Joined':
            joined_activities.append(activity_info)
        elif enrollment.status == "Rejected":
            rejected_activities.append(activity_info)
        else:
            interested_activities.append(activity_info)

    skills_list = [skill.skill_name for skill in student.skills]


    awards_data = []
    for award in student.awards_received:
        in_range = False
        for year in time_li:
            if check_in_time(award.date_awarded , year):
                in_range = True
                break
        if not in_range:
            continue
        awards_data.append({
            "Award": award.award_name,
            "Date": award.date_awarded,
            "From Activity": award.activity.name if award.activity else ""
        })
    

    attendance_data = []
    for record in student.attendance_records:
        in_range = False
        for year in time_li:
            if check_in_time(record.session_date , year):
                in_range = True
                break
        if not in_range:
            continue
        attendance_data.append({
        "Date": record.session_date,
        "Activity": record.activity.name,
        "Status": record.status
    })



    return {
            "skills": skills_list,
            "awards_df": pd.DataFrame(awards_data),
            "joined_activities_df": pd.DataFrame(joined_activities),
            "rejected_activities_df" : pd.DataFrame(rejected_activities),
            "interested_activities_df": pd.DataFrame(interested_activities),
            "attendance_df": pd.DataFrame(attendance_data)
        }
    


def student_display():

    if "time_li" not in st.session_state:
        data = get_student_data([current_year])
    else:
        data = get_student_data(st.session_state.time_li)
    st.title("🎓 MY INFORMATION")
    st.header(f"{student.name} ({student.ssid})")
    st.caption(f"Email: {student.ssid}@school.edu.hk | Class: {student.class_form} | Age: {student.age} ({student.sex})")

    col1 , col2 , col3 , col4 = st.columns(4)
    col1.metric("Joined Activities", len(data['joined_activities_df']))
    col2.metric("Awards Won", len(data['awards_df']))
    col3.metric("Skills Listed", len(data['skills']))

    # Calculate attendance
    total_sessions = len(data['attendance_df'])
    if data["attendance_df"].empty:
        present_sessions  = 0 
    else:
        present_sessions = len(data['attendance_df'][data['attendance_df']['Status'] == 'Present'])
    col4.metric("Total Attendance", f"{present_sessions} / {total_sessions}")



    init_year = int(student.ssid[1:5])
    options = [x for x in range(init_year , current_year + 1)]
    result = st.segmented_control("Select Years" , options=options , selection_mode="multi" ,
                                    format_func= lambda i :f"{i}-{i+1}" , key="time_li")



#    col1 , col2 ,col3 = st.columns(3)
#    student.name
#    with col1:
#        st.write(f'SSID: {student.ssid}')
#    with col2:
#        st.write(f'Age {student.age}')
#    with col3:
#        st.write(f'Age {student.sex}')




    #view joined acts

    tab1, tab2, tab3, tab4 = st.tabs(["Activities", "Skills", "Awards", "Attendance"])

    with tab1:
        st.subheader("Joined Activities")
        if data['joined_activities_df'].empty:
            st.info("Not currently joined in any activities.")
        else:
            st.dataframe(data['joined_activities_df'], width = "stretch" , hide_index=True)
        
        st.subheader("Interested Activities")
        if data['interested_activities_df'].empty:
            st.info("No activities marked as 'Interested'.") 
        else:
            st.dataframe(data['interested_activities_df'], width = "stretch" , hide_index=True)
        if st.session_state.identity == "student":
            if st.button("add interested activities"):  
                st.switch_page("page/Student_Viewacts.py")
        st.subheader("Rejected Activities")
        if data["rejected_activities_df"].empty:
            st.info("No result ")
        else:
            df = data["rejected_activities_df"]
            df= df[["Activity" , "Category" , "Academic Year"]]
            df["Status"] = "Rejected"
            st.dataframe(df , width="stretch" , hide_index=True)






    with tab2:
        st.subheader("Registered Skills")
        if not data['skills']:
            st.info("No skills listed for this student.")
        else:
            st.write(" ") # Add a little space
            for skill in data['skills']:
                st.write(skill)
        if st.session_state.identity == "student":
            if st.button("amend skills"):
                st.switch_page("page/Student_Skills.py")
    
    with tab3:
        st.subheader("Awards and Achievements")
        if data['awards_df'].empty:
            st.info("No awards on record.")
        else:
            st.dataframe(data['awards_df'], width = "stretch")
        if st.session_state.identity == "student":
            if st.button("upload awards"):
                st.switch_page("page/Student_Awards.py")
    with tab4:
        st.subheader("Full Attendance Log")
        if data['attendance_df'].empty:
            st.info("No attendance records found.")
        else:
            st.dataframe(data['attendance_df'], width = "stretch")
    
    st.divider()


with app.app_context():
    student_display()