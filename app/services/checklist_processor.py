import pandas as pd
from sqlalchemy.orm import Session
from app.models.audit import Audit, ChecklistItem


class ChecklistProcessor:
    def __init__(self, db: Session):
        self.db = db
    
    def process_checklist(self, file_path: str, filename: str) -> Audit:
        """
        Procesa un archivo Excel de checklist y crea registros en la BD
        """
        # Leer archivo Excel
        df = pd.read_excel(file_path)
        
        # Validar columnas requeridas
        required_columns = ['ID', 'Pregunta', 'Palabras_Clave', 'Obligatorio']
        
        # Renombrar columnas si es necesario (flexible)
        df.columns = df.columns.str.strip()
        
        # Crear auditoría
        audit = Audit(
            filename=filename,
            status="pending",
            total_items=len(df)
        )
        self.db.add(audit)
        self.db.flush()  # Para obtener el ID
        
        # Procesar cada fila del checklist
        for _, row in df.iterrows():
            item = ChecklistItem(
                audit_id=audit.id,
                item_id=str(row.iloc[0]),  # Columna A: ID
                description=str(row.iloc[1]),  # Columna B: Pregunta
                keywords=str(row.iloc[2]),  # Columna C: Palabras clave
                is_mandatory=str(row.iloc[3]).lower() in ['si', 'sí', 'yes', 'true', '1']  # Columna D
            )
            self.db.add(item)
        
        self.db.commit()
        self.db.refresh(audit)
        
        return audit