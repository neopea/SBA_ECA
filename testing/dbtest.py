from database import Teacher , db , app , Student , Skill , student_skills_link
from flask_sqlalchemy import SQLAlchemy 
from flask import Flask 
from sqlalchemy import text, inspect 

with app.app_context():

    stmt1 = text(
        '''
        EXPLAIN QUERY PLAN
        SELECT s.name, sk.skill_name 
        FROM students s
        JOIN student_skills link ON s.ssid = link.student_ssid
        JOIN skills sk ON link.skill_id = sk.skill_id
        WHERE s.ssid = 's2022001';
    '''
    )
    stmt2 = text(
        '''
        update 
        '''
    )
   # result = db.session.execute(stmt1).all()
    #for row in result:
    #   print(row)

    for student in db.session.query(Student):
        student.set_password("123")
        print(f"updating student f{student}")
        
    db.session.commit()

        #stmt2 = text("explain query plan select * from students;")
