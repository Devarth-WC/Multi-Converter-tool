# Multi-Format Converter

A comprehensive Python Flask web application that enables users to convert files across various formats including PDFs, documents, images, and audio files. This universal file conversion platform brings together multiple conversion capabilities in one user-friendly interface.

## 🌟 Features

### Universal Accessibility
- **Text-to-Speech**: Convert PDF and text documents to audio for visually impaired users
- **Speech-to-Text**: Convert audio recordings to readable text
- **OCR (Optical Character Recognition)**: Extract text from images for better accessibility

### Document Conversions
- PDF to DOCX, TXT, or Audio (Text-to-Speech)
- DOCX to TXT and vice versa
- Text to Audio with multiple TTS engines (Google TTS, System TTS)

### Image Processing
- **OCR**: Extract text from images (JPG, PNG, GIF, BMP, TIFF)
- **Format Conversion**: Convert between JPG, PNG, GIF, BMP, TIFF
- **Image Manipulation**: Resize, compress, rotate, apply filters
- **PDF Creation**: Convert images to PDF documents
- **Batch Processing**: Create collages from multiple images

### Audio Processing
- **Speech Recognition**: Convert speech in audio files to text
- **Format Conversion**: Convert between MP3, WAV, OGG, FLAC, AAC
- **Audio Enhancement**: Normalize, compress, trim audio files
- **Speed Control**: Change audio playback speed
- **Video Processing**: Extract audio from video files

### Advanced Features
- Drag-and-drop file upload interface
- Real-time conversion progress tracking
- File validation and security checks
- Automatic cleanup of temporary files
- Conversion statistics and logging
- Support for multiple languages (OCR and TTS)

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- ffmpeg (for audio/video processing)
- Tesseract OCR engine

### System Dependencies

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-eng ffmpeg libsm6 libxext6 libxrender-dev libglib2.0-0
```

#### macOS:
```bash
brew install tesseract ffmpeg
```

#### Windows:
1. Install Tesseract from: https://github.com/tesseract-ocr/tesseract/wiki
2. Install ffmpeg from: https://ffmpeg.org/download.html
3. Add both to your system PATH

### Python Setup

1. **Clone the repository:**
```bash
git clone <repository-url>
cd Multi\ Format\ Converter
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\\Scripts\\activate   # Windows
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up directories:**
```bash
mkdir -p static/uploads downloads
```

## 🏃‍♂️ Running the Application

### Development Mode:
```bash
python app.py
```

### Production Mode:
```bash
gunicorn --bind 0.0.0.0:5000 app:app
```

Visit `http://localhost:5000` in your web browser.

## 📁 Project Structure

```
Multi Format Converter/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── test_converters.py     # Test suite
├── converters/
│   ├── __init__.py
│   ├── audio_converter.py # Audio processing
│   ├── image_converter.py # Image processing & OCR
│   ├── pdf_converter.py   # PDF processing
│   ├── text_converter.py  # Text & TTS processing
│   └── utils.py          # Utilities & validation
├── templates/
│   ├── base.html         # Base template
│   ├── index.html        # Landing page
│   ├── convert.html      # Main conversion interface
│   ├── result.html       # Conversion results
│   ├── 404.html         # Error pages
│   └── 500.html
├── static/
│   ├── css/
│   │   └── style.css     # Custom styles
│   ├── js/
│   │   └── main.js       # Client-side JavaScript
│   └── uploads/          # Temporary upload storage
└── downloads/            # Converted files storage
```

## 🔧 Configuration

### Environment Variables
```bash
export SECRET_KEY="your-secret-key-here"
export FLASK_ENV="production"  # or "development"
```

### Settings in `config.py`:
- `MAX_CONTENT_LENGTH`: Maximum file upload size (default: 200MB)
- `ALLOWED_EXTENSIONS`: Supported file types
- `TEMP_FILE_LIFETIME`: How long to keep temporary files
- `OCR_LANGUAGES`: Supported OCR languages
- `TTS_LANGUAGES`: Supported TTS languages

## 📋 Supported Formats

### Input Formats:
| Type | Extensions | Max Size |
|------|------------|----------|
| Documents | PDF, DOCX, TXT | 50MB |
| Images | JPG, PNG, GIF, BMP, TIFF | 20MB |
| Audio | MP3, WAV, OGG, FLAC, M4A, AAC | 100MB |
| Video | MP4, AVI, MOV | 200MB |

### Available Conversions:

#### Documents:
- PDF → DOCX, TXT, Audio (TTS)
- TXT ↔ DOCX
- Text → Audio (TTS)

#### Images:
- Image → PDF, Text (OCR)
- Format conversion between all supported types
- Resize, compress, rotate, apply filters
- Create collages from multiple images

#### Audio:
- Audio → Text (Speech Recognition)
- Format conversion between all supported types
- Compress, normalize, trim, change speed
- Extract audio from video files

## 🧪 Testing

Run the test suite to verify functionality:

```bash
python test_converters.py
```

This will check:
- All required dependencies
- Core conversion functionality
- Module loading and basic operations

## 🌍 Language Support

### OCR Languages:
English, Spanish, French, German, Italian, Portuguese, Russian, Chinese (Simplified), Japanese, Korean

### TTS Languages:
English, Spanish, French, German, Italian, Portuguese, Russian, Japanese, Korean, Chinese

## 🔒 Security Features

- File type validation
- File size limits
- Secure filename handling
- Automatic cleanup of temporary files
- Input sanitization
- CSRF protection

## 🚀 API Endpoints

### Main Endpoints:
- `GET /` - Home page
- `GET /convert` - Conversion interface
- `POST /convert` - Process file conversion
- `GET /download/<filename>` - Download converted file

### API Endpoints:
- `GET /api/supported_conversions` - Get supported conversion types
- `GET /api/stats` - Get conversion statistics
- `POST /api/file_info` - Get file information
- `GET /cleanup` - Admin endpoint for file cleanup

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and test thoroughly
4. Commit changes: `git commit -am 'Add feature'`
5. Push to branch: `git push origin feature-name`
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues:

1. **Tesseract not found:**
   - Install Tesseract OCR and add to PATH
   - Set `tesseract_cmd` path in image_converter.py if needed

2. **ffmpeg not available:**
   - Install ffmpeg and add to PATH
   - Audio/video conversions will be limited without ffmpeg

3. **Out of memory errors:**
   - Reduce file sizes
   - Adjust `MAX_CONTENT_LENGTH` in config.py

4. **TTS not working:**
   - Check internet connection for Google TTS
   - Fallback to offline pyttsx3 engine

### Performance Tips:
- Use SSD storage for better I/O performance
- Increase RAM for handling large files
- Configure nginx/apache for production deployment
- Use Redis for session storage in production

## 🌟 Project Impact

This Multi-Format Converter helps:

- **Students & Professionals**: Save time on document conversions
- **People with Disabilities**: Access content in preferred formats
- **Educators**: Create accessible learning materials
- **Content Creators**: Process media files efficiently
- **Organizations**: Standardize document formats

By providing a unified platform for file conversions, this tool eliminates the need for multiple specialized software applications and makes digital content more accessible to everyone.

---

**Built with ❤️ using Flask, Python, and modern web technologies.**