import msal
import requests
import json
import os
from typing import List, Dict, Optional
from app.config import settings
from pathlib import Path


class OneDriveService:
    TOKEN_CACHE_FILE = "token_cache.json"
    SIMULATED_FOLDER = "simulated_onedrive"
    
    def __init__(self):
        self.client_id = settings.ONEDRIVE_CLIENT_ID
        self.client_secret = settings.ONEDRIVE_CLIENT_SECRET
        self.authority = settings.microsoft_authority
        self.scopes = settings.microsoft_scopes
        self.redirect_uri = settings.ONEDRIVE_REDIRECT_URI
        self.access_token = None
        
        cache = msal.SerializableTokenCache()
        
        if os.path.exists(self.TOKEN_CACHE_FILE):
            with open(self.TOKEN_CACHE_FILE, 'r') as f:
                cache.deserialize(f.read())
        
        self.app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=self.authority,
            client_credential=self.client_secret,
            token_cache=cache
        )
        
        self.cache = cache
        self._load_token_from_cache()
        
        os.makedirs(self.SIMULATED_FOLDER, exist_ok=True)
    
    def _save_cache(self):
        if self.cache.has_state_changed:
            with open(self.TOKEN_CACHE_FILE, 'w') as f:
                f.write(self.cache.serialize())
    
    def _load_token_from_cache(self):
        accounts = self.app.get_accounts()
        if accounts:
            result = self.app.acquire_token_silent(
                scopes=self.scopes,
                account=accounts[0]
            )
            if result and "access_token" in result:
                self.access_token = result["access_token"]
                print(f"Token cargado desde cache")
                return True
        return False
    
    def get_auth_url(self) -> str:
        auth_url = self.app.get_authorization_request_url(
            scopes=self.scopes,
            redirect_uri=self.redirect_uri
        )
        return auth_url
    
    def authenticate_with_code(self, code: str) -> bool:
        try:
            result = self.app.acquire_token_by_authorization_code(
                code,
                scopes=self.scopes,
                redirect_uri=self.redirect_uri
            )
            
            if "access_token" in result:
                self.access_token = result["access_token"]
                self._save_cache()
                print(f"Token obtenido y guardado exitosamente")
                return True
            else:
                print(f"Error en autenticación: {result.get('error_description')}")
                return False
                
        except Exception as e:
            print(f"Error en autenticación: {str(e)}")
            return False
    
    def authenticate_silent(self) -> bool:
        try:
            accounts = self.app.get_accounts()
            if accounts:
                result = self.app.acquire_token_silent(
                    scopes=self.scopes,
                    account=accounts[0]
                )
                if result and "access_token" in result:
                    self.access_token = result["access_token"]
                    self._save_cache()
                    print(f"Token renovado silenciosamente")
                    return True
            
            print("No hay cuentas guardadas para autenticación silenciosa")
            return False
                
        except Exception as e:
            print(f"Error en autenticación silenciosa: {str(e)}")
            return False
    
    def ensure_authenticated(self) -> bool:
        if self.access_token:
            return True
        
        if self._load_token_from_cache():
            return True
        
        if self.authenticate_silent():
            return True
        
        return False
    
    def search_files(self, keywords: List[str]) -> List[Dict]:
        """
        MODO SIMULACION: Busca archivos en carpeta local
        En producción con cuenta empresarial, esto se reemplaza con llamadas a Microsoft Graph
        """
        if not self.ensure_authenticated():
            print("ERROR: No hay token de acceso válido.")
            return []
        
        matched_files = []
        
        try:
            print(f"\n{'='*60}")
            print(f"BUSQUEDA EN ONEDRIVE SIMULADO")
            print(f"Keywords: {keywords}")
            print(f"Carpeta local: {os.path.abspath(self.SIMULATED_FOLDER)}")
            print(f"{'='*60}\n")
            
            simulated_path = Path(self.SIMULATED_FOLDER)
            
            if not simulated_path.exists():
                print(f"ERROR: La carpeta {self.SIMULATED_FOLDER} no existe")
                return []
            
            all_files = list(simulated_path.glob('*'))
            all_files = [f for f in all_files if f.is_file()]
            
            print(f"Archivos en carpeta simulada: {len(all_files)}\n")
            
            if len(all_files) == 0:
                print(f"ADVERTENCIA: No hay archivos en {self.SIMULATED_FOLDER}")
                print(f"Copia tus archivos PDF a esta carpeta para simular OneDrive\n")
                return []
            
            print("ARCHIVOS ENCONTRADOS:")
            for idx, file in enumerate(all_files, 1):
                print(f"  {idx}. {file.name}")
            
            print(f"\n{'='*60}")
            print("FILTRADO POR KEYWORDS")
            print(f"{'='*60}\n")
            
            for file in all_files:
                file_name = file.name.lower()
                file_name_clean = file_name.replace('_', ' ').replace('-', ' ')
                
                print(f"Archivo: {file.name}")
                
                matched_kw = []
                for kw in keywords:
                    kw_clean = kw.lower().strip()
                    if kw_clean in file_name_clean:
                        matched_kw.append(kw)
                        print(f"  [OK] '{kw_clean}'")
                    else:
                        print(f"  [X]  '{kw_clean}'")
                
                if len(matched_kw) == len(keywords):
                    print(f"  CUMPLE\n")
                    matched_files.append({
                        'id': str(file),
                        'name': file.name,
                        'path': str(file.parent),
                        'web_url': f'file:///{file.absolute()}',
                        'size': file.stat().st_size,
                        'created_datetime': str(file.stat().st_ctime),
                        'modified_datetime': str(file.stat().st_mtime),
                        'matched_keywords': matched_kw
                    })
                else:
                    print(f"  NO CUMPLE\n")
            
            print(f"{'='*60}")
            print(f"RESULTADO: {len(matched_files)} archivo(s) cumplen")
            print(f"{'='*60}\n")
            
            return matched_files
            
        except Exception as e:
            print(f"EXCEPCION: {str(e)}\n")
            import traceback
            traceback.print_exc()
            return []
    
    def get_file_metadata(self, file_id: str) -> Optional[Dict]:
        if not self.ensure_authenticated():
            return None
        
        try:
            file_path = Path(file_id)
            if file_path.exists():
                return {
                    'id': str(file_path),
                    'name': file_path.name,
                    'size': file_path.stat().st_size
                }
        except Exception as e:
            print(f"Error obteniendo metadata: {str(e)}")
            return None