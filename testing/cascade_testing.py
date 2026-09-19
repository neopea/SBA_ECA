from database import Teacher , db , app , Student , Skill , student_skills_link
from flask_sqlalchemy import SQLAlchemy 
from flask import Flask 
from sqlalchemy import text, inspect


with app.app_context():
    inspector = inspect(db.engine)
    def get_length():
        parents = db.session.query(Student).all()
        children = db.session.query(student_skills_link).all()

        print(f"length of parent table ={len(parents)}")
        print(f"length of child table ={len(children)}")


    print(" ------ initial ----- ")
    get_length()


    stmt = text("select * from student_skills where student_ssid = 's2022001';")
    result = db.session.execute(stmt).all()
    print(result)

    student_to_del = db.session.get(Student , 's2022001')

    try:
        db.session.delete(student_to_del)
        db.session.flush()
    except Exception as e:
        print(e)
    
    db.session.expire_all()

    print(" ------ final ----- ")

    get_length()
