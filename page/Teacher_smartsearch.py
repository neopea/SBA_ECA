import torch 
import numpy
import os

import streamlit as  st
import time
from datetime import datetime
from database import app, db, Student, Activity, StudentActivity, Award, Attendance , Skill 
os.environ["USE_TF"] = "0"
os.environ["USE_TORCH"] = "1"

def display_student(student : Student , score):
    with st.container(border= True):
        student_info_col  ,  score_col,  view_detail_col = st.columns([4, 4, 3] , vertical_alignment='center')
        with student_info_col:
            with st.container(gap=0):
                st.markdown(f"__{student.name}__ ")
                st.markdown(f"Class: {student.class_form} | SSID: {student.ssid}")

        with score_col:
            with st.container(gap=0):
                st.markdown("Relativity Score")
                st.markdown(f"{score:.3f}")
        with view_detail_col:
            if st.button("View Details" , key=student.ssid + "button" , width="content"):
                st.session_state.ssid = student.ssid
                #print("huisdh")
                st.switch_page("page/Student_display.py")

@st.cache_resource
def get_model():
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return model 

@st.cache_resource
def get_embedding_matrix():
    all_acts = db.session.execute(db.select(Activity)).scalars().all()
    all_skills = db.session.execute(db.select(Skill)).scalars().all()
    all_awards = db.session.execute(db.select(Award)).scalars().all()

    return {
        "activities" : [{act.activity_id : act.get_embeddings() for act in all_acts}][0],
        "awards" : [{award.award_id : award.get_embeddings() for award in all_awards}][0],
        "skills" : [{skill.skill_id : skill.get_embeddings() for skill in all_skills}][0]
        }


def get_relativity(query_vector , matrix : list[dict]):
    #return list with relativity > 0.35 
    sim_matrix = {}
    for kkeys, dicts in matrix.items():
        result = {}
        for keys, values in dicts.items():
            sim = model.similarity(values , query_vector).item()
            if sim > 0.35:
                result[keys] = sim
        sim_matrix[kkeys] = result
    return sim_matrix

def get_score(ssid , sim_matrix : list[dict]):
    #act , award , skills 
    score = 0
    student =  db.session.get(Student, ssid)
    act_li = sim_matrix["activities"].keys()
    for enrollment in student.enrollments:
        if enrollment.activity_id in act_li:
            act_score = 0.2
            if enrollment.position_tier == "Leader":
                act_score += 0.5
            elif enrollment.position_tier == "Committee":
                act_score += 0.3
            else:
                act_score += 0.1
            score += act_score * sim_matrix["activities"][enrollment.activity_id] * 10

    rank_weighting = {
        'Gold / 1st Place' : 1.5,
        "Silver / 2nd Place" : 1.25, 
        "Bronze / 3rd Place" : 1, 
        "Merit / Finalist" : 0.75 , 
        "Participation" : 0.5,
        "N/A" : 1
    }

    level_weighting = {
    "School" : 0.75 , 
    "Inter-School / District": 1 , 
    "National" : 1.25,
    "International" : 1.75
    }

    for award in student.awards_received:
        if award.award_id in sim_matrix["awards"].keys():
            score += sim_matrix["awards"][award.award_id] * level_weighting[award.level] * rank_weighting[award.rank] / (1 + (datetime.today() - award.date_awarded).days / 365 * 0.2 ) * 5

    for skill in student.skills:
        if skill.skill_id in sim_matrix["skills"].keys():
            score += sim_matrix["skills"][skill.skill_id] * 2

    return score 



if __name__ == "__main__":
    model = get_model()
    st.title("Smart Student Selector")
    query = st.text_input("Query")
    if "result_dict" not in st.session_state:
        st.session_state.result_dict = {}
    with app.app_context():
        all_student = db.session.execute(db.select(Student)).scalars().all()
        score_li = {}
        embedding_matrix = get_embedding_matrix()
        if st.button("Search"):
            query_embeddings = model.encode(query)

            sim_matrix = get_relativity(query_vector=query_embeddings, matrix=embedding_matrix)
            #st.write(sim_matrix)
            for student in all_student:
                ssid = student.ssid
                score_li[student.ssid] = get_score(ssid , sim_matrix=sim_matrix)
            st.session_state.result_dict = dict(sorted(score_li.items(), key=lambda x : x[1]  , reverse=True) )

        if st.session_state.result_dict != {}:
            for ssid , score in st.session_state.result_dict.items():
                student = db.session.get(Student , ssid)
                display_student(student , score)
            #order according to the mark in score li


