from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import CheckConstraint , event
from sqlalchemy.orm import DeclarativeBase , Mapped , mapped_column , relationship
from sqlalchemy import Engine
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

import numpy  as np
import torch


class base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=base)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///school1.db"

db.init_app(app)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    #print("connected to new db" , dbapi_conn)
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

#m to m linking tables 

teacher_activity_link = db.Table("teacher_activities" , 
    db.Column('teacher_id' , db.String(2) , db.ForeignKey('teachers.teacher_id') , nullable = False ,  primary_key =True) ,
    db.Column('activity_id' , db.Integer , db.ForeignKey('activities.activity_id') , nullable = False ,primary_key =True)
)

student_skills_link = db.Table('student_skills',
    db.Column('student_skill_id' , db.Integer , primary_key = True , autoincrement = True ),
    db.Column('student_ssid' , db.String(8) , db.ForeignKey('students.ssid',ondelete="CASCADE") ,  nullable = False) ,
    db.Column('skill_id', db.Integer, db.ForeignKey('skills.skill_id', ondelete="CASCADE"), nullable=False),
    db.UniqueConstraint('student_ssid', 'skill_id')
)


class Student(db.Model):
    __tablename__ = "students" 
    ssid : Mapped[str] = mapped_column(db.String(8) , primary_key=True )
    name : Mapped[str] = mapped_column(db.String(100)  ,nullable=False)
    password_hash : Mapped[str] = mapped_column(db.String(255) , nullable=False)
    age : Mapped[int] = mapped_column(db.Integer)
    sex : Mapped[str] = mapped_column(db.String(1))
    class_form : Mapped[str] = mapped_column(db.String(2))
    class_number : Mapped[int] =  mapped_column(db.Integer)


    enrollments : Mapped[list["StudentActivity"]] = relationship(back_populates="student" , cascade="all, delete-orphan")
    awards_received : Mapped[list["Award"]] = relationship(back_populates="student" , cascade="all , delete-orphan")
    attendance_records : Mapped[list["Attendance"]] = relationship(back_populates="student" , cascade="all ,delete-orphan")
    skills : Mapped[list["Skill"]] = relationship(secondary=student_skills_link ,back_populates="student")
    highlights : Mapped[list["TeacherHighlight"]] = relationship(back_populates="student" , cascade="all , delete-orphan")
    notifications : Mapped[list["Notification"]] = relationship(back_populates="student" , cascade="all , delete-orphan")

    def __repr__(self):
        return f"<Student {self.ssid} {self.name}>"
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        print("new password setted for " , self)
    def check_password(self, password):
        return check_password_hash( self.password_hash , password)
    
class Teacher(db.Model):
    __tablename__ = "teachers"
    teacher_id : Mapped[str] = mapped_column(db.String(2) , primary_key=True)
    password_hash : Mapped[str] = mapped_column(db.String(255))
    name : Mapped[str] = mapped_column(db.String(200))

    highlights : Mapped[list["TeacherHighlight"]] = relationship(back_populates='teacher')
    activities_in_charge : Mapped[list["Activity"]] = relationship(secondary=teacher_activity_link , back_populates='teachers_in_charge')
    notifications : Mapped[list["Notification"]] = relationship(back_populates='teacher')

    def __repr__(self):
        return f"<Teacher {self.teacher_id}>"
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        print("new password setted for " , self)
    def check_password(self, password):
        return check_password_hash(self.password_hash , password)
    
