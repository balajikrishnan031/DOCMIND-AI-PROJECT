import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'docmind_ai_secret_key_12984710')
    
    # Paths
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE = os.path.join(BASE_DIR, 'database', 'database.db')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    
    # Upload parameters
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32MB max limit
    
    # Local Cache for sentence-transformers
    HF_HOME = os.path.join(BASE_DIR, '.cache')
    os.environ['HF_HOME'] = HF_HOME
