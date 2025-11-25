from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class ChecklistItemSchema(BaseModel):
    id: int
    item_id: str
    description: str
    keywords: str
    is_mandatory: bool
    
    class Config:
        from_attributes = True


class AuditResultSchema(BaseModel):
    id: int
    checklist_item_id: int
    found: bool
    matched_files: Optional[str] = None
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True


class AuditCreate(BaseModel):
    filename: str


class AuditResponse(BaseModel):
    id: int
    filename: str
    status: str
    compliance_rate: float
    total_items: int
    compliant_items: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AuditStatusResponse(BaseModel):
    id: int
    status: str
    progress: int
    message: str


class AuditHistoryResponse(BaseModel):
    audits: List[AuditResponse]
    total: int