class Activity(db.Model):
    __tablename__ = "activities"
    activity_id : Mapped[int] = mapped_column(db.Integer , primary_key=True ,  autoincrement=True)
    name : Mapped[str] = mapped_column(db.String(100) , nullable=False , unique=True)
    category : Mapped[str] = mapped_column(db.String(100))
    description : Mapped[str] = mapped_column(db.Text)
    enrollments : Mapped[list["StudentActivity"]] = relationship(back_populates='activity' , cascade="all , delete-orphan")
    teachers_in_charge : Mapped[list["Teacher"]]= relationship(
        secondary=teacher_activity_link,
        back_populates='activities_in_charge'
    )
    __table_args__ = (
        CheckConstraint(category.in_([
            'Academic & STEM', 'Arts & Performance', 'Sports & Athletics', 
            'Service & Leadership', 'Media & Communications', 'Culture & Hobbies'
        ]), name='category_check'),
    )



    awards_given :Mapped[list["Award"]]= relationship(back_populates='activity', cascade='all, delete-orphan')
    
    attendance_logs : Mapped[list["Attendance"]]= relationship( back_populates='activity', cascade='all, delete-orphan')

    notifications : Mapped[list["Notification"]]= relationship(back_populates='activity', cascade='all, delete-orphan')

    embeddings : Mapped[bytes] = mapped_column(db.LargeBinary , nullable=False)

    def set_embeddings(self , np_array ):
        self.embeddings = np_array.tobytes()
    def get_embeddings(self):
        return torch.from_numpy(np.frombuffer(self.embeddings , dtype= np.float32)).reshape(1,384)
    
    def __repr__(self):
        return f"<Activity {self.name}>"

class Award(db.Model):
    __tablename__ = 'awards'
    award_id : Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    student_ssid : Mapped[str] = mapped_column(db.String(8), db.ForeignKey('students.ssid'), nullable=False)
    activity_id : Mapped[int]= mapped_column(db.Integer, db.ForeignKey('activities.activity_id'), nullable=True)
    award_name : Mapped[str] = mapped_column(db.Text, nullable=False)
    date_awarded : Mapped[datetime] = mapped_column(db.DateTime, nullable=False)
    category : Mapped[str] = mapped_column(db.Text)
    level : Mapped[str] = mapped_column(db.Text)
    rank : Mapped[str] = mapped_column(db.Text)
    embeddings : Mapped[bytes] = mapped_column(db.LargeBinary , nullable=False)

    student : Mapped["Student"] = relationship(back_populates="awards_received")
    activity : Mapped["Activity"] = relationship(back_populates="awards_given")

    __table_args__ = (
    CheckConstraint(category.in_([
        'Academic & STEM', 'Arts & Performance', 'Sports & Athletics', 
        'Service & Leadership', 'Media & Communications', 'Culture & Hobbies'
    ]), name='category_check'),

    CheckConstraint(level.in_([
    "School", "Inter-School / District", "National", "International"
    ]) , name="level_check"),

    CheckConstraint(rank.in_([
        'Gold / 1st Place', "Silver / 2nd Place", "Bronze / 3rd Place", "Merit / Finalist", "Participation" , "N/A"
    ]), name="rank_check"),
    )


    def set_embeddings(self , np_array ):
        self.embeddings = np_array.tobytes()
    def get_embeddings(self):
        return torch.from_numpy(np.frombuffer(self.embeddings , dtype= np.float32)).reshape(1,384)
    
class Skill(db.Model):
    __tablename__ = "skills"
    skill_id = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    skill_name = mapped_column(db.String(100), nullable=False, unique=True)

    student : Mapped[list["Student"]] = relationship(secondary=student_skills_link , back_populates='skills')
    embeddings : Mapped[bytes] = mapped_column(db.LargeBinary , nullable=False)

    def set_embeddings(self , np_array ):
        self.embeddings = np_array.tobytes()
    def get_embeddings(self):
        return torch.from_numpy(np.frombuffer(self.embeddings , dtype= np.float32)).reshape(1,384)
    def __repr__(self):
        return f"<Skill {self.skill_name}>"

class TeacherHighlight(db.Model):
    __tablename__ = 'teacher_highlights'
    highlight_id : Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    teacher_id : Mapped[str] = mapped_column(db.String(2), db.ForeignKey('teachers.teacher_id'), nullable=False)
    student_ssid : Mapped[str] = mapped_column(db.String(8), db.ForeignKey('students.ssid'), nullable=True)
    activity_id : Mapped[int] = mapped_column(db.Integer, db.ForeignKey('activities.activity_id'), nullable=True)
    
    teacher = db.relationship('Teacher', back_populates='highlights')
    student = db.relationship('Student', back_populates='highlights')
    activity = db.relationship('Activity')
    __table_args__ = (
        db.UniqueConstraint('teacher_id', 'student_ssid', 'activity_id', name='unique_check'),
        CheckConstraint("(student_ssid is not null and activity_id is null) or (student_ssid is null and activity_id is not null)", name="student_act_check"),
    )

