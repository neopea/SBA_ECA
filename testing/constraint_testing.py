from database import Teacher , db , app , Student
from flask_sqlalchemy import SQLAlchemy 
from flask import Flask 
from sqlalchemy import text, inspect


with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()

    for table in tables:
        tables_info = inspector.get_unique_constraints(table)
        if not tables_info == []:
            print(table)
            for x in range(len(tables_info)):
                print(tables_info[x]["column_names"])

        #print(table)
        #for col in tables_info:
            #print(col['name'], col['type'], "PK" if col['primary_key'] else "" + 
            #    "not null" if not col["nullable"] else "" 
            #    + f"default{col['default']}" if col["default"] else "" )
        #print()
    #stmt = text("SELECT name FROM sqlite_master WHERE type='table';")
    #stmt = text("select * from sqlite_master where type ='table';")
    #result = db.session.execute(stmt).all()
    #for row in result:
    #    print(row)
