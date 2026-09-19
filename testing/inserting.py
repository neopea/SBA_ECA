    

from database import Teacher , db , app , Student , Attendance , Activity 
from flask_sqlalchemy import SQLAlchemy 
from flask import Flask 
from sqlalchemy import text, inspect


with app.app_context():
    new_act = Activity(name= 'Coding Team 101', category ="ICT" , description = 'test' )
    try:
        db.session.add(new_act)
        db.session.commit()
    except Exception as e:
        print(e)
