import streamlit as st
import pandas as pd
from sqlalchemy.orm import selectinload
from database import app, db, Student, Activity, StudentActivity, Award, Attendance
from io import BytesIO

st.set_page_config(layout="wide", page_title="Reports & Analysis")
st.title("Chart")

def get_attendance(student:Student):
    counter = 0
    if student.attendance_records == []:
        return 0
    for i in student.attendance_records:
        if i.status == "Present":
            counter += 1
    
    return counter / len(student.attendance_records) * 100

def get_act_num(student:Student):
    counter = 0
    for i in student.enrollments:
        if i.status == "Joined":
            counter += 1
    return counter

def plot_graph(df , x_col  ,x_label , y_col , y_label):
    color_li = ["#264CB5" , "#18D615" , "#E1E67B" ,"#D21969" ,"#F3CC1E"] #5 colors
    #if len(y_col) == 1:
    st.bar_chart(df , x=x_col , x_label=x_label ,y=y_col , y_label=y_label , sort=False ,color="#264CB5")
    # else:
    #     st.line_chart(df , x=x_col ,y=y_col , x_label=x_label ,y_label=y_label  )


with app.app_context():

    all_class = db.session.execute(db.select(Student.class_form).distinct()).scalars().all()
    all_class.sort()
    col1 , col2 , col3 = st.columns(3)

    with col1:
        x_axis = st.selectbox(label="X axis" , options=["Student" , "Activity"])

    with col2:
        if x_axis == "Student":
            filter_options = ["All" , "by class" , "by form"]            
        else:
            filter_options = ['All' ,
                'Academic & STEM', 'Arts & Performance', 'Sports & Athletics', 
                'Service & Leadership', 'Media & Communications', 'Culture & Hobbies'
            ]
        x_filter = st.selectbox(label="filters" , options=filter_options)
        if x_filter == "by class":
            class_filter = st.selectbox(label="Class" , options=all_class)


    with col3:
        if x_axis != "Activity":
            y_axis_options = ["Attendance Rate (%)", "Skill Registered" , "Activities Joined" , "Awards Won"]
        else:
            y_axis_options = ["Attendance Rate (%)" , "Members" , "Awards Given"]

        y_axis = st.selectbox(label="Y axis" , options=y_axis_options)




    st.subheader(f"📈 {y_axis} vs {x_axis}")
    if x_axis == "Student":
        all_students = db.session.execute(db.select(Student)).scalars().all()
        student_df = [{
            "SSID" : i.ssid,
            "Name" : i.name,
            "Class" : i.class_form,
            "Attendance Rate (%)" : get_attendance(i),
            "Awards Won" : len(i.awards_received) ,
            "Skill Registered" : len(i.skills),
            "Activities Joined" : get_act_num(i)
            
        } for i in all_students]
        student_df = pd.DataFrame(student_df).sort_values(by=y_axis , ascending=False)
        #st.dataframe(student_df)
        if x_filter == "by class":
            student_df = student_df[student_df["Class"] == class_filter]
        display_df = student_df
        plot_graph(student_df , "SSID" , "Student" , y_axis , "Values")
    else:

        all_acts = db.session.execute(db.select(Activity)).scalars().all()
        act_df = []

        for act in all_acts:

            member_number = 0
            for i in act.enrollments:
                if i.status == "Joined":
                    member_number += 1
            counter = 0
            for i in act.attendance_logs:
                if i.status == "Present":
                    counter += 1
            attendance = counter / len(act.attendance_logs) * 100

            act_df.append({
                "Name": act.name,
                "Category" : act.category,
                "Members" : member_number,
                "Awards Given" : len(act.awards_given),
                "Attendance Rate (%)" : attendance
            })
        act_df = pd.DataFrame(act_df).sort_values(by=y_axis, ascending=False)
        if x_filter == "All":
            pass
        else:
            act_df = act_df[act_df["Category"] == x_filter]

        display_df = act_df
        plot_graph(act_df , "Name" , "Activities" , y_axis , "Values")


    output = BytesIO()
    with pd.ExcelWriter(output , engine="xlsxwriter") as writer:
        display_df.to_excel(writer , index=False , sheet_name="Sheet 1")
    excel = output.getvalue()
        


    if st.download_button("Export data as excel (.xlsx) file" , data=excel , file_name="sheet1.xlsx", icon=":material/download:"):
        st.toast("File downloaded")
        
        
