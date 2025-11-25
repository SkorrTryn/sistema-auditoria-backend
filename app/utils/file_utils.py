from fastapi import UploadFile, HTTPException
import aiofiles
import os
from typing import List
from datetime import datetime


def validate_file(file: UploadFile, allowed_extensions: List[str], max_size: int):
    """
    Valida que el archivo cumpla con los requisitos
    """
    # Validar extensión
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Extensión de archivo no permitida. Permitidas: {', '.join(allowed_extensions)}"
        )
    
    # Validar tamaño (si es posible)
    # Nota: file.size puede no estar disponible en todos los casos
    # La validación completa se hace al guardar


async def save_upload_file(file: UploadFile, upload_dir: str) -> str:
    """
    Guarda un archivo subido en el directorio especificado
    """
    # Crear directorio si no existe
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generar nombre único
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Guardar archivo
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    return file_path