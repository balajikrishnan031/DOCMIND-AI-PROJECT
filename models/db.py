import sqlite3
import os
from flask import g, current_app

def get_db():
    if 'db' not in g:
        db_path = current_app.config['DATABASE']
        # Ensure database directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        g.db = sqlite3.connect(
            db_path,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    schema_path = os.path.join(current_app.config['BASE_DIR'], 'database', 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        db.executescript(f.read())
    db.commit()

def init_app(app):
    app.teardown_appcontext(close_db)
    # Automatically initialize db if it doesn't exist
    with app.app_context():
        if not os.path.exists(app.config['DATABASE']):
            init_db()
            print("Database initialized successfully.")
