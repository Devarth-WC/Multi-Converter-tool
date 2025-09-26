import os
import shutil
import tempfile
import logging
import mimetypes
from datetime import datetime, timedelta
from pathlib import Path
import hashlib

class FileValidator:
    """Utility class for file validation"""
    
    # Supported file extensions
    SUPPORTED_EXTENSIONS = {
        'pdf': ['.pdf'],
        'document': ['.docx', '.txt'],
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'],
        'audio': ['.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac'],
        'video': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']
    }
    
    # Maximum file sizes (in bytes)
    MAX_FILE_SIZES = {
        'pdf': 50 * 1024 * 1024,      # 50MB
        'document': 10 * 1024 * 1024,  # 10MB
        'image': 20 * 1024 * 1024,     # 20MB
        'audio': 100 * 1024 * 1024,    # 100MB
        'video': 200 * 1024 * 1024     # 200MB
    }
    
    @classmethod
    def is_valid_file(cls, file_path):
        """Check if file is valid and supported"""
        if not os.path.exists(file_path):
            return False, "File does not exist"
        
        if not os.path.isfile(file_path):
            return False, "Path is not a file"
        
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            return False, "File is empty"
        
        file_extension = Path(file_path).suffix.lower()
        file_type = cls.get_file_type(file_extension)
        
        if file_type == 'unknown':
            return False, f"Unsupported file type: {file_extension}"
        
        max_size = cls.MAX_FILE_SIZES.get(file_type, 50 * 1024 * 1024)
        if file_size > max_size:
            return False, f"File too large. Maximum size for {file_type}: {max_size // (1024*1024)}MB"
        
        return True, "File is valid"
    
    @classmethod
    def get_file_type(cls, file_extension):
        """Get file type category from extension"""
        file_extension = file_extension.lower()
        
        for file_type, extensions in cls.SUPPORTED_EXTENSIONS.items():
            if file_extension in extensions:
                return file_type
        
        return 'unknown'
    
    @classmethod
    def get_supported_conversions(cls, file_type):
        """Get list of supported conversions for a file type"""
        conversions = {
            'pdf': ['pdf_to_docx', 'pdf_to_txt', 'pdf_to_audio'],
            'document': ['text_to_audio', 'txt_to_docx', 'docx_to_txt'],
            'image': [
                'image_to_pdf', 'image_to_text', 'image_resize', 'image_format', 
                'image_compress', 'image_filter', 'image_rotate', 'image_collage'
            ],
            'audio': [
                'audio_to_text', 'audio_format', 'audio_compress', 'audio_merge', 
                'audio_trim', 'audio_speed', 'audio_normalize'
            ],
            'video': ['video_to_audio']
        }
        
        return conversions.get(file_type, [])
    
    @classmethod
    def validate_conversion_type(cls, file_type, conversion_type):
        """Validate if conversion type is supported for file type"""
        supported_conversions = cls.get_supported_conversions(file_type)
        return conversion_type in supported_conversions


class ConversionLogger:
    """Logger for conversion operations"""
    
    def __init__(self, log_file='conversion.log'):
        self.logger = logging.getLogger('file_converter')
        self.logger.setLevel(logging.INFO)
        
        # Create file handler
        handler = logging.FileHandler(log_file)
        handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        # Add handler to logger
        if not self.logger.handlers:
            self.logger.addHandler(handler)
    
    def log_conversion_start(self, input_file, conversion_type):
        """Log start of conversion"""
        self.logger.info(f"Starting conversion: {input_file} -> {conversion_type}")
    
    def log_conversion_success(self, input_file, output_file, conversion_type, duration):
        """Log successful conversion"""
        self.logger.info(
            f"Conversion successful: {input_file} -> {output_file} "
            f"({conversion_type}) in {duration:.2f} seconds"
        )
    
    def log_conversion_error(self, input_file, conversion_type, error):
        """Log conversion error"""
        self.logger.error(
            f"Conversion failed: {input_file} ({conversion_type}) - {str(error)}"
        )
    
    def log_file_validation_error(self, file_path, error):
        """Log file validation error"""
        self.logger.warning(f"File validation failed: {file_path} - {error}")


