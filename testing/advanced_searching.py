import torch 
import numpy
import os
import time
from datetime import datetime
from database import app, db, Student, Activity, StudentActivity, Award, Attendance , Skill 
os.environ["USE_TF"] = "0"
os.environ["USE_TORCH"] = "1"

s = time.perf_counter()
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

e = time.perf_counter()



def get_embedding_matrix(student :Student):
    student_award_dict = {}
    for award in student.awards_received:
        student_award_dict[award.award_id] = award.get_embeddings()
    student_skill_dict = {}
    for skill in student.skills:
        student_skill_dict[skill.skill_id] = skill.get_embeddings()
    student_act_dict ={}
    for enrollment in student.enrollments:
        act_id = enrollment.activity_id
        student_act_dict[act_id] = enrollment.activity.get_embeddings()

    return [ student_act_dict , student_award_dict , student_skill_dict]


def get_relativity(query_vector , student_matrix : list[dict]):
    #return list with relativity > 0.35 
    li= []
    for student_dicts in student_matrix:
        result = {}
        for keys, values in student_dicts.items():
            sim = model.similarity(values , query_vector).item()
            if sim > 0.35:
                result[keys] = sim
        li.append(result)
    return li

def get_score(ssid , filtered_student_matrix : list[dict]):
    #act , award , skills 
    score = 0
    student =  db.session.get(Student, ssid)
    act_li = filtered_student_matrix[0].keys()
    for enrollment in student.enrollments:
        if enrollment.activity_id in act_li:
            act_score = 0
            if enrollment.position_tier == "Leader":
                act_score += 0.5
            elif enrollment.position_tier == "Committee":
                act_score += 0.3
            else:
                act_score += 0.1
            score += act_score * filtered_student_matrix[0][enrollment.activity_id]

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

    for award_id , sim in filtered_student_matrix[1].items():
        award = db.session.get(Award , award_id)
        score += sim * level_weighting[award.level] * rank_weighting[award.rank] / (1 + (datetime.today() - award.date_awarded).days() / 365 * 0.2 ) 
    pass

    for sim in filtered_student_matrix[2].values():
        score += sim

    return score 

with app.app_context():
    query = input("Word query:")
    query_embedding = model.encode(query)
    print(query_embedding)
    #all_student = db.session.execute(db.select(Student)).scalars().all()


    # print(e-s)
    #m = get_embedding_matrix(all_student[0])
    #print(query_embedding.shape())
    #x= get_relativity(query_vector=query_embedding, student_matrix=m)
    #print(get_score(all_student[0].ssid , x))
    #print(x[0][17].shape())

