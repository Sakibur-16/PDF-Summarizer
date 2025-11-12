# logger_module.py
import logging
import json
from datetime import datetime
from pathlib import Path
from config import Config

class DocumentLogger:
    """Comprehensive logging system for document processing"""
    
    def __init__(self, document_name):
        self.document_name = document_name
        self.start_time = datetime.now()
        self.log_file = Config.LOG_DIR / f"{self.document_name}_{self.start_time.strftime('%Y%m%d_%H%M%S')}.log"
        self.json_log_file = Config.LOG_DIR / f"{self.document_name}_{self.start_time.strftime('%Y%m%d_%H%M%S')}.json"
        
        # Setup logging
        self.logger = logging.getLogger(self.document_name)
        self.logger.setLevel(logging.DEBUG)
        
        # File handler
        fh = logging.FileHandler(self.log_file, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
        
        # JSON log data
        self.json_data = {
            'document_name': document_name,
            'start_time': self.start_time.isoformat(),
            'events': [],
            'statistics': {},
            'errors': []
        }
        
        self.log_event("Logging started", "INFO")
    
    def log_event(self, message, level="INFO", details=None):
        """Log an event with timestamp"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message
        }
        
        if details:
            event['details'] = details
        
        self.json_data['events'].append(event)
        
        # Log to file
        if level == "DEBUG":
            self.logger.debug(message)
        elif level == "INFO":
            self.logger.info(message)
        elif level == "WARNING":
            self.logger.warning(message)
        elif level == "ERROR":
            self.logger.error(message)
            self.json_data['errors'].append(event)
        elif level == "CRITICAL":
            self.logger.critical(message)
            self.json_data['errors'].append(event)
    
    def log_processing_start(self, file_path, file_size, language):
        """Log start of document processing"""
        self.log_event(
            f"Starting processing: {file_path}",
            "INFO",
            {
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'language': language
            }
        )
    
    def log_ocr_operation(self, page_count, success=True):
        """Log OCR operation"""
        if success:
            self.log_event(
                f"OCR completed successfully on {page_count} pages",
                "INFO",
                {'page_count': page_count}
            )
        else:
            self.log_event(
                f"OCR failed",
                "ERROR",
                {'page_count': page_count}
            )
    
    def log_chapter_processed(self, chapter_name, word_count):
        """Log chapter processing"""
        self.log_event(
            f"Chapter processed: {chapter_name}",
            "INFO",
            {'word_count': word_count}
        )
    
    def log_summary_generated(self, summary_type, word_count, language):
        """Log summary generation"""
        self.log_event(
            f"{summary_type} summary generated",
            "INFO",
            {
                'word_count': word_count,
                'language': language
            }
        )
    
    def log_api_call(self, endpoint, tokens_used, cost=None):
        """Log API calls"""
        details = {'tokens_used': tokens_used}
        if cost:
            details['estimated_cost'] = cost
        
        self.log_event(
            f"API call to {endpoint}",
            "DEBUG",
            details
        )
    
    def add_statistics(self, stats_dict):
        """Add processing statistics"""
        self.json_data['statistics'].update(stats_dict)
        self.log_event("Statistics updated", "INFO", stats_dict)
    
    def finalize(self):
        """Finalize logging and save JSON log"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        self.json_data['end_time'] = end_time.isoformat()
        self.json_data['duration_seconds'] = duration
        
        # Save JSON log
        with open(self.json_log_file, 'w', encoding='utf-8') as f:
            json.dump(self.json_data, f, ensure_ascii=False, indent=2)
        
        self.log_event(
            f"Processing completed in {duration:.2f} seconds",
            "INFO"
        )
        
        return self.json_log_file
    
    def get_summary_report(self):
        """Get a summary report of the processing"""
        return {
            'document': self.document_name,
            'duration': (datetime.now() - self.start_time).total_seconds(),
            'events_count': len(self.json_data['events']),
            'errors_count': len(self.json_data['errors']),
            'statistics': self.json_data['statistics']
        }