# Extracurricular Activity Manager (ECA)

An information system for secondary schools to track students' non-academic growth and achievements, and to help teachers identify students with high potential for special programs. The system is supervised by teachers, and students register for the activities they wish to join.

---

## Features

### Student Features

- **Role-based login** with hashed passwords
- **Student Dashboard** showing joined activities, awards won, skills listed, and total attendance
- **Year filter** to view records for specific academic years (useful for SLP and OEA submissions)
- **Activities tab** showing joined, interested, and rejected activities
- **Skills tab** to view, add, and remove personal skills
- **Awards tab** to view and upload awards with date picker and category selection
- **Attendance tab** showing full attendance log for all activities
- **Activity enrollment** with confirmation dialogs and duplicate detection
- **Inbox** to receive and read messages from teachers

### Teacher Features

- **Role-based login** with separate navigation bar
- **My Activity** showing all activities the teacher is in charge of
- **Activity Information** page with Overview, Members, Awards & Attendance, and History tabs
- **Approve or reject** student enrollment applications
- **Promote students** to custom roles and position tiers
- **Create new activities** with name, category, teachers in charge, and description
- **Take attendance** with colour-coded statuses (Present, Absent, Sick Leave, Personal Leave)
- **Search students** by name, class, skills, or participation rate
- **Add to Highlights** for quick access to frequently viewed students or activities
- **Send messages** to individual or multiple students
- **Analytics** page with bar charts and Excel export
- **Smart Student Selector** using Sentence Transformer embeddings to identify high-potential students by natural language query

---


## Project Structure

```
sba_eca/
├── app.py                  
├── database.py           
├── requirements.txt       
├── runtime.txt      
├── instance/
    ├── school1.db             
└── page/
    ├── Settings.py
    ├── ChangePassword.py
    ├── Student_display.py
    ├── Student_Viewacts.py
    ├── Student_Skills.py
    ├── Student_Awards.py
    ├── Student_Inbox.py
    ├── Student_Report.py
    ├── myacts.py
    ├── createActivity.py
    ├── Teacher_activityinfo.py
    ├── Teacher_searching.py
    ├── Teacher_smartsearch.py
    ├── Teacher_attendance.py
    ├── Teacher_highlights.py
    ├── Teacher_message.py
    └── Teacher_info.py
```

---

## Installation

### Prerequisites

- Python 3.11
- pip
- A modern web browser

### Steps



1. Run the app:

```bash
streamlit run app.py
```

2. Open the app in your browser at `http://localhost:8501`.

or 

1. Visit Streamlit Community Cloud at 'https://sbaeca-demo.streamlit.app'



---

## Author

**Li Shing Cheung Neo**
Class 6C, No. 16
Carmel Pak U Secondary School
HKDSE Information and Communication Technology
School-Based Assessment 2025–2026

---

## License

This project is submitted as part of the HKDSE ICT School-Based Assessment. It is intended for educational purposes only.