import streamlit as st
from database import Student , Activity , StudentActivity ,app , db , Teacher , Award
import pandas as pd
import time
from sqlalchemy.orm import selectinload 
from page.Teacher_smartsearch import get_model


def add_awards(name , date , acts , category ,level , rank):
    with app.app_context():
        new_award = Award(student_ssid =st.session_state.ssid,
                        activity_id = acts.activity_id if acts != "None" else None ,
                        award_name =name,
                        category= category,
                        date_awarded =date,
                        rank=rank, 
                        level=level)
        tensor = model.encode(name)
        new_award.set_embeddings(tensor)
        db.session.add(new_award)
        db.session.commit()


with app.app_context():
    acts = db.session.execute(db.select(Activity).order_by(Activity.name)).scalars().all()
    print(acts)
    options = ["None"] + acts 
    st.title("Add Awards")
    model = get_model()

    name = st.text_input("Award name:")
    date = st.date_input("Awarded date")
    acts = st.selectbox("Related activities (Can be None)" , options=options , format_func=lambda x: x.name if x != "None" else "None")
    category = st.selectbox("Category" , options=['Academic & STEM', 'Arts & Performance', 'Sports & Athletics', 
            'Service & Leadership', 'Media & Communications', 'Culture & Hobbies'
        ])

    level = st.selectbox("Level" , options=   ["School", "Inter-School / District", "National", "International"])
    rank = st.selectbox("Rank" , options=[ 'Gold / 1st Place', "Silver / 2nd Place", "Bronze / 3rd Place", "Merit / Finalist", "Participation" , "N/A"])
    if st.button("submit" , disabled=name == ""):
        @st.dialog("Confirm Submittion")
        def confirm():
            col1 , col2 = st.columns(2)
            with col1:
                st.write("Name:")
                st.write("Award date:")
                st.write("Activity Related:")
                st.write("Cateogry:")
                st.write("Rank:")
                st.write("Level:")
                Yes_button = st.button("Yes" , width = 'stretch')
            with col2:
                st.write(name)
                st.write(date)
                if acts == "None":
                    st.write("None")
                else:
                    st.write(acts.name)
                st.write(category)
                st.write(rank)
                st.write(level)
                No_button =  st.button("No" , width = 'stretch')
            
            if No_button:
                st.rerun()
            if Yes_button:
                add_awards(name , date , acts ,category, level , rank)
                st.success("Awards added!")
                time.sleep(0.75)
                st.rerun()
        confirm()