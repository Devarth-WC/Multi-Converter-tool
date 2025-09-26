import fitz  # PyMuPDF
import pdfplumber
from docx import Document
from gtts import gTTS
import os
import tempfile

class PDFConverter:
    def __init__(self):
        pass
    
    def pdf_to_txt(self, pdf_path, output_path):
        """Convert PDF to plain text"""
        try:
            text_content = ""
            
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + "\n\n"
            
            with open(output_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(text_content)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"PDF to TXT conversion failed: {str(e)}")
    
    def pdf_to_docx(self, pdf_path, output_path):
        """Convert PDF to DOCX"""
        try:
            # Extract text from PDF
            text_content = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + "\n\n"
            
            # Create DOCX document
            doc = Document()
            
            # Split text into paragraphs and add to document
            paragraphs = text_content.split('\n\n')
            for paragraph in paragraphs:
                if paragraph.strip():
                    doc.add_paragraph(paragraph.strip())
            
            doc.save(output_path)
            return output_path
            
        except Exception as e:
            raise Exception(f"PDF to DOCX conversion failed: {str(e)}")
    
    def pdf_to_audio(self, pdf_path, output_path):
        """Convert PDF to audio using text-to-speech"""
        try:
            # Extract text from PDF
            text_content = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + " "
            
            if not text_content.strip():
                raise Exception("No text found in PDF")
            
            # Limit text length for gTTS (max ~5000 characters per request)
            if len(text_content) > 4500:
                text_content = text_content[:4500] + "..."
            
            # Convert to speech
            tts = gTTS(text=text_content, lang='en', slow=False)
            tts.save(output_path)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"PDF to Audio conversion failed: {str(e)}")
    
    def extract_images_from_pdf(self, pdf_path, output_dir):
        """Extract images from PDF"""
        try:
            doc = fitz.open(pdf_path)
            image_paths = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    
                    if pix.n - pix.alpha < 4:  # GRAY or RGB
                        img_path = os.path.join(output_dir, f"image_p{page_num}_{img_index}.png")
                        pix.save(img_path)
                        image_paths.append(img_path)
                    
                    pix = None
            
            doc.close()
            return image_paths
            
        except Exception as e:
            raise Exception(f"Image extraction failed: {str(e)}")