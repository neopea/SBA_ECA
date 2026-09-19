# index_all_fks.py
from database import app, db
from sqlalchemy import text

with app.app_context():
    conn = db.session.connection()

    tables = conn.execute(text("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
    """)).scalars().all()

    for table in tables:
        for fk in conn.execute(text(f'PRAGMA foreign_key_list("{table}")')).all():
            print(fk)
            col = fk[3]                      
            name = f"ix_fk_{table}_{col}"
            conn.execute(text(
                f'CREATE INDEX IF NOT EXISTS "{name}" ON "{table}" ("{col}")'
            ))
            print(f"indexed {table}.{col} , {name}")

    db.session.commit()
    db.session.remove()
    db.engine.dispose()