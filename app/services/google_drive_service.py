import os
import pickle
from typing import List, Dict, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from app.config import settings


class GoogleDriveService:
    TOKEN_FILE = "google_token.pickle"
    SCOPES = [
        'https://www.googleapis.com/auth/drive.readonly',
        'https://www.googleapis.com/auth/drive.metadata.readonly'
    ]
    
    def __init__(self):
        self.credentials = None
        self.service = None
        self._load_credentials()
    
    def _load_credentials(self):
        if os.path.exists(self.TOKEN_FILE):
            with open(self.TOKEN_FILE, 'rb') as token:
                self.credentials = pickle.load(token)
        
        if self.credentials and self.credentials.expired and self.credentials.refresh_token:
            try:
                self.credentials.refresh(Request())
                self._save_credentials()
                print("Credenciales renovadas")
            except Exception as e:
                print(f"Error renovando credenciales: {e}")
                self.credentials = None
    
    def _save_credentials(self):
        with open(self.TOKEN_FILE, 'wb') as token:
            pickle.dump(self.credentials, token)
    
    def get_auth_url(self) -> str:
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [settings.GOOGLE_REDIRECT_URI]
                }
            },
            scopes=self.SCOPES,
            redirect_uri=settings.GOOGLE_REDIRECT_URI
        )
        
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        return auth_url
    
    def authenticate_with_code(self, code: str) -> bool:
        try:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": settings.GOOGLE_CLIENT_ID,
                        "client_secret": settings.GOOGLE_CLIENT_SECRET,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [settings.GOOGLE_REDIRECT_URI]
                    }
                },
                scopes=self.SCOPES,
                redirect_uri=settings.GOOGLE_REDIRECT_URI
            )
            
            flow.fetch_token(code=code)
            self.credentials = flow.credentials
            self._save_credentials()
            
            print("Autenticacion exitosa con Google Drive")
            return True
            
        except Exception as e:
            print(f"Error en autenticacion: {e}")
            return False
    
    def ensure_authenticated(self) -> bool:
        if self.credentials and self.credentials.valid:
            return True
        
        self._load_credentials()
        
        if self.credentials and self.credentials.valid:
            return True
        
        return False
    
    def _get_service(self):
        if not self.service and self.credentials:
            self.service = build('drive', 'v3', credentials=self.credentials)
        return self.service
    
    def search_files(self, keywords: List[str]) -> List[Dict]:
        if not self.ensure_authenticated():
            print("No autenticado con Google Drive")
            return []
        
        matched_files = []
        
        try:
            print(f"\n{'='*60}")
            print(f"BUSQUEDA EN GOOGLE DRIVE")
            print(f"Keywords: {keywords}")
            print(f"{'='*60}\n")
            
            service = self._get_service()
            
            query = "trashed=false"
            
            results = service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, mimeType, webViewLink, size, createdTime, modifiedTime, parents)',
                pageSize=1000
            ).execute()
            
            all_files = results.get('files', [])
            
            print(f"Total archivos en Google Drive: {len(all_files)}\n")
            
            if len(all_files) == 0:
                print("No hay archivos en Google Drive\n")
                return []
            
            print("ARCHIVOS EN GOOGLE DRIVE:")
            for idx, file in enumerate(all_files[:10], 1):
                print(f"  {idx}. {file.get('name')}")
            if len(all_files) > 10:
                print(f"  ... y {len(all_files) - 10} mas\n")
            
            print(f"{'='*60}")
            print("FILTRADO POR KEYWORDS")
            print(f"{'='*60}\n")
            
            for file in all_files:
                if file.get('mimeType', '').startswith('application/vnd.google'):
                    continue
                
                file_name = file.get('name', '').lower()
                file_name_clean = file_name.replace('_', ' ').replace('-', ' ')
                
                matched_kw = []
                for kw in keywords:
                    kw_clean = kw.lower().strip()
                    if kw_clean in file_name_clean:
                        matched_kw.append(kw)
                
                if len(matched_kw) == len(keywords):
                    print(f"CUMPLE: {file.get('name')}")
                    matched_files.append({
                        'id': file.get('id'),
                        'name': file.get('name'),
                        'path': 'Google Drive',
                        'web_url': file.get('webViewLink', ''),
                        'size': int(file.get('size', 0)),
                        'created_datetime': file.get('createdTime', ''),
                        'modified_datetime': file.get('modifiedTime', ''),
                        'matched_keywords': matched_kw
                    })
            
            print(f"\n{'='*60}")
            print(f"RESULTADO: {len(matched_files)} archivos")
            print(f"{'='*60}\n")
            
            return matched_files
            
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_file_metadata(self, file_id: str) -> Optional[Dict]:
        if not self.ensure_authenticated():
            return None
        
        try:
            service = self._get_service()
            file = service.files().get(
                fileId=file_id,
                fields='id, name, mimeType, size, webViewLink'
            ).execute()
            return file
        except Exception as e:
            print(f"Error obteniendo metadata: {e}")
            return None