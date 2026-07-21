import sqlite3
import os
from flask import g, current_app

def get_db():
    if 'db' not in g:
        turso_url = os.environ.get('TURSO_DATABASE_URL')
        turso_token = os.environ.get('TURSO_AUTH_TOKEN')
        
        if turso_url and turso_token:
            try:
                import libsql_experimental as libsql
                g.db = libsql.connect(turso_url, auth_token=turso_token)
                g.db.row_factory = sqlite3.Row
                return g.db
            except Exception as e:
                print(f"Turso Cloud DB Connection Notice: {e}, falling back to local SQLite.")

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
    base_dir = current_app.config.get('BASE_DIR', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    candidates = [
        os.path.abspath(os.path.join(base_dir, '..', 'database', 'schema.sql')),
        os.path.abspath(os.path.join(base_dir, 'database', 'schema.sql')),
        '/var/task/database/schema.sql'
    ]
    schema_path = None
    for cand in candidates:
        if os.path.exists(cand):
            schema_path = cand
            break
            
    if not schema_path:
        raise FileNotFoundError("Could not find schema.sql in any expected directory path.")
        
    with open(schema_path, 'r', encoding='utf-8') as f:
        db.executescript(f.read())
    db.commit()

    try:
        from utils.sample_dataset_loader import SampleDatasetLoader
        SampleDatasetLoader.seed_academic_database(db)
    except Exception as e:
        print(f"Sample dataset loader notice: {e}")

def init_app(app):
    app.teardown_appcontext(close_db)
    # Automatically initialize db if it doesn't exist
    with app.app_context():
        if not os.path.exists(app.config['DATABASE']):
            init_db()
            print("Database initialized successfully.")
