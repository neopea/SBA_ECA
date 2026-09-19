import streamlit as st
from database import db , app , Teacher , Activity , teacher_activity_link
import time
from page.Teacher_smartsearch import get_model
st.title("Create Activity")




def add_acts(name , categories , description , teachers_in_charge):
    with app.app_context():
        new_acts = Activity(name=name , category=categories , description=description)
        tensor = model.encode(name)
        new_acts.set_embeddings(tensor)
        db.session.add(new_acts)
        db.session.commit()
        acts = db.session.execute(db.select(Activity).where(Activity.name == name)).scalars().first()
        acts.teachers_in_charge.extend(teachers_in_charge)
        db.session.commit()




with app.app_context():
    categories = db.session.execute(db.select(Activity.category).distinct().order_by(Activity.category)).scalars().all()
    teachers = db.session.execute(db.select(Teacher).order_by(Teacher.name)).scalars().all()

    name = st.text_input("name")
    cate = st.selectbox(label="categories" , options=categories)



    teachers = st.multiselect(label="Teacher(s) in charge" , options=teachers , format_func=lambda x : x.name )
    description = st.text_input('description')
    model = get_model()
    if st.button("Submit"):
        if name == '':
            st.warning("Activity name cannot be empty")
        elif teachers :
            print('')
        else:
            @st.dialog("Confirm submission?")
            def confirm():
                st.write() 
                col1 , col2 = st.columns(2)
                with col1:
                    Yes_button = st.button("Yes" , width = 'stretch')
                with col2:
                    No_button =  st.button("No" , width = 'stretch')
                if Yes_button:
                    #try:
                        add_acts(name , cate , description , teachers_in_charge=teachers)
                        st.success(f"new acts {name} added")

                    #except:
                    #    st.warning(f"{acts.name} already joined")
                    #finally:
                    #    time.sleep(0.5)
                    #    st.rerun()
                if No_button:
                    time.sleep(0.5)
                    st.rerun()
            confirm()
