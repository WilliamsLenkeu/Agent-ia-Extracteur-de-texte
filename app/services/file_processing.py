import logging
from io import BytesIO
from typing import Tuple, List, Optional
from fastapi import HTTPException
from PIL import Image
import pytesseract
import fitz  # PyMuPDF
from docx import Document
import numpy as np
import cv2
import concurrent.futures
from functools import partial

# Vérifie que Tesseract est accessible
# try:
#     pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
#     pytesseract.get_tesseract_version()
# except Exception as e:
#     raise RuntimeError(f"Tesseract non installé : {str(e)}")

logger = logging.getLogger(__name__)

class TextExtractor:
    # Configuration optimisée
    OCR_CONFIG = r'--oem 1 --psm 6 -l fra+eng'  # OCR rapide
    PDF_DPI = 200  # Résolution réduite
    MAX_PAGE_SIZE = 1600  # Taille max en pixels
    PAGE_TIMEOUT = 20  # Secondes par page
    MAX_WORKERS = 4  # Threads parallèles

    @staticmethod
    def enhance_image(image: Image) -> Image:
        """Amélioration d'image optimisée pour l'OCR"""
        try:
            # Conversion en niveaux de gris
            img_array = np.array(image.convert('L'))
            
            # CLAHE - Amélioration de contraste
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            img_array = clahe.apply(img_array)
            
            # Seuillage adaptatif
            img_array = cv2.adaptiveThreshold(
                img_array, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )
            
            return Image.fromarray(img_array)
        except Exception as e:
            logger.warning(f"Échec prétraitement: {str(e)}")
            return image

    @staticmethod
    def process_page(page, page_num: int) -> Optional[str]:
        """Traite une page avec timeout"""
        try:
            # Essai extraction texte standard
            text = page.get_text("text").strip()
            if text:
                return text

            # Fallback OCR pour page scannée
            pix = page.get_pixmap(dpi=TextExtractor.PDF_DPI)
            
            # Réduction de taille si nécessaire
            if max(pix.width, pix.height) > TextExtractor.MAX_PAGE_SIZE:
                scale = TextExtractor.MAX_PAGE_SIZE / max(pix.width, pix.height)
                pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale))
            
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            processed_img = TextExtractor.enhance_image(img)
            
            return pytesseract.image_to_string(
                processed_img,
                config=TextExtractor.OCR_CONFIG
            ).strip()
            
        except Exception as e:
            logger.warning(f"Erreur page {page_num}: {str(e)}")
            return None

    @staticmethod
    def extract_from_pdf(file: BytesIO) -> Tuple[str, bool]:
        """Extraction PDF parallélisée"""
        try:
            file.seek(0)
            doc = fitz.open(stream=file.read(), filetype="pdf")
            text_parts = []
            ocr_used = False
            
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=TextExtractor.MAX_WORKERS
            ) as executor:
                futures = {
                    executor.submit(
                        TextExtractor.process_page,
                        page,
                        num
                    ): num for num, page in enumerate(doc)
                }
                
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    if result:
                        text_parts.append(result)
                        if futures[future] > 0:  # Vérifie si OCR utilisé
                            ocr_used = True

            return "\n".join(text_parts), ocr_used
            
        except Exception as e:
            logger.error(f"Erreur PDF: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=422,
                detail="Erreur d'extraction PDF"
            )

    @staticmethod
    def extract_from_image(file: BytesIO) -> str:
        """Extraction depuis image avec gestion d'erreur"""
        try:
            file.seek(0)
            image = Image.open(file)
            
            if image.mode not in ('L', 'RGB'):
                image = image.convert('RGB')
            
            processed_img = TextExtractor.enhance_image(image)
            text = pytesseract.image_to_string(
                processed_img,
                config=TextExtractor.OCR_CONFIG
            )
            return text.strip()
        except Exception as e:
            logger.error(f"Erreur image: {str(e)}")
            raise HTTPException(
                status_code=422,
                detail="Échec reconnaissance texte"
            )

    @staticmethod
    def extract_from_word(file: BytesIO) -> Tuple[str, bool]:
        """Extraction depuis Word"""
        try:
            doc = Document(file)
            text = "\n".join(
                p.text for p in doc.paragraphs if p.text.strip()
            )
            return text.strip(), False
        except Exception as e:
            logger.error(f"Erreur Word: {str(e)}")
            raise HTTPException(
                status_code=422,
                detail="Échec extraction Word"
            )