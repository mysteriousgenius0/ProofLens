import cv2
import pytesseract
from PIL import Image
import numpy as np
import io
import logging
from typing import Tuple, Dict, List

logger = logging.getLogger(__name__)

class ImageAnalyzer:
    """Analyzes images for text extraction and visual red flags"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_text(self, file) -> str:
        """
        Extract text from image using OCR
        
        Args:
            file: Flask file object
            
        Returns:
            Extracted text string
        """
        try:
            # Read image
            img = Image.open(file.stream)
            file.stream.seek(0)  # Reset stream
            
            # Preprocess image for better OCR
            img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            
            # Apply image enhancement
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            
            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            
            # Denoise
            denoised = cv2.fastNlMeansDenoising(enhanced)
            
            # Extract text
            text = pytesseract.image_to_string(denoised)
            
            self.logger.info(f"Extracted {len(text)} characters from image")
            return text.strip()
        
        except Exception as e:
            self.logger.error(f"Error extracting text: {str(e)}")
            return ""
    
    def detect_visual_red_flags(self, file) -> Dict:
        """
        Detect visual red flags in image
        
        Args:
            file: Flask file object
            
        Returns:
            Dictionary of detected red flags
        """
        try:
            img = Image.open(file.stream)
            file.stream.seek(0)
            
            img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            
            red_flags = {
                'blurry': self._is_blurry(img_cv),
                'low_resolution': self._is_low_resolution(img_cv),
                'suspicious_fonts': self._detect_suspicious_fonts(img),
                'watermark_absence': not self._has_watermark(img_cv),
                'pixelation_detected': self._detect_pixelation(img_cv),
                'inconsistent_branding': self._detect_branding_inconsistencies(img_cv),
                'quality_score': self._calculate_image_quality(img_cv)
            }
            
            self.logger.info(f"Visual analysis complete: {red_flags}")
            return red_flags
        
        except Exception as e:
            self.logger.error(f"Error detecting visual red flags: {str(e)}")
            return {}
    
    def _is_blurry(self, img) -> bool:
        """Detect if image is blurry using Laplacian variance"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Threshold for blur detection (lower = blurrier)
        is_blurry = laplacian_var < 100
        self.logger.debug(f"Blur detection - Laplacian variance: {laplacian_var}, Blurry: {is_blurry}")
        return is_blurry
    
    def _is_low_resolution(self, img) -> bool:
        """Check if image resolution is suspiciously low"""
        height, width = img.shape[:2]
        is_low_res = width < 400 or height < 300
        self.logger.debug(f"Resolution check - {width}x{height}, Low res: {is_low_res}")
        return is_low_res
    
    def _detect_suspicious_fonts(self, img) -> bool:
        """Detect suspicious or poorly rendered fonts"""
        # This is a placeholder for more advanced font analysis
        # In production, you might use more sophisticated methods
        try:
            img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            # Detect edges to analyze text rendering quality
            edges = cv2.Canny(img_cv, 100, 200)
            edge_ratio = np.sum(edges > 0) / edges.size
            
            # High edge ratio might indicate poor font rendering
            suspicious = edge_ratio > 0.3
            self.logger.debug(f"Suspicious fonts check - Edge ratio: {edge_ratio}")
            return suspicious
        except:
            return False
    
    def _has_watermark(self, img) -> bool:
        """Check if image has watermarks or official branding"""
        # Look for semi-transparent overlays
        if img.shape[2] == 4:  # Has alpha channel
            return True
        
        # Check for uniform regions (watermark indicators)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # This is simplified; production version would be more sophisticated
        return False
    
    def _detect_pixelation(self, img) -> bool:
        """Detect pixelation or compression artifacts"""
        # Analyze compression artifacts
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply Fourier transform
        f_transform = np.fft.fft2(gray)
        f_shift = np.fft.fftshift(f_transform)
        magnitude = np.abs(f_shift)
        
        # High frequency content analysis
        high_freq_ratio = np.sum(magnitude > np.median(magnitude)) / magnitude.size
        
        is_pixelated = high_freq_ratio < 0.1  # Low high-frequency content = pixelated
        self.logger.debug(f"Pixelation check - High freq ratio: {high_freq_ratio}")
        return is_pixelated
    
    def _detect_branding_inconsistencies(self, img) -> bool:
        """Detect inconsistent or fake branding"""
        # This is a simplified check; production version would compare against known logos
        return False
    
    def _calculate_image_quality(self, img) -> float:
        """Calculate overall image quality score (0-100)"""
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Sharpness score
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            sharpness = laplacian.var()
            sharpness_score = min(100, (sharpness / 200) * 100)
            
            # Brightness score (not too dark, not too bright)
            brightness = np.mean(gray)
            brightness_score = 100 if 50 < brightness < 200 else 50
            
            # Contrast score
            contrast = gray.std()
            contrast_score = min(100, (contrast / 100) * 100)
            
            # Overall score
            quality_score = (sharpness_score + brightness_score + contrast_score) / 3
            
            self.logger.debug(f"Quality score: {quality_score} (Sharpness: {sharpness_score}, Brightness: {brightness_score}, Contrast: {contrast_score})")
            return round(quality_score, 2)
        
        except Exception as e:
            self.logger.error(f"Error calculating quality: {str(e)}")
            return 50.0