class TempFileManager:
    """Manager for temporary files and cleanup"""
    
    def __init__(self, temp_dir=None, max_age_hours=1):
        self.temp_dir = temp_dir or tempfile.gettempdir()
        self.max_age = timedelta(hours=max_age_hours)
        self.managed_files = set()
    
    def create_temp_file(self, suffix='', prefix='converter_'):
        """Create a temporary file"""
        temp_file = tempfile.NamedTemporaryFile(
            suffix=suffix, 
            prefix=prefix, 
            dir=self.temp_dir,
            delete=False
        )
        temp_path = temp_file.name
        temp_file.close()
        
        self.managed_files.add(temp_path)
        return temp_path
    
    def create_temp_dir(self, prefix='converter_'):
        """Create a temporary directory"""
        temp_dir = tempfile.mkdtemp(prefix=prefix, dir=self.temp_dir)
        self.managed_files.add(temp_dir)
        return temp_dir
    
    def cleanup_file(self, file_path):
        """Clean up a specific file"""
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
            
            self.managed_files.discard(file_path)
            return True
        except Exception:
            return False
    
    def cleanup_old_files(self):
        """Clean up old temporary files"""
        current_time = datetime.now()
        cleaned_count = 0
        
        for file_path in list(self.managed_files):
            try:
                if os.path.exists(file_path):
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if current_time - file_time > self.max_age:
                        if self.cleanup_file(file_path):
                            cleaned_count += 1
                else:
                    self.managed_files.discard(file_path)
            except Exception:
                continue
        
        return cleaned_count
    
    def cleanup_all(self):
        """Clean up all managed files"""
        cleaned_count = 0
        for file_path in list(self.managed_files):
            if self.cleanup_file(file_path):
                cleaned_count += 1
        return cleaned_count
    
    def __del__(self):
        """Cleanup on destruction"""
        self.cleanup_all()


class FileHasher:
    """Utility for generating file hashes"""
    
    @staticmethod
    def get_file_hash(file_path, algorithm='md5'):
        """Generate hash for a file"""
        hash_obj = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
    
    @staticmethod
    def compare_files(file1, file2):
        """Compare two files using hash"""
        try:
            hash1 = FileHasher.get_file_hash(file1)
            hash2 = FileHasher.get_file_hash(file2)
            return hash1 == hash2
        except Exception:
            return False


class ConversionStats:
    """Track conversion statistics"""
    
    def __init__(self):
        self.stats = {
            'total_conversions': 0,
            'successful_conversions': 0,
            'failed_conversions': 0,
            'conversion_types': {},
            'file_types': {},
            'total_size_processed': 0
        }
    
    def record_conversion_start(self, file_path, file_type, conversion_type):
        """Record the start of a conversion"""
        self.stats['total_conversions'] += 1
        
        # Update conversion type stats
        if conversion_type not in self.stats['conversion_types']:
            self.stats['conversion_types'][conversion_type] = {'count': 0, 'success': 0}
        self.stats['conversion_types'][conversion_type]['count'] += 1
        
        # Update file type stats
        if file_type not in self.stats['file_types']:
            self.stats['file_types'][file_type] = {'count': 0, 'success': 0}
        self.stats['file_types'][file_type]['count'] += 1
        
        # Add file size
        if os.path.exists(file_path):
            self.stats['total_size_processed'] += os.path.getsize(file_path)
    
    def record_conversion_success(self, conversion_type, file_type):
        """Record a successful conversion"""
        self.stats['successful_conversions'] += 1
        self.stats['conversion_types'][conversion_type]['success'] += 1
        self.stats['file_types'][file_type]['success'] += 1
    
    def record_conversion_failure(self):
        """Record a failed conversion"""
        self.stats['failed_conversions'] += 1
    
    def get_success_rate(self):
        """Get overall success rate"""
        if self.stats['total_conversions'] == 0:
            return 0
        return (self.stats['successful_conversions'] / self.stats['total_conversions']) * 100
    
    def get_stats_summary(self):
        """Get summary of statistics"""
        return {
            'total_conversions': self.stats['total_conversions'],
            'success_rate': f"{self.get_success_rate():.1f}%",
            'total_size_processed': self._format_size(self.stats['total_size_processed']),
            'most_popular_conversion': self._get_most_popular_conversion(),
            'most_processed_file_type': self._get_most_processed_file_type()
        }
    
    def _format_size(self, size_bytes):
        """Format size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def _get_most_popular_conversion(self):
        """Get most popular conversion type"""
        if not self.stats['conversion_types']:
            return 'None'
        
        most_popular = max(
            self.stats['conversion_types'].items(),
            key=lambda x: x[1]['count']
        )
        return most_popular[0]
    
    def _get_most_processed_file_type(self):
        """Get most processed file type"""
        if not self.stats['file_types']:
            return 'None'
        
        most_processed = max(
            self.stats['file_types'].items(),
            key=lambda x: x[1]['count']
        )
        return most_processed[0]


# Global instances
temp_manager = TempFileManager()
conversion_logger = ConversionLogger()
conversion_stats = ConversionStats()