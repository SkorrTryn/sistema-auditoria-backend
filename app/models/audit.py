from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Audit(Base):
    __tablename__ = "audits"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    status = Column(String(50), default="pending")  # pending, processing, completed, error
    compliance_rate = Column(Float, default=0.0)
    total_items = Column(Integer, default=0)
    compliant_items = Column(Integer, default=0)
    report_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    checklist_items = relationship("ChecklistItem", back_populates="audit", cascade="all, delete-orphan")
    results = relationship("AuditResult", back_populates="audit", cascade="all, delete-orphan")


class ChecklistItem(Base):
    __tablename__ = "checklist_items"
    
    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(Integer, ForeignKey("audits.id", ondelete="CASCADE"))
    item_id = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    keywords = Column(String(500), nullable=False)
    is_mandatory = Column(Boolean, default=True)
    
    # Relaciones
    audit = relationship("Audit", back_populates="checklist_items")


class AuditResult(Base):
    __tablename__ = "audit_results"
    
    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(Integer, ForeignKey("audits.id", ondelete="CASCADE"))
    checklist_item_id = Column(Integer, ForeignKey("checklist_items.id", ondelete="CASCADE"))
    found = Column(Boolean, default=False)
    matched_files = Column(Text, nullable=True)  # JSON string con archivos encontrados
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    audit = relationship("Audit", back_populates="results")