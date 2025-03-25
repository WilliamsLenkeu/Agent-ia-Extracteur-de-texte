import logging
from io import BytesIO
from typing import Tuple
from fastapi import HTTPException
from PIL import Image, ImageEnhance, ImageOps
import pytesseract
import fitz  # PyMuPDF
from docx import Document
import numpy as np
import cv2

# Configuration du logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class TextExtractor:
    @staticmethod
    def enhance_image(image: Image) -> Image:
        """Améliore la qualité de l'image pour l'OCR avec prétraitement avancé"""
        try:
            logger.debug("Début du prétraitement d'image")
            
            # Conversion en numpy array
            img_array = np.array(image.convert('L'))
            
            # Égalisation d'histogramme adaptative (CLAHE)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            img_array = clahe.apply(img_array)
            
            # Détection des bords
            img_array = cv2.adaptiveThreshold(img_array, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY, 11, 2)
            
            # Reconversion en Image PIL
            enhanced_img = Image.fromarray(img_array)
            logger.debug("Prétraitement d'image réussi")
            return enhanced_img
        except Exception as e:
            logger.error(f"Erreur de prétraitement d'image: {str(e)}")
            return image

    @staticmethod
    def extract_from_image(file: BytesIO) -> str:
        """Extrait le texte d'une image avec gestion robuste"""
        try:
            logger.debug("Début d'extraction depuis une image")
            file.seek(0)
            image = Image.open(file)
            
            # Conversion forcée en mode compatible
            if image.mode not in ('L', 'RGB'):
                image = image.convert('RGB')
            
            enhanced = TextExtractor.enhance_image(image)
            
            # Configuration OCR optimisée
            custom_config = r'--oem 3 --psm 6 -l fra+eng'
            text = pytesseract.image_to_string(enhanced, config=custom_config)
            
            logger.debug(f"Texte extrait ({len(text)} caractères)")
            return text.strip()
        except Exception as e:
            logger.error(f"Échec OCR: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=422,
                detail="Échec de la reconnaissance de texte dans l'image"
            )

    @staticmethod
    def extract_from_pdf(file: BytesIO) -> Tuple[str, bool]:
        """Extrait le texte d'un PDF avec gestion des pages scannées"""
        try:
            logger.debug("Début d'extraction depuis PDF")
            file.seek(0)
            doc = fitz.open(stream=file.read(), filetype="pdf")
            text = ""
            ocr_used = False

            for page in doc:
                # Essai d'extraction texte normal
                page_text = page.get_text("text")
                if page_text.strip():
                    text += page_text + "\n"
                    continue
                
                # Fallback OCR pour page scannée
                logger.debug(f"OCR nécessaire pour la page {page.number}")
                try:
                    pix = page.get_pixmap(dpi=300)
                    img_bytes = pix.tobytes("ppm")
                    
                    with BytesIO(img_bytes) as img_buffer:
                        ocr_text = TextExtractor.extract_from_image(img_buffer)
                        if ocr_text:
                            text += ocr_text + "\n"
                            ocr_used = True
                except Exception as ocr_error:
                    logger.warning(f"Échec OCR page {page.number}: {str(ocr_error)}")
                    continue

            logger.debug(f"Extraction PDF terminée - OCR utilisé: {ocr_used}")
            return text.strip(), ocr_used
        except Exception as e:
            logger.error(f"Erreur PDF: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=422,
                detail="Échec de l'extraction du document PDF"
            )

    @staticmethod
    def extract_from_word(file: BytesIO) -> Tuple[str, bool]:
        """Extrait le texte d'un document Word"""
        try:
            logger.debug("Début d'extraction depuis Word")
            doc = Document(file)
            text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
            logger.debug(f"Texte extrait ({len(text)} caractères)")
            return text.strip(), False
        except Exception as e:
            logger.error(f"Erreur Word: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=422,
                detail="Échec de l'extraction du document Word"
            )