from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.services.google_drive_service import GoogleDriveService
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

_google_drive_service = None

def get_google_drive_service():
    global _google_drive_service
    if _google_drive_service is None:
        _google_drive_service = GoogleDriveService()
    return _google_drive_service


@router.get("/login")
async def login():
    service = get_google_drive_service()
    auth_url = service.get_auth_url()
    
    return {
        "auth_url": auth_url,
        "message": "Redirige al usuario a esta URL para autenticarse"
    }


@router.get("/callback")
async def auth_callback(code: str = None, error: str = None):
    if error:
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error de autenticacion</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
                }
                .container {
                    text-align: center;
                    background: white;
                    padding: 40px;
                    border-radius: 12px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                }
                .error-icon {
                    font-size: 64px;
                    color: #ef4444;
                    margin-bottom: 20px;
                }
                h1 {
                    color: #dc2626;
                    margin-bottom: 10px;
                }
                p {
                    color: #6b7280;
                    font-size: 14px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error-icon">X</div>
                <h1>Error de autenticacion</h1>
                <p>No se pudo conectar con Google Drive. Por favor intenta de nuevo.</p>
            </div>
            <script>
                if (window.opener) {
                    window.opener.postMessage({ type: 'auth_error' }, '*');
                }
                setTimeout(function() {
                    window.close();
                }, 3000);
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    
    if not code:
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error de autenticacion</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
                }
                .container {
                    text-align: center;
                    background: white;
                    padding: 40px;
                    border-radius: 12px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                }
                .error-icon {
                    font-size: 64px;
                    color: #ef4444;
                    margin-bottom: 20px;
                }
                h1 {
                    color: #dc2626;
                    margin-bottom: 10px;
                }
                p {
                    color: #6b7280;
                    font-size: 14px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error-icon">X</div>
                <h1>Error de autenticacion</h1>
                <p>No se recibio codigo de autorizacion.</p>
            </div>
            <script>
                if (window.opener) {
                    window.opener.postMessage({ type: 'auth_error' }, '*');
                }
                setTimeout(function() {
                    window.close();
                }, 3000);
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    
    service = get_google_drive_service()
    success = service.authenticate_with_code(code)
    
    if success:
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Autenticacion exitosa</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                }
                .container {
                    text-align: center;
                    background: white;
                    padding: 40px;
                    border-radius: 12px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                }
                .success-icon {
                    font-size: 64px;
                    color: #10b981;
                    margin-bottom: 20px;
                }
                h1 {
                    color: #059669;
                    margin-bottom: 10px;
                }
                p {
                    color: #6b7280;
                    font-size: 14px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success-icon">&#10003;</div>
                <h1>Autenticacion exitosa</h1>
                <p>Conectado con Google Drive. Esta ventana se cerrara automaticamente...</p>
            </div>
            <script>
                if (window.opener) {
                    window.opener.postMessage({ type: 'auth_success' }, '*');
                }
                setTimeout(function() {
                    window.close();
                }, 2000);
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    else:
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error de autenticacion</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
                }
                .container {
                    text-align: center;
                    background: white;
                    padding: 40px;
                    border-radius: 12px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                }
                .error-icon {
                    font-size: 64px;
                    color: #ef4444;
                    margin-bottom: 20px;
                }
                h1 {
                    color: #dc2626;
                    margin-bottom: 10px;
                }
                p {
                    color: #6b7280;
                    font-size: 14px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error-icon">X</div>
                <h1>Error de autenticacion</h1>
                <p>No se pudo conectar con Google Drive. Por favor intenta de nuevo.</p>
            </div>
            <script>
                if (window.opener) {
                    window.opener.postMessage({ type: 'auth_error' }, '*');
                }
                setTimeout(function() {
                    window.close();
                }, 3000);
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)


@router.get("/status")
async def auth_status():
    service = get_google_drive_service()
    
    if service.ensure_authenticated():
        return {
            "authenticated": True,
            "message": "Usuario autenticado con Google Drive"
        }
    else:
        return {
            "authenticated": False,
            "message": "Usuario no autenticado"
        }