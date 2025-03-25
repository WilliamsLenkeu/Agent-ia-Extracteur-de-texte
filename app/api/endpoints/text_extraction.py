import time
from fastapi import APIRouter, File, UploadFile, HTTPException
from io import BytesIO
from app.services.file_processing import TextExtractor
import logging
from typing import Dict, Any
import concurrent.futures

router = APIRouter()
logger = logging.getLogger(__name__)

# Configuration
ALLOWED_TYPES = {
    'pdf': 'application/pdf',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png'
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
PROCESS_TIMEOUT = 120  # 2 minutes

async def validate_file(file: UploadFile) -> BytesIO:
    """Validation du fichier"""
    if file.content_type not in ALLOWED_TYPES.values():
        raise HTTPException(
            status_code=400,
            detail=f"Type non supporté. Formats: {list(ALLOWED_TYPES.keys())}"
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Taille max dépassée ({MAX_FILE_SIZE//(1024*1024)}MB)"
        )
    return BytesIO(content)

def process_content(content: bytes, content_type: str) -> Dict[str, Any]:
    """Traitement synchrone pour le thread pool"""
    result = {
        "text": "",
        "ocr_used": False,
        "file_type": content_type,
        "status": "success"
    }
    
    try:
        file_bytes = BytesIO(content)
        
        if content_type == ALLOWED_TYPES['pdf']:
            result["text"], result["ocr_used"] = TextExtractor.extract_from_pdf(file_bytes)
        elif content_type in {ALLOWED_TYPES['jpg'], ALLOWED_TYPES['jpeg'], ALLOWED_TYPES['png']}:
            result["text"] = TextExtractor.extract_from_image(file_bytes)
            result["ocr_used"] = True
        else:  # DOCX
            result["text"], _ = TextExtractor.extract_from_word(file_bytes)

        if not result["text"].strip():
            raise HTTPException(
                status_code=422,
                detail="Aucun texte détecté"
            )
            
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur traitement: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erreur de traitement"
        )

@router.post("/extract-text", response_model=Dict[str, Any])
async def extract_text(file: UploadFile = File(...)):
    """Endpoint principal avec timeout"""
    try:
        logger.info(f"Début traitement: {file.filename}")
        start_time = time.time()
        
        # Validation
        file_bytes = await validate_file(file)
        
        # Traitement avec timeout
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(
                process_content,
                file_bytes.getvalue(),
                file.content_type
            )
            result = future.result(timeout=PROCESS_TIMEOUT)
        
        result["processing_time"] = round(time.time() - start_time, 2)
        logger.info(f"Traitement réussi en {result['processing_time']}s")
        return result

    except concurrent.futures.TimeoutError:
        logger.error("Timeout du traitement")
        raise HTTPException(
            status_code=504,
            detail="Traitement trop long"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur inattendue: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Erreur interne"
        )