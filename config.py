import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    # Secret key for session management
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-this-in-production')
    
    # Base directory of the application
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # SQLite Database Path
    DATABASE_PATH = os.path.join(BASE_DIR, 'database.db')
    
    # Google Gemini API Key
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    
    # Document upload configurations
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 Megabytes max
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}
    
    # Ensure upload folder exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
