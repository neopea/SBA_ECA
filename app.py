import streamlit as st
from database import Student , Teacher , app , db
import time
from page.Teacher_smartsearch import get_model
if "login" not in st.session_state:
    st.session_state.login = False


def login():    
    st.title("login")
    if st.session_state.login == False:
        username = st.text_input("username")
        password = st.text_input("password" , type = "password")
        submit = st.button("Login ")

        if submit:
            student = db.session.get(Student , username)
            teacher =  db.session.get(Teacher , username)
            if student == None and teacher == None:
                st.warning("Invalid username")
            else:
                if len(username) == 8 and student.check_password(password ): #s2021XXX
                    st.session_state.identity = 'student'
                    st.session_state.login = True
                    st.session_state.ssid = username
                    st.success(f"login successful as {student.ssid}")
                    time.sleep(0.65)
                    st.rerun()

                elif len(username) == 2 and teacher.check_password(password): # teacher KT
                    st.session_state.identity = 'teacher'
                    st.session_state.login = True
                    st.success(f"login successful as {teacher.teacher_id}")
                    st.session_state.teacher_id = username
                    time.sleep(0.65)
                    st.rerun()
                    #jump to main function
                    
                else:
                    st.warning("Invalid password")

    else:
        st.info(f"You log in already as {st.session_state.identity}")
        

with app.app_context():
    if st.session_state.login:
        if st.session_state.identity == "teacher":
            teacher_pages = {
            "OVERVIEW": [
                st.Page("page/myacts.py", title="My Activity", icon="📋", default=True),
                st.Page("page/Teacher_highlights.py", title="Highlights", icon="📌"),
            ],
            "WORKSPACE": [
                st.Page("page/Teacher_attendance.py",  title="Attendance" , icon="🗓️"),
                st.Page("page/Teacher_searching.py", title="Search", icon="🔍"),
                st.Page("page/Teacher_smartsearch.py" , title = "Smart Selector" , icon = "📇"),
                st.Page("page/Teacher_message.py", title="Messages", icon="📨"),
            ],
            "REPORTS": [
                st.Page("page/Teacher_info.py", title="Analytics", icon="📊"),
            ],
            "ACCOUNT": [
                st.Page("page/Settings.py", title="Settings.py", icon="⚙️"),
            ],
            "Hidden" : [
                st.Page("page/Teacher_activityinfo.py" , visibility="hidden"),
                st.Page("page/Student_display.py" , visibility="hidden"),
                st.Page("page/ChangePassword.py" , visibility="hidden"),
                st.Page("page/createActivity.py" ,visibility="hidden"),

            ]
        }
            pg = st.navigation(teacher_pages)
        else:
            student_pages = {
                "OVERVIEW" : [
                    st.Page("page/Student_display.py" , title="Student Dashboard" , icon = "🎯" , default=True)
                ],
                "UTILITY" : [
                    st.Page("page/Student_Viewacts.py" , title="Activity" , icon = "🎨"),
                    st.Page("page/Student_Awards.py" , title="Awards" , icon = "🏅"),
                    st.Page("page/Student_Inbox.py" , title = "Inbox" , icon ="📨"),
                    st.Page("page/Student_Report.py" , title="Report" , icon="📝"),
                    st.Page("page/Student_Skills.py" , title="Skill", icon= "🛠️")
                ],
                "ACCOUNT" : [
                    st.Page("page/Settings.py", title="Settings.py", icon="⚙️")
                ],
                "HIDDEN" : [
                    st.Page("page/ChangePassword.py" , visibility="hidden")
                ]
                }
            pg = st.navigation(student_pages)
        pg.run()

    else:
        login()