class StudentActivity(db.Model):
    __tablename__ = 'student_activities'
    
    enrollment_id : Mapped[int]= mapped_column(db.Integer, primary_key=True, autoincrement=True)
    student_ssid : Mapped[str] = mapped_column(db.String(8), db.ForeignKey('students.ssid'), nullable=False)
    activity_id : Mapped[int] = mapped_column(db.Integer, db.ForeignKey('activities.activity_id'), nullable=False)
    role : Mapped[str] = mapped_column(db.String(100), default='Member')
    status : Mapped[str] = mapped_column(db.Text, default='Interested')
    position_tier : Mapped[str] = mapped_column(db.Text , nullable=False , default="Member")
    academic_year : Mapped[str] = mapped_column(db.String(20)) 

    student : Mapped["Student"] = relationship(back_populates="enrollments")
    activity : Mapped["Activity"] = relationship(back_populates="enrollments")

    __table_args__ = (
        CheckConstraint(status.in_(['Joined', 'Interested' , "Rejected"]), name='status_check'),
        db.UniqueConstraint('student_ssid', 'activity_id' , 'academic_year', name="unique_check"),
        CheckConstraint(position_tier.in_(["Leader" , "Committee" , "Member"]))
    )
    def __repr__(self):
        return f"<StudentActivity {self.enrollment_id} >"

class Attendance(db.Model):
    __tablename__ = 'attendance'
    attendance_id : Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    student_ssid : Mapped[str] = mapped_column(db.String(8), db.ForeignKey('students.ssid'), nullable=False)
    activity_id : Mapped[int]= mapped_column(db.Integer, db.ForeignKey('activities.activity_id'), nullable=False)
    session_date : Mapped[datetime] = mapped_column(db.DateTime, nullable=False)
    status : Mapped[str] = mapped_column(db.Text, nullable=False)
    
    # Links to the parent objects
    student :Mapped["Student"] = db.relationship('Student', back_populates='attendance_records')
    activity : Mapped["Activity"] = db.relationship('Activity', back_populates='attendance_logs')
    __table_args__ = (
        CheckConstraint(status.in_(['Present', 'Absent', 'Sick Leave', 'Personal Leave']), name='attendance_status_check'),
    )

class Notification(db.Model):
    __tablename__ = 'notifications' 
    notification_id : Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    teacher_id : Mapped[str] = mapped_column(db.String(2), db.ForeignKey('teachers.teacher_id'), nullable=False)
    student_ssid : Mapped[str] = mapped_column(db.String(8), db.ForeignKey('students.ssid'), nullable=True)
    activity_id : Mapped[int] = mapped_column(db.Integer, db.ForeignKey('activities.activity_id'), nullable=True)


    title : Mapped[str] = mapped_column(db.String(30), nullable=False)
    is_read : Mapped[bool]= mapped_column(db.Boolean, default =False)
    message : Mapped[str] = mapped_column(db.String(200), nullable=True)
    create_time : Mapped[datetime]= mapped_column(db.DateTime , default= datetime.now())
    category : Mapped[str] = mapped_column(db.String , nullable=False , default="General")


    teacher : Mapped["Teacher"]= relationship('Teacher', back_populates='notifications')
    student : Mapped["Student"]= relationship('Student', back_populates='notifications')
    activity : Mapped["Activity"] = relationship('Activity' , back_populates='notifications')

    __table_args__ = (
        CheckConstraint(category.in_(["General", "Activity Update", "Warning"]) , name = "category_check"),
    )

with app.app_context():
    db.create_all()
    db.session.commit()