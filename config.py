import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Drn11@2003'
    UPLOAD_FOLDER = 'static/uploads'
    DOWNLOAD_FOLDER = 'downloads'
    MAX_CONTENT_LENGTH = 200 * 1024 * 1024  # 200MB max file size
    
    # Supported file extensions
    ALLOWED_EXTENSIONS = {
        'pdf', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff',
        'mp3', 'wav', 'ogg', 'flac', 'm4a', 'aac', 'mp4', 'avi', 'mov'
    }
    
    # Cleanup settings
    TEMP_FILE_LIFETIME = timedelta(hours=1)
    
    # OCR language settings
    OCR_LANGUAGES = ['eng', 'spa', 'fra', 'deu', 'ita', 'por', 'rus', 'chi_sim', 'jpn', 'kor']
    
    # TTS settings
    TTS_LANGUAGES = {
        'en': 'English',
        'es': 'Spanish', 
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'ja': 'Japanese',
        'ko': 'Korean',
        'zh': 'Chinese'
    }
    
    @staticmethod
    def init_app(app):
        # Create directories if they don't exist
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.DOWNLOAD_FOLDER, exist_ok=True)