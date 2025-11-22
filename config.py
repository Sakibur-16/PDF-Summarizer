# config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration settings for the document summarizer bot"""
    
    # API Configuration
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    
    # Model Selection (you can change this to any OpenRouter supported model)
    # Recommended models for multilingual support:
    # - "anthropic/claude-3.5-sonnet" (best quality)
    # - "google/gemini-pro-1.5" (good multilingual)
    # - "meta-llama/llama-3.1-70b-instruct" (cost-effective)
    MODEL_NAME = "anthropic/claude-3.5-sonnet"
    
    # Language Settings
    SUPPORTED_LANGUAGES = {
        'bengali': 'bn',
        'english': 'en',
        'arabic': 'ar'
    }
    
    LANGUAGE_NAMES = {
        'bn': 'Bengali (বাংলা)',
        'en': 'English',
        'ar': 'Arabic (العربية)'
    }
    
    LANGUAGE_INSTRUCTIONS = {
        'bn': 'বাংলায় উত্তর দিন। সাবলীল ও প্রাকৃতিক ভাষা ব্যবহার করুন।',
        'en': 'Respond in English. Use natural and fluent language.',
        'ar': 'أجب بالعربية. استخدم لغة طبيعية وطلقة.'
    }
    
    # Tesseract Configuration
    # Update this path based on your system
    TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows
    # For Linux/Mac: '/usr/bin/tesseract'
    
    TESSERACT_LANG_MAP = {
        'bn': 'ben',
        'en': 'eng',
        'ar': 'ara'
    }
    
    # Processing Settings
    MAX_CHUNK_SIZE = 12000  # Characters per chunk for processing
    SUMMARY_DETAIL_LEVEL = "elaborate"  # Options: brief, moderate, elaborate
    
    # Output Settings
    LOG_DIR = Path("logs")
    OUTPUT_DIR = Path("outputs")
    
    # Create directories if they don't exist
    LOG_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Academic Paper Keywords
    ACADEMIC_SECTIONS = [
        'abstract', 'introduction', 'literature review', 'related work',
        'methodology', 'methods', 'approach', 'proposed method',
        'implementation', 'experiments', 'experimental setup',
        'results', 'findings', 'analysis', 'discussion',
        'conclusion', 'future work', 'references'
    ]
    
    # API Request Settings
    MAX_TOKENS = 4000
    TEMPERATURE = 0.7
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY not found. Please set it in .env file")
        
        if not Path(cls.TESSERACT_CMD).exists():
            print(f"Warning: Tesseract not found at {cls.TESSERACT_CMD}")
            print("OCR functionality may not work. Please install Tesseract OCR.")
        
        return True