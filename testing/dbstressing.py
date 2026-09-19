# dbstressing.py
import time
from database import Teacher, db, app, Student, Skill, student_skills_link
from sqlalchemy import text

BATCH = 5000


# ---------- C ----------
def stress_write(total):
    print(f"Inserting {total} records...")
    t0 = time.time()

    for start in range(1, total + 1, BATCH):
        end = min(start + BATCH, total + 1)
        rows = [
            dict(ssid=f"STRESS_{i}", password_hash="x", name=f"Student_{i}",
                 age=12, sex="M", class_form="5A", class_number=12)
            for i in range(start, end)
        ]
        db.session.bulk_insert_mappings(Student, rows)
        db.session.commit()

    dt = time.time() - t0
    print(f"Insert: {total} rows in {dt:.2f}s ({total/dt:.0f} rows/s)")


# ---------- R ----------
def stress_read():
    print("Reading...")
    t0 = time.time()
    total = db.session.execute(text(
        "SELECT COUNT(*) FROM students WHERE ssid GLOB 'STRESS_*'"
    )).scalar()
    dt = time.time() - t0
    print(f"Read: {total} rows in {dt:.2f}s ({total/dt:.0f} rows/s)")


# ---------- U ----------
def stress_update():
    print("Updating...")
    t0 = time.time()
    last = ""
    done = 0

    while True:
        # find the next batch and remember its last ssid
        batch_last = db.session.execute(text("""
            SELECT MAX(ssid) FROM (
                SELECT ssid FROM students
                WHERE ssid GLOB 'STRESS_*' AND ssid > :last
                ORDER BY ssid
                LIMIT :n
            )
        """), {"last": last, "n": BATCH}).scalar()

        if batch_last is None:
            break

        res = db.session.execute(text("""
            UPDATE students SET age = age + 1
            WHERE ssid IN (
                SELECT ssid FROM students
                WHERE ssid GLOB 'STRESS_*'
                AND ssid > :last AND ssid <= :batch_last
            )
        """), {"last": last, "batch_last": batch_last})
        print("updation")
        db.session.commit()

        done += res.rowcount
        last = batch_last

    dt = time.time() - t0
    print(f"Update: {done} rows in {dt:.2f}s ({done/dt:.0f} rows/s)")

    

# ---------- D ----------
def stress_delete():
    print("Deleting...")
    t0 = time.time()
    db.session.execute(text("PRAGMA foreign_keys = ON"))

    done = 0
    counter =0 
    while True:
        counter += 1
        res = db.session.execute(text("""
            DELETE FROM students
            WHERE ssid IN (
                SELECT ssid FROM students
                WHERE ssid GLOB 'STRESS_*'
                LIMIT :n
            )
        """), {"n": BATCH})
        print(f"deleted:{BATCH * counter}")
        db.session.commit()
        if res.rowcount == 0:
            break
        done += res.rowcount

    dt = time.time() - t0
    print(f"Delete: {done} rows in {dt:.2f}s ({done/dt:.0f} rows/s)")


# Run within app context
with app.app_context():
    try:
        stress_delete()
        stress_write(50000)
        stress_read()
        stress_update()
        stress_delete()
        db.session.execute(text("VACUUM"))
    finally:
        db.session.remove()
        db.engine.dispose()