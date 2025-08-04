#!/usr/bin/env python3
"""
WebDAV Uploader API Server
==========================

Tento skript vytváří Flask API server, který umožňuje Perplexity Assistantovi
ukládat výstupy přímo do WebDAV složky na serveru.

Funkce:
- Příjem dat přes API endpoint
- Ověření uživatele pomocí jména a hesla
- Nahrání souborů do WebDAV serveru
- Konfigurace cesty k WebDAV serveru a adresáře
- Bezpečnostní opatření pro nahrávání souborů

Autor: Claude AI Assistant
Datum: 2025-07-05
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from webdav3.client import Client
from functools import wraps
import tempfile
import base64

# Konfigurace aplikace
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB limit

# Konfigurace logování
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Konfigurace WebDAV serveru
WEBDAV_CONFIG = {
    'webdav_hostname': os.getenv('WEBDAV_HOSTNAME', 'https://your-webdav-server.com'),
    'webdav_login': os.getenv('WEBDAV_LOGIN', 'username'),
    'webdav_password': os.getenv('WEBDAV_PASSWORD', 'password'),
    'webdav_root': os.getenv('WEBDAV_ROOT', '/uploads/')
}

# Povolené typy souborů
ALLOWED_EXTENSIONS = {
    'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx',
    'xls', 'xlsx', 'ppt', 'pptx', 'md', 'json', 'xml', 'csv'
}

# Konfigurace uživatelů (v produkci použijte databázi)
USERS = {
    'perplexity': 'secure-password-123',
    'admin': 'admin-password-456'
}


def allowed_file(filename):
    """Kontroluje, zda je typ souboru povolen"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def authenticate_user(username, password):
    """Ověří uživatele podle jména a hesla"""
    return username in USERS and USERS[username] == password


