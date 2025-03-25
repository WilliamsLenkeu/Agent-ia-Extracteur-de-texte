import time
from fastapi import APIRouter, File, UploadFile, HTTPException
from io import BytesIO
from app.services.file_processing import TextExtractor
import logging
from typing import Dict, Any

router = APIRouter()
logger = logging.getLogger(__name__)

ALLOWED_TYPES = {
    'pdf': 'application/pdf',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png'
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

async def validate_file(file: UploadFile) -> BytesIO:
    """Valide et prépare le fichier pour traitement"""
    if file.content_type not in ALLOWED_TYPES.values():
        raise HTTPException(
            status_code=400,
            detail=f"Type non supporté. Types valides: {list(ALLOWED_TYPES.keys())}"
        )

    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Fichier trop volumineux (> {MAX_FILE_SIZE//(1024*1024)}MB)"
        )

    return BytesIO(file_content)

@router.post("/extract-text", response_model=Dict[str, Any])
async def extract_text(file: UploadFile = File(...)):
    """Endpoint principal pour l'extraction de texte"""
    try:
        logger.info(f"Début traitement fichier {file.filename}")
        start_time = time.time()
        
        # Validation du fichier
        file_bytes = await validate_file(file)
        
        # Détection du type de contenu
        content_type = file.content_type
        logger.debug(f"Type détecté: {content_type}")
        
        # Extraction basée sur le type
        result = {
            "text": "",
            "ocr_used": False,
            "file_type": content_type,
            "status": "success"
        }

        try:
            if content_type == ALLOWED_TYPES['pdf']:
                result["text"], result["ocr_used"] = TextExtractor.extract_from_pdf(file_bytes)
            elif content_type in {ALLOWED_TYPES['jpg'], ALLOWED_TYPES['jpeg'], ALLOWED_TYPES['png']}:
                result["text"] = TextExtractor.extract_from_image(file_bytes)
                result["ocr_used"] = True
            else:  # DOCX
                result["text"], _ = TextExtractor.extract_from_word(file_bytes)
        except HTTPException as he:
            result["status"] = "error"
            result["error"] = str(he.detail)
            raise he

        # Vérification du résultat
        if not result["text"].strip():
            raise HTTPException(
                status_code=422,
                detail="Aucun texte valide n'a pu être extrait"
            )

        result["processing_time"] = round(time.time() - start_time, 2)
        logger.info(f"Traitement réussi en {result['processing_time']}s")
        return result

    except HTTPException as he:
        logger.warning(f"Erreur de traitement: {str(he.detail)}")
        raise
    except Exception as e:
        logger.error(f"Erreur interne: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Une erreur interne est survenue"
        )