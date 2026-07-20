import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'docmind_ai_secret_key_12984710')
    
    # Paths
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    if os.environ.get('VERCEL') == '1':
        DATABASE = '/tmp/database.db'
        UPLOAD_FOLDER = '/tmp/uploads'
        HF_HOME = '/tmp/.cache'
    else:
        DATABASE = os.path.abspath(os.path.join(BASE_DIR, '..', 'database', 'database.db'))
        UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
        HF_HOME = os.path.join(BASE_DIR, '.cache')
        
    # Upload parameters
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32MB max limit
    
    os.environ['HF_HOME'] = HF_HOME