def require_auth(f):
    """Dekorátor pro ověření autentifikace"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.authorization
        if not auth or not authenticate_user(auth.username, auth.password):
            return jsonify({'error': 'Neplatné přihlašovací údaje'}), 401
        return f(*args, **kwargs)
    return decorated_function


def create_webdav_client():
    """Vytvoří WebDAV klienta"""
    try:
        client = Client(WEBDAV_CONFIG)
        return client
    except Exception as e:
        logger.error(f"Chyba při vytváření WebDAV klienta: {e}")
        return None


@app.route('/health', methods=['GET'])
def health_check():
    """Kontrola stavu serveru"""
    return jsonify({
        'status': 'OK',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })


@app.route('/upload', methods=['POST'])
@require_auth
def upload_file():
    """
    Nahraje soubor do WebDAV serveru
    
    Očekávaná data:
    - file: soubor (multipart/form-data)
    - nebo data: base64 encoded data (JSON)
    - filename: název souboru
    - path: cesta v WebDAV (volitelné)
    """
    try:
        # Vytvoření WebDAV klienta
        webdav_client = create_webdav_client()
        if not webdav_client:
            return jsonify({'error': 'Chyba připojení k WebDAV serveru'}), 500

        # Zpracování souboru z multipart/form-data
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'Nebyl vybrán žádný soubor'}), 400
            
            if not allowed_file(file.filename):
                return jsonify({'error': 'Nepodporovaný typ souboru'}), 400
            
            filename = secure_filename(file.filename)
            
            # Kontrola velikosti souboru před čtením
            file.seek(0, 2)  # Přesun na konec souboru
            file_size = file.tell()
            file.seek(0)     # Návrat na začátek
            
            if file_size > app.config['MAX_CONTENT_LENGTH']:
                return jsonify({'error': 'Soubor je příliš velký'}), 413
            
            file_data = file.read()
            
        # Zpracování dat z JSON
        elif request.is_json:
            data = request.get_json()
            if 'data' not in data or 'filename' not in data:
                return jsonify({'error': 'Chybí data nebo filename'}), 400
            
            filename = secure_filename(data['filename'])
            if not allowed_file(filename):
                return jsonify({'error': 'Nepodporovaný typ souboru'}), 400
            
            # Dekódování base64 dat
            try:
                file_data = base64.b64decode(data['data'])
            except Exception:
                # Pokud nejsou data base64, použijeme je přímo
                file_data = data['data'].encode('utf-8')
                
            # Kontrola velikosti pro JSON data
            if len(file_data) > app.config['MAX_CONTENT_LENGTH']:
                return jsonify({'error': 'Soubor je příliš velký'}), 413
        else:
            return jsonify({'error': 'Neplatný formát požadavku'}), 400

        # Určení cesty v WebDAV
        if 'file' in request.files:
            # Pro multipart formuláře
            webdav_path = request.form.get('path', '')
        else:
            # Pro JSON data
            webdav_path = (request.get_json() or {}).get('path', '')
        
        if webdav_path and not webdav_path.startswith('/'):
            webdav_path = '/' + webdav_path
        
        # Sestavení plné cesty
        remote_path = WEBDAV_CONFIG['webdav_root'].rstrip('/') + webdav_path.rstrip('/') + '/' + filename
        
        # Vytvoření dočasného souboru
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file_data)
            temp_file_path = temp_file.name

        try:
            # Nahrání do WebDAV
            webdav_client.upload_sync(remote_path=remote_path, local_path=temp_file_path)
            
            logger.info(f"Soubor {filename} úspěšně nahrán do {remote_path}")
            
            return jsonify({
                'message': 'Soubor úspěšně nahrán',
                'filename': filename,
                'remote_path': remote_path,
                'size': len(file_data)
            }), 200
            
        finally:
            # Smazání dočasného souboru
            os.unlink(temp_file_path)
            
    except Exception as e:
        logger.error(f"Chyba při nahrávání souboru: {e}")
        return jsonify({'error': f'Chyba při nahrávání: {str(e)}'}), 500


@app.route('/list', methods=['GET'])
@require_auth
def list_files():
    """Vypíše soubory v WebDAV adresáři"""
    try:
        webdav_client = create_webdav_client()
        if not webdav_client:
            return jsonify({'error': 'Chyba připojení k WebDAV serveru'}), 500
        
        path = request.args.get('path', WEBDAV_CONFIG['webdav_root'])
        files = webdav_client.list(path)
        
        return jsonify({
            'path': path,
            'files': files
        }), 200
        
    except Exception as e:
        logger.error(f"Chyba při výpisu souborů: {e}")
        return jsonify({'error': f'Chyba při výpisu: {str(e)}'}), 500


@app.route('/config', methods=['GET'])
@require_auth
def get_config():
    """Zobrazí aktuální konfiguraci (bez hesel)"""
    config = WEBDAV_CONFIG.copy()
    config['webdav_password'] = '***'  # Skrytí hesla
    
    return jsonify({
        'webdav_config': config,
        'allowed_extensions': list(ALLOWED_EXTENSIONS),
        'max_file_size': app.config['MAX_CONTENT_LENGTH']
    }), 200


@app.errorhandler(413)
def too_large(e):
    """Obsluha příliš velkých souborů"""
    return jsonify({'error': 'Soubor je příliš velký'}), 413


@app.errorhandler(500)
def internal_error(e):
    """Obsluha interních chyb"""
    logger.error(f"Interní chyba: {e}")
    return jsonify({'error': 'Interní chyba serveru'}), 500


if __name__ == '__main__':
    # Kontrola konfigurace
    if WEBDAV_CONFIG['webdav_hostname'] == 'https://your-webdav-server.com':
        logger.warning("POZOR: Použijte skutečnou WebDAV konfiguraci!")
        print("\nKonfigurace WebDAV serveru:")
        print("export WEBDAV_HOSTNAME='https://your-webdav-server.com'")
        print("export WEBDAV_LOGIN='username'")
        print("export WEBDAV_PASSWORD='password'")
        print("export WEBDAV_ROOT='/uploads/'")
        print("\nPříklad použití:")
        print("curl -u perplexity:secure-password-123 -X POST \\")
        print("  -F 'file=@example.txt' \\")
        print("  http://localhost:5000/upload")
    
    # Spuštění serveru
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('DEBUG', 'False').lower() == 'true'
    )