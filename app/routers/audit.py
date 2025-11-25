from fastapi import APIRouter, HTTPException, Depends, Body
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.audit import Audit, AuditResult
from app.schemas.audit import AuditStatusResponse, AuditHistoryResponse, AuditResponse
from app.services.report_generator import ReportGenerator
from app.routers.auth import get_google_drive_service
from typing import List
import os
import json

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.post("/start")
async def start_audit(audit_id: int = Body(..., embed=True), db: Session = Depends(get_db)):
    """
    Inicia el proceso de auditoría con búsqueda en Google Drive
    """
    google_drive_service = get_google_drive_service()
    
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    
    if not audit:
        raise HTTPException(status_code=404, detail="Auditoría no encontrada")
    
    print(f"\n{'='*60}")
    print(f"INICIANDO AUDITORÍA #{audit.id} - {audit.filename}")
    print(f"{'='*60}\n")
    
    audit.status = "processing"
    db.commit()
    
    if not google_drive_service.ensure_authenticated():
        audit.status = "error"
        db.commit()
        raise HTTPException(
            status_code=401, 
            detail="No autenticado con Google Drive. Por favor autentícate primero en /api/auth/login"
        )
    
    checklist_items = audit.checklist_items
    total_items = len(checklist_items)
    compliant_items = 0
    
    print(f"Procesando {total_items} requisitos del checklist...\n")
    
    for idx, item in enumerate(checklist_items, 1):
        print(f"  [{idx}/{total_items}] Requisito: {item.description}")
        
        keywords = [kw.strip() for kw in item.keywords.split(',')]
        print(f"    Palabras clave: {keywords}")
        
        matched_files = google_drive_service.search_files(keywords)
        
        found = len(matched_files) > 0
        
        if found:
            compliant_items += 1
            print(f"    CUMPLE - Se encontraron {len(matched_files)} archivo(s)")
        else:
            print(f"    NO CUMPLE - No se encontraron archivos")
        
        result = AuditResult(
            audit_id=audit.id,
            checklist_item_id=item.id,
            found=found,
            matched_files=json.dumps(matched_files, ensure_ascii=False) if matched_files else None,
            notes=f"Se encontraron {len(matched_files)} archivos" if found else "No se encontraron archivos"
        )
        db.add(result)
        print()
    
    audit.status = "completed"
    audit.compliant_items = compliant_items
    audit.compliance_rate = round((compliant_items / total_items) * 100, 2) if total_items > 0 else 0
    
    db.commit()
    db.refresh(audit)
    
    print(f"{'='*60}")
    print(f"AUDITORÍA COMPLETADA")
    print(f"   Cumplimiento: {audit.compliance_rate}%")
    print(f"   Requisitos cumplidos: {compliant_items}/{total_items}")
    print(f"{'='*60}\n")
    
    return {
        "message": "Auditoría completada",
        "audit_id": audit.id,
        "status": audit.status,
        "compliance_rate": audit.compliance_rate,
        "compliant_items": compliant_items,
        "total_items": total_items
    }


@router.get("/{audit_id}/status", response_model=AuditStatusResponse)
async def get_audit_status(audit_id: int, db: Session = Depends(get_db)):
    """
    Obtiene el estado actual de una auditoría
    """
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    
    if not audit:
        raise HTTPException(status_code=404, detail="Auditoría no encontrada")
    
    progress_map = {
        "pending": 0,
        "processing": 50,
        "completed": 100,
        "error": 0
    }
    
    return AuditStatusResponse(
        id=audit.id,
        status=audit.status,
        progress=progress_map.get(audit.status, 0),
        message=f"Auditoría {audit.status}"
    )


@router.get("/{audit_id}/report")
async def download_report(audit_id: int, db: Session = Depends(get_db)):
    """
    Descarga el reporte de una auditoría completada
    """
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    
    if not audit:
        raise HTTPException(status_code=404, detail="Auditoría no encontrada")
    
    if audit.status != "completed":
        raise HTTPException(status_code=400, detail="Auditoría no completada")
    
    if not audit.report_path or not os.path.exists(audit.report_path):
        generator = ReportGenerator()
        report_path = generator.generate_report(audit, db)
        audit.report_path = report_path
        db.commit()
    
    return FileResponse(
        path=audit.report_path,
        filename=f"Reporte_Auditoria_{audit.id}.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.get("/history", response_model=AuditHistoryResponse)
async def get_audit_history(db: Session = Depends(get_db)):
    """
    Obtiene el historial de todas las auditorías
    """
    audits = db.query(Audit).order_by(Audit.created_at.desc()).all()
    
    return AuditHistoryResponse(
        audits=[AuditResponse.model_validate(audit) for audit in audits],
        total=len(audits)
    )


@router.delete("/{audit_id}")
async def delete_audit(audit_id: int, db: Session = Depends(get_db)):
    """
    Elimina una auditoría y su reporte asociado
    """
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    
    if not audit:
        raise HTTPException(status_code=404, detail="Auditoría no encontrada")
    
    if audit.report_path and os.path.exists(audit.report_path):
        try:
            os.remove(audit.report_path)
        except Exception as e:
            print(f"Error eliminando archivo de reporte: {e}")
    
    db.delete(audit)
    db.commit()
    
    return {
        "message": "Auditoría eliminada exitosamente",
        "audit_id": audit_id
    }