from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.checklist_processor import ChecklistProcessor
from app.config import settings
from app.utils.file_utils import validate_file, save_upload_file
import os

router = APIRouter(prefix="/checklist", tags=["Checklist"])


@router.post("/upload")
async def upload_checklist(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Sube y procesa un archivo de checklist en Excel
    """
    # Validar archivo
    validate_file(file, settings.allowed_extensions_list, settings.MAX_FILE_SIZE)
    
    # Guardar archivo
    file_path = await save_upload_file(file, settings.UPLOAD_DIR)
    
    try:
        # Procesar checklist
        processor = ChecklistProcessor(db)
        audit = processor.process_checklist(file_path, file.filename)
        
        return {
            "message": "Checklist procesado exitosamente",
            "audit_id": audit.id,
            "total_items": audit.total_items
        }
    
    except Exception as e:
        # Eliminar archivo si hay error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error procesando checklist: {str(e)}")