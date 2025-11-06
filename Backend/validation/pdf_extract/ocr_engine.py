import fitz  # PyMuPDF
import pytesseract
import cv2
import numpy as np
from PIL import Image, ImageEnhance
import re
from concurrent.futures import ThreadPoolExecutor

# Initialize spell checker (make it optional)
try:
    from spellchecker import SpellChecker
    SPELL_CHECK_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    SPELL_CHECK_AVAILABLE = False
    print("Warning: spellchecker module not available. Spell checking will be disabled.")

class DummySpellChecker:
    """Dummy spell checker that does nothing when the real one is not available"""
    def correction(self, word):
        return word

# Initialize spell checker or dummy
spell = SpellChecker() if SPELL_CHECK_AVAILABLE else DummySpellChecker()

def deskew(image):
    """Correct image skew/slant"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)
    coords = np.column_stack(np.where(gray > 0))
    angle = cv2.minAreaRect(coords)[-1]
    
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
        
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

def enhance_image(image):
    """Enhance image quality for better OCR results"""
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    # Apply bilateral filter to reduce noise while preserving edges
    denoised = cv2.bilateralFilter(enhanced, 9, 75, 75)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        denoised, 255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    
    # Apply dilation to make text more solid
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    dilated = cv2.dilate(thresh, kernel, iterations=1)
    
    return dilated

def preprocess_image(pil_img):
    """Apply all preprocessing steps"""
    img = np.array(pil_img.convert('RGB'))
    
    # Deskew the image
    deskewed = deskew(img)
    
    # Enhance the image
    enhanced = enhance_image(deskewed)
    
    # Convert back to PIL Image
    return Image.fromarray(enhanced)

def correct_spelling(text):
    """Basic spell checking and correction"""
    words = text.split()
    corrected_words = []
    
    for word in words:
        # Skip if it's a number or contains special characters
        if word.isdigit() or not word.isalnum():
            corrected_words.append(word)
            continue
            
        # Get the most likely correction
        corrected = spell.correction(word)
        if corrected is not None and corrected != word:
            corrected_words.append(corrected)
        else:
            corrected_words.append(word)
            
    return ' '.join(corrected_words)

def ocr_image(pil_img):
    """Perform OCR with multiple configurations and combine results"""
    # Convert to OpenCV format
    img_cv = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    
    # Try different preprocessing methods
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    
    # Method 1: Otsu's thresholding
    _, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Method 2: Adaptive thresholding
    thresh2 = cv2.adaptiveThreshold(
        gray, 255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    
    # Method 3: Gaussian blur + Otsu's thresholding
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh3 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Convert back to PIL for Tesseract
    images = [
        (Image.fromarray(cv2.cvtColor(thresh1, cv2.COLOR_GRAY2RGB)), "Otsu"),
        (Image.fromarray(cv2.cvtColor(thresh2, cv2.COLOR_GRAY2RGB)), "Adaptive"),
        (Image.fromarray(cv2.cvtColor(thresh3, cv2.COLOR_GRAY2RGB)), "Gaussian+Otsu"),
        (pil_img, "Default")  # Try original as last resort
    ]
    
    results = []
    for img, method in images:
        # Try different Tesseract configurations
        configs = [
            ('--psm 6 -l eng+handwritten --oem 1', 'Handwritten Text'),
            ('--psm 11 -l eng+handwritten --oem 1', 'Sparse Text with OSD'),
            ('--psm 4 -l eng+handwritten --oem 1', 'Single Column'),
            ('--psm 6 -l eng --oem 1', 'Printed Text'),
            ('--psm 11 -l eng --oem 1', 'Printed Text with OSD')
        ]
        
        for config, config_name in configs:
            try:
                # Use Tesseract with the current configuration
                text = pytesseract.image_to_string(img, config=config)
                
                # Get confidence scores
                data = pytesseract.image_to_data(img, config=custom_config, 
                                               output_type=pytesseract.Output.DICT)
                confs = [int(c) for c in data['conf'] if c != '-1']
                avg_conf = sum(confs) / len(confs) if confs else 0
                
                results.append({
                    'text': text.strip(),
                    'confidence': avg_conf,
                    'method': f"{method} + {config_name}"
                })
            except Exception as e:
                print(f"Error with {method} + {config_name}: {str(e)}")
    
    # Sort by confidence and return the best result
    if results:
        best_result = max(results, key=lambda x: x['confidence'])
        return best_result['text'], best_result['confidence'], best_result['method']
    
    return "", 0, "No results"

def process_page(page):
    """Process a single page in parallel"""
    pix = page.get_pixmap(dpi=300)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    img = preprocess_image(img)
    text, conf, method = ocr_image(img)
    return text, conf, method

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF with improved parallel processing"""
    doc = fitz.open(pdf_path)
    full_text = []
    ocr_scores = []
    methods_used = set()
    
    # Process pages in parallel
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(process_page, [doc.load_page(i) for i in range(len(doc))]))
    
    for text, conf, method in results:
        full_text.append(text)
        ocr_scores.append(conf)
        methods_used.add(method)
    
    # Combine all text with page separators
    full_text = "\n\n--- PAGE BREAK ---\n\n".join(full_text)
    
    meta = {
        "pages": len(doc),
        "avg_confidence": round(sum(ocr_scores) / len(ocr_scores), 2) if ocr_scores else 0,
        "methods_used": list(methods_used)
    }
    
    return full_text, meta

def clean_ocr_text(text):
    """Clean and post-process OCR text"""
    # Remove excessive whitespace
    text = ' '.join(text.split())
    
    # Fix common OCR mistakes
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Add space between lower and uppercase
    text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)  # Ensure space after sentence endings
    
    # Split into lines and clean each line
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if line:  # Skip empty lines
            # Basic spell checking
            line = correct_spelling(line)
            lines.append(line)
    
    # Join lines with proper spacing
    return '\n'.join(lines)
