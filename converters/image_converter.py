import os
import tempfile
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import cv2
import numpy as np
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.utils import ImageReader
import img2pdf
import zipfile

class ImageConverter:
    def __init__(self):
        # Set tesseract path if needed (may need adjustment based on system)
        # pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
        pass
    
    def image_to_text(self, image_path, output_path):
        """Extract text from image using OCR (Optical Character Recognition)"""
        try:
            # Open and process image
            image = Image.open(image_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Enhance image for better OCR results
            image = self._enhance_image_for_ocr(image)
            
            # Perform OCR
            extracted_text = pytesseract.image_to_string(image)
            
            if not extracted_text.strip():
                extracted_text = "No text could be extracted from the image."
            
            # Save text to file
            with open(output_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(extracted_text)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Image to text conversion failed: {str(e)}")
    
    def _enhance_image_for_ocr(self, image):
        """Enhance image quality for better OCR results"""
        try:
            # Convert PIL image to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Convert to grayscale
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Apply denoising
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Apply threshold to get image with only black and white
            _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Convert back to PIL Image
            enhanced_image = Image.fromarray(thresh)
            
            return enhanced_image
            
        except Exception:
            # If enhancement fails, return original image
            return image
    
    def image_to_pdf(self, image_path, output_path):
        """Convert image to PDF"""
        try:
            # Method 1: Using img2pdf (preserves image quality better)
            try:
                with open(output_path, "wb") as pdf_file:
                    pdf_file.write(img2pdf.convert(image_path))
                return output_path
            except:
                # Method 2: Fallback using ReportLab
                self._image_to_pdf_reportlab(image_path, output_path)
                return output_path
            
        except Exception as e:
            raise Exception(f"Image to PDF conversion failed: {str(e)}")
    
    def _image_to_pdf_reportlab(self, image_path, output_path):
        """Convert image to PDF using ReportLab"""
        image = Image.open(image_path)
        
        # Create PDF with image
        c = canvas.Canvas(output_path, pagesize=A4)
        
        # Calculate dimensions to fit page
        img_width, img_height = image.size
        page_width, page_height = A4
        
        # Calculate scaling factor to fit image on page
        scale_w = page_width / img_width
        scale_h = page_height / img_height
        scale = min(scale_w, scale_h) * 0.8  # 80% of page size
        
        new_width = img_width * scale
        new_height = img_height * scale
        
        # Center the image
        x = (page_width - new_width) / 2
        y = (page_height - new_height) / 2
        
        c.drawImage(image_path, x, y, width=new_width, height=new_height)
        c.save()
    
    def resize_image(self, input_path, output_path, size=(800, 600), maintain_aspect=True):
        """Resize image to specified dimensions"""
        try:
            with Image.open(input_path) as image:
                if maintain_aspect:
                    # Calculate new size maintaining aspect ratio
                    image.thumbnail(size, Image.Resampling.LANCZOS)
                    resized_image = image
                else:
                    # Resize to exact dimensions
                    resized_image = image.resize(size, Image.Resampling.LANCZOS)
                
                # Save resized image
                resized_image.save(output_path, optimize=True, quality=95)
                
            return output_path
            
        except Exception as e:
            raise Exception(f"Image resizing failed: {str(e)}")
    
    def convert_image_format(self, input_path, output_path, target_format=None):
        """Convert image to different format"""
        try:
            if target_format is None:
                target_format = os.path.splitext(output_path)[1][1:].lower()
            
            # Normalize format names for PIL
            format_map = {
                'jpg': 'JPEG',
                'jpeg': 'JPEG',
                'png': 'PNG',
                'gif': 'GIF',
                'bmp': 'BMP',
                'tiff': 'TIFF',
                'tif': 'TIFF'
            }
            
            pil_format = format_map.get(target_format.lower(), target_format.upper())
            
            with Image.open(input_path) as image:
                # Convert RGBA to RGB for formats that don't support transparency
                if pil_format == 'JPEG' and image.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                    image = background
                
                # Save in target format
                image.save(output_path, format=pil_format, optimize=True, quality=95)
                
            return output_path
            
        except Exception as e:
            raise Exception(f"Image format conversion failed: {str(e)}")
    
    def compress_image(self, input_path, output_path, quality=85):
        """Compress image to reduce file size"""
        try:
            with Image.open(input_path) as image:
                # Convert RGBA to RGB if saving as JPEG
                if output_path.lower().endswith('.jpg') or output_path.lower().endswith('.jpeg'):
                    if image.mode in ('RGBA', 'LA'):
                        background = Image.new('RGB', image.size, (255, 255, 255))
                        background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                        image = background
                
                # Save with compression
                image.save(output_path, optimize=True, quality=quality)
                
            return output_path
            
        except Exception as e:
            raise Exception(f"Image compression failed: {str(e)}")
    
    def create_image_collage(self, image_paths, output_path, cols=2, spacing=10):
        """Create a collage from multiple images"""
        try:
            if not image_paths:
                raise Exception("No images provided for collage")
            
            # Load images
            images = [Image.open(path) for path in image_paths]
            
            # Calculate grid dimensions
            rows = (len(images) + cols - 1) // cols
            
            # Find maximum dimensions for uniform sizing
            max_width = max(img.width for img in images)
            max_height = max(img.height for img in images)
            
            # Create thumbnail size (make images uniform)
            thumb_size = (max_width // 2, max_height // 2)
            
            # Resize all images to thumbnail size
            for i, img in enumerate(images):
                img.thumbnail(thumb_size, Image.Resampling.LANCZOS)
                images[i] = img
            
            # Calculate collage dimensions
            collage_width = cols * thumb_size[0] + (cols + 1) * spacing
            collage_height = rows * thumb_size[1] + (rows + 1) * spacing
            
            # Create new image for collage
            collage = Image.new('RGB', (collage_width, collage_height), 'white')
            
            # Paste images into collage
            for i, img in enumerate(images):
                row = i // cols
                col = i % cols
                
                x = col * thumb_size[0] + (col + 1) * spacing
                y = row * thumb_size[1] + (row + 1) * spacing
                
                collage.paste(img, (x, y))
            
            # Save collage
            collage.save(output_path, quality=95)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Collage creation failed: {str(e)}")
    
    def apply_image_filter(self, input_path, output_path, filter_type='enhance'):
        """Apply filters to enhance image"""
        try:
            with Image.open(input_path) as image:
                if filter_type == 'enhance':
                    # Enhance sharpness and contrast
                    enhancer = ImageEnhance.Sharpness(image)
                    image = enhancer.enhance(1.2)
                    
                    enhancer = ImageEnhance.Contrast(image)
                    image = enhancer.enhance(1.1)
                    
                elif filter_type == 'blur':
                    image = image.filter(ImageFilter.BLUR)
                    
                elif filter_type == 'sharpen':
                    image = image.filter(ImageFilter.SHARPEN)
                    
                elif filter_type == 'smooth':
                    image = image.filter(ImageFilter.SMOOTH)
                    
                elif filter_type == 'grayscale':
                    image = image.convert('L')
                    
                # Save filtered image
                image.save(output_path, quality=95)
                
            return output_path
            
        except Exception as e:
            raise Exception(f"Image filter application failed: {str(e)}")
    
    def rotate_image(self, input_path, output_path, angle=90):
        """Rotate image by specified angle"""
        try:
            with Image.open(input_path) as image:
                # Rotate image
                rotated_image = image.rotate(angle, expand=True)
                
                # Save rotated image
                rotated_image.save(output_path, quality=95)
                
            return output_path
            
        except Exception as e:
            raise Exception(f"Image rotation failed: {str(e)}")
    
    def crop_image(self, input_path, output_path, crop_box=(0, 0, 100, 100)):
        """Crop image to specified area"""
        try:
            with Image.open(input_path) as image:
                # Crop image
                cropped_image = image.crop(crop_box)
                
                # Save cropped image
                cropped_image.save(output_path, quality=95)
                
            return output_path
            
        except Exception as e:
            raise Exception(f"Image cropping failed: {str(e)}")
    
    def create_image_zip(self, image_paths, output_path):
        """Create a ZIP file containing multiple images"""
        try:
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for image_path in image_paths:
                    if os.path.exists(image_path):
                        zip_file.write(image_path, os.path.basename(image_path))
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Image ZIP creation failed: {str(e)}")
    
    def get_image_info(self, image_path):
        """Get image information"""
        try:
            with Image.open(image_path) as image:
                return {
                    'format': image.format,
                    'mode': image.mode,
                    'width': image.width,
                    'height': image.height,
                    'has_transparency': image.mode in ('RGBA', 'LA') or 'transparency' in image.info,
                    'file_size': os.path.getsize(image_path)
                }
                
        except Exception as e:
            raise Exception(f"Failed to get image info: {str(e)}")
