import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # ArXiv search configuration
    KEYWORDS = os.getenv('ARXIV_KEYWORDS', 'machine learning,artificial intelligence').split(',')
    MAX_PAPERS = int(os.getenv('MAX_PAPERS', '5'))
    MAX_BACK_DAY = int(os.getenv('MAX_BACK_DAY', '3'))
    ARXIV_SOURCE = os.getenv('ARXIV_SOURCE', 'api').strip().lower()
    if ARXIV_SOURCE not in ('api', 'rss'):
        ARXIV_SOURCE = 'api'
    # Gemini API configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # Email configuration
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SENDER_EMAIL = os.getenv('SENDER_EMAIL')
    SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')  # Use app password for Gmail
    RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')
    
    # WeChat configuration
    WECHAT_ENABLED = os.getenv('WECHAT_ENABLED', 'false').lower() == 'true'
    WECHAT_RECIPIENT = os.getenv('WECHAT_RECIPIENT')  # WeChat username to send to
    
    # Other settings
    PDF_DOWNLOAD_DIR = os.getenv('PDF_DOWNLOAD_DIR', './downloads')
    SCHEDULE_TIME = os.getenv('SCHEDULE_TIME', '09:00')  # Daily run time
    SEND_AS_IMAGE = os.getenv('SEND_AS_IMAGE', 'true').lower() == 'true'  # Send as image instead of HTML
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required_vars = [
            ('GEMINI_API_KEY', cls.GEMINI_API_KEY),
            ('SENDER_EMAIL', cls.SENDER_EMAIL),
            ('SENDER_PASSWORD', cls.SENDER_PASSWORD),
            ('RECIPIENT_EMAIL', cls.RECIPIENT_EMAIL)
        ]
        
        # Check WeChat configuration if enabled
        if cls.WECHAT_ENABLED:
            required_vars.append(('WECHAT_RECIPIENT', cls.WECHAT_RECIPIENT))
        
        missing_vars = [var_name for var_name, var_value in required_vars if not var_value]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True