# Sistema de Auditoría - Backend

Backend en FastAPI para sistema de auditoría automatizada con Google Drive.

## Tecnologías
- FastAPI
- SQLAlchemy
- PostgreSQL / SQLite
- Google Drive API
- Python 3.9+

## Variables de entorno requeridas
```env
DATABASE_URL=postgresql://user:password@host:port/dbname
GOOGLE_CLIENT_ID=tu_client_id
GOOGLE_CLIENT_SECRET=tu_client_secret
GOOGLE_REDIRECT_URI=https://tu-backend.onrender.com/api/auth/callback
FRONTEND_URL=https://tu-frontend.vercel.app
```

## Instalación local
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload