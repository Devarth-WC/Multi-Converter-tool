from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
import os
import uuid
import time
from datetime import datetime
from werkzeug.utils import secure_filename
from config import Config
from converters.pdf_converter import PDFConverter
from converters.audio_converter import AudioConverter
from converters.image_converter import ImageConverter
from converters.text_converter import TextConverter
from converters.utils import FileValidator, ConversionLogger, TempFileManager, conversion_stats

app = Flask(__name__)
app.config.from_object(Config)
Config.init_app(app)

logger = ConversionLogger()
temp_manager = TempFileManager()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_file_type(filename):
    """Determine file type category"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    return FileValidator.get_file_type(f'.{ext}')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['GET', 'POST'])
def convert():
    if request.method == 'GET':
        return render_template('convert.html')
    
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(request.url)
    
    file = request.files['file']
    conversion_type = request.form.get('conversion_type')
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(request.url)
    
    if not allowed_file(file.filename):
        flash('File type not supported', 'error')
        return redirect(request.url)
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Validate file
        is_valid, validation_message = FileValidator.is_valid_file(file_path)
        if not is_valid:
            os.remove(file_path)  # Clean up invalid file
            flash(f'File validation failed: {validation_message}', 'error')
            return redirect(url_for('convert'))
        
        # Determine conversion type and process
        input_type = get_file_type(filename)
        
        # Validate conversion type
        if not FileValidator.validate_conversion_type(input_type, conversion_type):
            os.remove(file_path)
            flash(f'Conversion type "{conversion_type}" not supported for {input_type} files', 'error')
            return redirect(url_for('convert'))
        
        # Log conversion start
        logger.log_conversion_start(filename, conversion_type)
        conversion_stats.record_conversion_start(file_path, input_type, conversion_type)
        
        # Perform conversion
        start_time = time.time()
        result = perform_conversion(file_path, input_type, conversion_type, unique_filename)
        conversion_time = time.time() - start_time
        
        if result['success']:
            logger.log_conversion_success(filename, result['filename'], conversion_type, conversion_time)
            conversion_stats.record_conversion_success(conversion_type, input_type)
            return render_template('result.html', 
                                 result=result, 
                                 original_filename=filename)
        else:
            logger.log_conversion_error(filename, conversion_type, result['error'])
            conversion_stats.record_conversion_failure()
            flash(f'Conversion failed: {result["error"]}', 'error')
            return redirect(url_for('convert'))
            
    except Exception as e:
        logger.log_conversion_error(filename if 'filename' in locals() else 'unknown', 
                                  conversion_type if 'conversion_type' in locals() else 'unknown', 
                                  str(e))
        conversion_stats.record_conversion_failure()
        flash(f'An unexpected error occurred: {str(e)}', 'error')
        return redirect(url_for('convert'))

def perform_conversion(file_path, input_type, conversion_type, unique_filename):
    """Perform the actual file conversion"""
    try:
        base_name = unique_filename.rsplit('.', 1)[0]
        output_path = None
        
        if input_type == 'pdf':
            converter = PDFConverter()
            if conversion_type == 'pdf_to_docx':
                output_path = converter.pdf_to_docx(file_path, 
                    os.path.join(app.config['DOWNLOAD_FOLDER'], f"{base_name}.docx"))
            elif conversion_type == 'pdf_to_audio':
                output_path = converter.pdf_to_audio(file_path, 
                    os.path.join(app.config['DOWNLOAD_FOLDER'], f"{base_name}.mp3"))
            elif conversion_type == 'pdf_to_txt':
                output_path = converter.pdf_to_txt(file_path, 
                    os.path.join(app.config['DOWNLOAD_FOLDER'], f"{base_name}.txt"))
        
        elif input_type == 'audio':
            converter = AudioConverter()
            if conversion_type == 'audio_to_text':
                output_path = converter.audio_to_text(file_path, 
                    os.path.join(app.config['DOWNLOAD_FOLDER'], f"{base_name}.txt"))
            elif conversion_type == 'audio_format':
                target_format = request.form.get('target_format', 'mp3')
                output_path = converter.convert_audio_format(file_path, 
                    os.path.join(app.config['DOWNLOAD_FOLDER'], f"{base_name}.{target_format}"))
            elif conversion_type == 'audio_compress':
                bitrate = request.form.get('bitrate', '64k')
                output_path = converter.compress_audio(file_path,
                    os.path.join(app.config['DOWNLOAD_FOLDER'], f"{base_name}_compressed.mp3"),
                    bitrate)
            elif conversion_type == 'audio_normalize':
                output_path = converter.normalize_audio(file_path,
                    os.path.join(app.config['DOWNLOAD_FOLDER'], f"{base_name}_normalized.mp3"))
            elif conversion_type == 'audio_trim':
                start_time = float(request.form.get('start_time', 0))
                end_time = request.form.get('end_time')
                end_time = float(end_time) if end_time else None
                output_path = converter.trim_audio(file_path,
                    os.path.join(app.config['DOWNLOAD_FOLDER'], f"{base_name}_trimmed.mp3"),
                    start_time, end_time)
            elif conversion_type == 'audio_speed':
                speed_factor = float(request.form.get('speed_factor', 1.0))
                output_path = converter.change_audio_speed(file_path,
                    os.path.join(app.config['DOWNLOAD_FOLDER'], f"{base_name}_speed.mp3"),
                    speed_factor)
        
        elif input_type == 'image':
            converter = ImageConverter()
            if conversion_type == 'image_to_pdf':
                output_path = converter.image_to_pdf(file_path, 
                    os.path.join(app.config['DOWNLOAD_FOLDER'], f"{base_name}.pdf"))
            elif conversion_type == 'image_to_text':
                output_path = converter.image_to_text(file_path, 
                    os.path.join(app.config['DOWNLOAD_FOLDER'], f"{base_name}.txt"))
            elif conversion_type == 'image_resize':
                width = int(request.form.get('width', 800))
                height = int(request.form.get('height', 600))
                maintain_aspect = request.form.get('maintain_aspect', 'true') == 'true'
                output_path = converter.resize_image(file_path, 
                    os.path.join(app.config['DOWNLOAD_FOLDER'], f"{base_name}_resized.jpg"),
                    (width, height), maintain_aspect)
            elif conversion_type == 'image_format':
                target_format = request.form.get('target_format', 'jpg')
                output_path = converter.convert_image_format(file_path,
                    os.path.join(app.config['DOWNLOAD_FOLDER'], f"{base_name}.{target_format}"))
            elif conversion_type == 'image_compress':
                quality = int(request.form.get('quality', 85))
                output_path = converter.compress_image(file_path,
                    os.path.join(app.config['DOWNLOAD_FOLDER'], f"{base_name}_compressed.jpg"),
                    quality)
            elif conversion_type == 'image_filter':
                filter_type = request.form.get('filter_type', 'enhance')
                output_path = converter.apply_image_filter(file_path,
                    os.path.join(app.config['DOWNLOAD_FOLDER'], f"{base_name}_filtered.jpg"),
                    filter_type)
            elif conversion_type == 'image_rotate':
                angle = int(request.form.get('rotate_angle', 90))
                output_path = converter.rotate_image(file_path,
                    os.path.join(app.config['DOWNLOAD_FOLDER'], f"{base_name}_rotated.jpg"),
                    angle)
        
        elif input_type == 'document':
            converter = TextConverter()
            if conversion_type == 'text_to_audio':
                engine = request.form.get('tts_engine', 'gtts')
                output_path = converter.text_to_audio(file_path, 
                    os.path.join(app.config['DOWNLOAD_FOLDER'], f"{base_name}.mp3"),
                    engine)
            elif conversion_type == 'txt_to_docx':
                output_path = converter.txt_to_docx(file_path,
                    os.path.join(app.config['DOWNLOAD_FOLDER'], f"{base_name}.docx"))
            elif conversion_type == 'docx_to_txt':
                output_path = converter.docx_to_txt(file_path,
                    os.path.join(app.config['DOWNLOAD_FOLDER'], f"{base_name}.txt"))
        
        elif input_type == 'video':
            converter = AudioConverter()  # Using AudioConverter for video to audio
            if conversion_type == 'video_to_audio':
                target_format = request.form.get('audio_format', 'mp3')
                output_path = converter.extract_audio_from_video(file_path,
                    os.path.join(app.config['DOWNLOAD_FOLDER'], f"{base_name}.{target_format}"))
        
        # Clean up uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)
        
        if output_path and os.path.exists(output_path):
            return {
                'success': True,
                'output_path': output_path,
                'filename': os.path.basename(output_path),
                'conversion_type': conversion_type,
                'file_size': os.path.getsize(output_path)
            }
        else:
            return {
                'success': False,
                'error': 'Conversion completed but output file not found'
            }
        
    except Exception as e:
        # Clean up uploaded file in case of error
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        
        return {
            'success': False,
            'error': str(e)
        }

@app.route('/download/<filename>')
def download_file(filename):
    """Download converted file"""
    file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        try:
            return send_file(file_path, as_attachment=True, download_name=filename)
        except Exception as e:
            flash(f'Download failed: {str(e)}', 'error')
            return redirect(url_for('index'))
    else:
        flash('File not found or has expired', 'error')
        return redirect(url_for('index'))

@app.route('/api/supported_conversions')
def supported_conversions():
    """API endpoint to get supported conversion types"""
    return jsonify({
        'pdf': FileValidator.get_supported_conversions('pdf'),
        'document': FileValidator.get_supported_conversions('document'),
        'image': FileValidator.get_supported_conversions('image'),
        'audio': FileValidator.get_supported_conversions('audio'),
        'video': FileValidator.get_supported_conversions('video')
    })
    
@app.route('/api/stats')
def conversion_statistics():
    """API endpoint to get conversion statistics"""
    return jsonify(conversion_stats.get_stats_summary())

@app.route('/api/file_info', methods=['POST'])
def get_file_info():
    """API endpoint to get file information"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Create temporary file to analyze
        temp_path = temp_manager.create_temp_file(suffix=f'.{file.filename.split(".")[-1]}')
        file.save(temp_path)
        
        # Get file info
        file_type = get_file_type(file.filename)
        is_valid, validation_message = FileValidator.is_valid_file(temp_path)
        file_size = os.path.getsize(temp_path)
        
        # Clean up temp file
        temp_manager.cleanup_file(temp_path)
        
        return jsonify({
            'filename': file.filename,
            'file_type': file_type,
            'file_size': file_size,
            'is_valid': is_valid,
            'validation_message': validation_message,
            'supported_conversions': FileValidator.get_supported_conversions(file_type)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/cleanup')
def cleanup_files():
    """Clean up old files (admin endpoint)"""
    try:
        cleaned_count = temp_manager.cleanup_old_files()
        
        # Also clean up old files in download folder
        download_folder = app.config['DOWNLOAD_FOLDER']
        cleaned_downloads = 0
        
        if os.path.exists(download_folder):
            current_time = datetime.now()
            for filename in os.listdir(download_folder):
                file_path = os.path.join(download_folder, filename)
                try:
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if current_time - file_time > app.config.get('TEMP_FILE_LIFETIME', 
                                                               temp_manager.max_age):
                        os.remove(file_path)
                        cleaned_downloads += 1
                except:
                    continue
        
        return jsonify({
            'success': True,
            'cleaned_temp_files': cleaned_count,
            'cleaned_downloads': cleaned_downloads,
            'total_cleaned': cleaned_count + cleaned_downloads
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

@app.errorhandler(413)
def too_large(error):
    flash('File too large. Maximum file size is 50MB.', 'error')
    return redirect(url_for('convert'))

# Context processor to add utility functions to templates
@app.context_processor
def utility_processor():
    def format_file_size(size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    return dict(format_file_size=format_file_size)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)