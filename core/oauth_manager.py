"""
oauth_manager.py
Handles OAuth2 PKCE Flows for Nova26, mimicking OpenClaw.
"""
import os
import secrets
import hashlib
import base64
import json
import webbrowser
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import urllib.request

# OpenClaw Public Client ID for OpenAI (Codex / ChatGPT Plus)
OPENAI_CLIENT_ID = "app_EMoamEEZ73f0CkXaXp7hrann"
OPENAI_AUTH_URL = "https://auth.openai.com/oauth/authorize"
OPENAI_TOKEN_URL = "https://auth.openai.com/oauth/token"

# Google (gcloud default) Public Client ID for Gemini
GOOGLE_CLIENT_ID = "32555940559.apps.googleusercontent.com" # Default gcloud client ID
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"

REDIRECT_URI = "http://localhost:1455/auth/callback"

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Local server to catch the redirect callback."""
    def log_message(self, format, *args):
        pass # Silence logging

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == '/auth/callback':
            query_components = urllib.parse.parse_qs(parsed_path.query)
            if 'code' in query_components:
                self.server.auth_code = query_components['code'][0]
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(b"<html><body><h1>Autenticacion Exitosa</h1><p>Ya puedes volver a la consola de nova26.</p><script>window.close()</script></body></html>")
            else:
                self.send_response(400)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(b"<html><body><h1>Error</h1><p>No se encontro codigo de autorizacion.</p></body></html>")
        else:
            self.send_response(404)
            self.end_headers()

class OAuthManager:
    def __init__(self, db):
        self.db = db
        self.port = 1455

    def generate_pkce_challenge(self):
        """Generate PKCE verifier and challenge."""
        code_verifier = secrets.token_urlsafe(64)
        hashed = hashlib.sha256(code_verifier.encode('ascii')).digest()
        code_challenge = base64.urlsafe_b64encode(hashed).decode('ascii').rstrip('=')
        return code_verifier, code_challenge

    async def login_openai(self):
        """Perform the OAuth2 PKCE flow for OpenAI."""
        logging.info("Iniciando flujo OAuth (PKCE) hacia OpenAI...")
        
        verifier, challenge = self.generate_pkce_challenge()
        state = secrets.token_urlsafe(16)
        
        params = {
            'response_type': 'code',
            'client_id': OPENAI_CLIENT_ID,
            'redirect_uri': REDIRECT_URI,
            'scope': 'openid profile email offline_access',
            'state': state,
            'code_challenge': challenge,
            'code_challenge_method': 'S256',
            'id_token_add_organizations': 'true',
            'codex_cli_simplified_flow': 'true',
            'originator': 'pi'
        }
        
        url = f"{OPENAI_AUTH_URL}?{urllib.parse.urlencode(params)}"
        print(f"\n[*] Abriendo el navegador para autenticar con OpenAI...")
        print(f"[*] Si no se abre, pega esto en el navegador: {url}")
        webbrowser.open(url)
        
        # Start local server to catch callback
        server = HTTPServer(('localhost', 1455), OAuthCallbackHandler)
        server.auth_code = None
        
        print(f"[*] Esperando respuesta en el puerto 1455...")
        while server.auth_code is None:
            server.handle_request()
            
        auth_code = server.auth_code
        server.server_close()
        
        print("[*] Codigo recibido. Intercambiando por tokens...")
        
        # Exchange code for token
        data = urllib.parse.urlencode({
            'grant_type': 'authorization_code',
            'client_id': OPENAI_CLIENT_ID,
            'code': auth_code,
            'redirect_uri': REDIRECT_URI,
            'code_verifier': verifier
        }).encode('utf-8')
        
        req = urllib.request.Request(OPENAI_TOKEN_URL, data=data)
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode())
                
                access_token = result.get('access_token')
                refresh_token = result.get('refresh_token')
                
                if access_token:
                    # Guardar en DB
                    await self.db.conn.execute(
                        "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", 
                        ('openai_access_token', access_token)
                    )
                    if refresh_token:
                         await self.db.conn.execute(
                            "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", 
                            ('openai_refresh_token', refresh_token)
                        )
                    await self.db.conn.commit()
                    print("\n[+] Login EXITOSO. Tokens guardados en la BD de memoria (config).")
                    return True
                else:
                    print("\n[-] Error: Respuesta del proveedor no incluye access_token.")
                    return False
        except urllib.error.HTTPError as e:
            err = e.read().decode()
            print(f"\n[-] Falla en el login: {e.code} {e.reason}")
            print(f"Detalle: {err}")
            return False
        except Exception as e:
            print(f"\n[-] Error inesperado al hacer login: {e}")
            return False

    async def login_google(self):
        """Perform the OAuth2 PKCE flow for Google Gemini."""
        logging.info("Iniciando flujo OAuth (PKCE) hacia Google...")
        
        verifier, challenge = self.generate_pkce_challenge()
        state = secrets.token_urlsafe(16)
        
        params = {
            'response_type': 'code',
            'client_id': GOOGLE_CLIENT_ID,
            'redirect_uri': REDIRECT_URI,
            'scope': 'openid https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/cloud-platform',
            'state': state,
            'code_challenge': challenge,
            'code_challenge_method': 'S256',
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        url = f"{GOOGLE_AUTH_URL}?{urllib.parse.urlencode(params)}"
        print(f"\n[*] Abriendo el navegador para autenticar con Google (Gemini)...")
        print(f"[*] Si no se abre, pega esto en el navegador: {url}")
        webbrowser.open(url)
        
        # Start local server to catch callback
        server = HTTPServer(('localhost', 1455), OAuthCallbackHandler)
        server.auth_code = None
        
        print(f"[*] Esperando respuesta en el puerto 1455...")
        while server.auth_code is None:
            server.handle_request()
            
        auth_code = server.auth_code
        server.server_close()
        
        print("[*] Codigo recibido. Intercambiando por tokens de Google...")
        
        # Exchange code for token
        data = urllib.parse.urlencode({
            'grant_type': 'authorization_code',
            'client_id': GOOGLE_CLIENT_ID,
            'code': auth_code,
            'redirect_uri': REDIRECT_URI,
            'code_verifier': verifier
        }).encode('utf-8')
        
        req = urllib.request.Request(GOOGLE_TOKEN_URL, data=data)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode())
                
                access_token = result.get('access_token')
                refresh_token = result.get('refresh_token')
                
                if access_token:
                    # Guardar en DB
                    await self.db.conn.execute(
                        "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", 
                        ('google_access_token', access_token)
                    )
                    if refresh_token:
                         await self.db.conn.execute(
                            "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", 
                            ('google_refresh_token', refresh_token)
                        )
                    await self.db.conn.commit()
                    print("\n[+] Login EXITOSO. Tokens guardados en la BD de memoria (config).")
                    return True
                else:
                    print("\n[-] Error: Respuesta de Google no incluye access_token.")
                    return False
        except urllib.error.HTTPError as e:
            err = e.read().decode()
            print(f"\n[-] Falla en el login Google: {e.code} {e.reason}")
            print(f"Detalle: {err}")
            return False
        except Exception as e:
            print(f"\n[-] Error inesperado al hacer login en Google: {e}")
            return False

    async def get_openai_token(self):
        """Retrieve the token from the DB."""
        async with self.db.conn.execute("SELECT value FROM config WHERE key = 'openai_access_token'") as cursor:
            row = await cursor.fetchone()
            if row:
                return row['value']
        return None

    async def get_google_token(self):
        """Retrieve the Google token from the DB."""
        async with self.db.conn.execute("SELECT value FROM config WHERE key = 'google_access_token'") as cursor:
            row = await cursor.fetchone()
            if row:
                return row['value']
        return None
