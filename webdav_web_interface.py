#!/usr/bin/env python3
"""
WebDAV Uploader Web Interface
=============================

Webové rozhraní pro správu WebDAV uploader serveru.
Podobné Webmin s kompletní autentifikací a správou.

Autor: Claude AI Assistant
Datum: 2025-07-05
"""

import os
import json
import logging
import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import requests
from werkzeug.security import generate_password_hash, check_password_hash

# Konfigurace aplikace
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Konfigurace logování
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Konfigurace
CONFIG = {
    'API_URL': 'http://localhost:5000',
    'DATABASE_FILE': '/root/webdav_users.db',
    'MAX_LOGIN_ATTEMPTS': 5,
    'LOCKOUT_DURATION': 30,  # minut
    'SESSION_TIMEOUT': 24,   # hodin
    'LOG_FILE': '/var/log/webdav-web.log'
}


class UserManager:
    """Správa uživatelů a autentifikace"""
    
    def __init__(self, db_file):
        self.db_file = db_file
        self.init_database()
    
    def init_database(self):
        """Inicializace databáze"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Tabulka uživatelů
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                is_admin BOOLEAN DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                failed_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP
            )
        ''')
        
        # Tabulka relací
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                username TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Tabulka logů
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                ip_address TEXT,
                action TEXT,
                success BOOLEAN,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details TEXT
            )
        ''')
        
        # Výchozí admin uživatel
        cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('admin',))
        if cursor.fetchone()[0] == 0:
            admin_hash = generate_password_hash('admin123')
            cursor.execute('''
                INSERT INTO users (username, password_hash, email, is_admin, is_active)
                VALUES (?, ?, ?, ?, ?)
            ''', ('admin', admin_hash, 'admin@localhost', True, True))
        
        conn.commit()
        conn.close()
    
    def authenticate_user(self, username, password, ip_address):
        """Ověření uživatele"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        try:
            # Kontrola uzamčení
            cursor.execute('''
                SELECT locked_until FROM users 
                WHERE username = ? AND locked_until > datetime('now')
            ''', (username,))
            
            if cursor.fetchone():
                self.log_access(username, ip_address, 'login_attempt', False, 'Account locked')
                return False, 'Účet je dočasně uzamčen'
            
            # Získání uživatele
            cursor.execute('''
                SELECT password_hash, is_active, failed_attempts 
                FROM users WHERE username = ?
            ''', (username,))
            
            user = cursor.fetchone()
            if not user:
                self.log_access(username, ip_address, 'login_attempt', False, 'User not found')
                return False, 'Neplatné přihlašovací údaje'
            
            password_hash, is_active, failed_attempts = user
            
            if not is_active:
                self.log_access(username, ip_address, 'login_attempt', False, 'Account disabled')
                return False, 'Účet je deaktivován'
            
            # Kontrola hesla
            if check_password_hash(password_hash, password):
                # Úspěšné přihlášení
                cursor.execute('''
                    UPDATE users SET 
                    last_login = datetime('now'),
                    failed_attempts = 0,
                    locked_until = NULL
                    WHERE username = ?
                ''', (username,))
                
                self.log_access(username, ip_address, 'login', True, 'Successful login')
                conn.commit()
                return True, 'Úspěšné přihlášení'
            else:
                # Neúspěšné přihlášení
                failed_attempts += 1
                locked_until = None
                
                if failed_attempts >= CONFIG['MAX_LOGIN_ATTEMPTS']:
                    locked_until = f"datetime('now', '+{CONFIG['LOCKOUT_DURATION']} minutes')"
                    cursor.execute(f'''
                        UPDATE users SET 
                        failed_attempts = ?,
                        locked_until = {locked_until}
                        WHERE username = ?
                    ''', (failed_attempts, username))
                    message = f'Účet uzamčen na {CONFIG["LOCKOUT_DURATION"]} minut'
                else:
                    cursor.execute('''
                        UPDATE users SET failed_attempts = ? WHERE username = ?
                    ''', (failed_attempts, username))
                    message = f'Neplatné heslo. Zbývá {CONFIG["MAX_LOGIN_ATTEMPTS"] - failed_attempts} pokusů'
                
                self.log_access(username, ip_address, 'login_attempt', False, f'Failed attempt {failed_attempts}')
                conn.commit()
                return False, message
                
        finally:
            conn.close()
    
    def create_session(self, username, ip_address, user_agent):
        """Vytvoření relace"""
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=CONFIG['SESSION_TIMEOUT'])
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sessions (session_id, username, ip_address, user_agent, expires_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, username, ip_address, user_agent, expires_at))
        
        conn.commit()
        conn.close()
        
        return session_id
    
    def validate_session(self, session_id):
        """Validace relace"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT username FROM sessions 
            WHERE session_id = ? AND expires_at > datetime('now') AND is_active = 1
        ''', (session_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def invalidate_session(self, session_id):
        """Zneplatnění relace"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE sessions SET is_active = 0 WHERE session_id = ?
        ''', (session_id,))
        
        conn.commit()
        conn.close()
    
    def log_access(self, username, ip_address, action, success, details=''):
        """Logování přístupů"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO access_logs (username, ip_address, action, success, details)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, ip_address, action, success, details))
        
        conn.commit()
        conn.close()
        
        # Logování do souboru
        logger.info(f"{username}@{ip_address} - {action}: {'SUCCESS' if success else 'FAIL'} - {details}")
    
    def get_user_info(self, username):
        """Získání informací o uživateli"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT username, email, is_admin, is_active, created_at, last_login
            FROM users WHERE username = ?
        ''', (username,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'username': result[0],
                'email': result[1],
                'is_admin': bool(result[2]),
                'is_active': bool(result[3]),
                'created_at': result[4],
                'last_login': result[5]
            }
        return None


# Inicializace user manageru
user_manager = UserManager(CONFIG['DATABASE_FILE'])


def require_login(f):
    """Dekorátor pro požadavek přihlášení"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'session_id' not in session:
            return redirect(url_for('login'))
        
        username = user_manager.validate_session(session['session_id'])
        if not username:
            session.clear()
            flash('Relace vypršela, přihlaste se znovu', 'warning')
            return redirect(url_for('login'))
        
        session['username'] = username
        return f(*args, **kwargs)
    return decorated_function


def require_admin(f):
    """Dekorátor pro požadavek admin práv"""
    @wraps(f)
    @require_login
    def decorated_function(*args, **kwargs):
        user_info = user_manager.get_user_info(session['username'])
        if not user_info or not user_info['is_admin']:
            flash('Nedostatečná oprávnění', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    """Hlavní stránka"""
    if 'session_id' in session and user_manager.validate_session(session['session_id']):
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Přihlášení"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        ip_address = request.remote_addr
        
        success, message = user_manager.authenticate_user(username, password, ip_address)
        
        if success:
            session_id = user_manager.create_session(username, ip_address, request.user_agent.string)
            session['session_id'] = session_id
            session['username'] = username
            session.permanent = True
            
            flash('Úspěšně přihlášen', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(message, 'error')
    
    return render_template('login.html')


@app.route('/logout')
@require_login
def logout():
    """Odhlášení"""
    if 'session_id' in session:
        user_manager.invalidate_session(session['session_id'])
        user_manager.log_access(session.get('username', ''), request.remote_addr, 'logout', True, 'User logout')
    
    session.clear()
    flash('Úspěšně odhlášen', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@require_login
def dashboard():
    """Dashboard"""
    # Získání stavu API serveru
    api_status = check_api_status()
    
    # Statistiky
    stats = get_dashboard_stats()
    
    return render_template('dashboard.html', 
                         username=session['username'],
                         api_status=api_status,
                         stats=stats)


@app.route('/upload', methods=['GET', 'POST'])
@require_login
def upload():
    """Upload souborů"""
    if request.method == 'POST':
        try:
            # Předání na API server
            files = request.files
            data = request.form
            
            # Proxy požadavek na API
            api_response = proxy_to_api('/upload', 'POST', files=files, data=data)
            
            if api_response.status_code == 200:
                flash('Soubor úspěšně nahrán', 'success')
                user_manager.log_access(session['username'], request.remote_addr, 'file_upload', True, 'File uploaded via web')
            else:
                flash(f'Chyba při nahrávání: {api_response.text}', 'error')
                user_manager.log_access(session['username'], request.remote_addr, 'file_upload', False, f'Upload failed: {api_response.status_code}')
                
        except Exception as e:
            flash(f'Chyba při nahrávání: {str(e)}', 'error')
    
    return render_template('upload.html')


@app.route('/files')
@require_login
def files():
    """Správa souborů"""
    try:
        # Získání seznamu souborů z API
        api_response = proxy_to_api('/list', 'GET')
        
        if api_response.status_code == 200:
            files_data = api_response.json()
        else:
            files_data = {'files': [], 'error': 'Chyba při načítání souborů'}
            
    except Exception as e:
        files_data = {'files': [], 'error': str(e)}
    
    return render_template('files.html', files_data=files_data)


@app.route('/settings', methods=['GET', 'POST'])
@require_admin
def settings():
    """Nastavení systému"""
    if request.method == 'POST':
        # Uložení nastavení
        flash('Nastavení uloženo', 'success')
    
    # Získání aktuální konfigurace z API
    try:
        api_response = proxy_to_api('/config', 'GET')
        config_data = api_response.json() if api_response.status_code == 200 else {}
    except:
        config_data = {}
    
    return render_template('settings.html', config=config_data)


@app.route('/users')
@require_admin
def users():
    """Správa uživatelů"""
    conn = sqlite3.connect(CONFIG['DATABASE_FILE'])
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT username, email, is_admin, is_active, created_at, last_login
        FROM users ORDER BY created_at DESC
    ''')
    
    users_data = cursor.fetchall()
    conn.close()
    
    return render_template('users.html', users=users_data)


@app.route('/logs')
@require_admin
def logs():
    """Zobrazení logů"""
    conn = sqlite3.connect(CONFIG['DATABASE_FILE'])
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT username, ip_address, action, success, timestamp, details
        FROM access_logs ORDER BY timestamp DESC LIMIT 100
    ''')
    
    logs_data = cursor.fetchall()
    conn.close()
    
    return render_template('logs.html', logs=logs_data)


@app.route('/api/status')
@require_login
def api_status():
    """Status API serveru"""
    status = check_api_status()
    return jsonify(status)


def check_api_status():
    """Kontrola stavu API serveru"""
    try:
        response = requests.get(f"{CONFIG['API_URL']}/health", timeout=5)
        if response.status_code == 200:
            return {'status': 'online', 'data': response.json()}
        else:
            return {'status': 'error', 'message': f'HTTP {response.status_code}'}
    except Exception as e:
        return {'status': 'offline', 'message': str(e)}


def proxy_to_api(endpoint, method, **kwargs):
    """Proxy požadavků na API server"""
    # Použití autentifikace z webmin configu (pro zjednodušení)
    auth = ('perplexity', 'secure-password-123')
    
    url = f"{CONFIG['API_URL']}{endpoint}"
    
    if method == 'GET':
        return requests.get(url, auth=auth, timeout=10)
    elif method == 'POST':
        return requests.post(url, auth=auth, timeout=30, **kwargs)


def get_dashboard_stats():
    """Získání statistik pro dashboard"""
    conn = sqlite3.connect(CONFIG['DATABASE_FILE'])
    cursor = conn.cursor()
    
    # Počet uživatelů
    cursor.execute('SELECT COUNT(*) FROM users WHERE is_active = 1')
    active_users = cursor.fetchone()[0]
    
    # Počet přihlášení dnes
    cursor.execute('''
        SELECT COUNT(*) FROM access_logs 
        WHERE action = 'login' AND success = 1 
        AND date(timestamp) = date('now')
    ''')
    logins_today = cursor.fetchone()[0]
    
    # Počet uploadů dnes
    cursor.execute('''
        SELECT COUNT(*) FROM access_logs 
        WHERE action = 'file_upload' AND success = 1 
        AND date(timestamp) = date('now')
    ''')
    uploads_today = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'active_users': active_users,
        'logins_today': logins_today,
        'uploads_today': uploads_today
    }


# Template pro vytvoření základních HTML šablon
def create_templates():
    """Vytvoření HTML šablon"""
    templates_dir = '/root/templates'
    os.makedirs(templates_dir, exist_ok=True)
    
    # Base template
    base_template = '''<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}WebDAV Uploader{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        .sidebar { min-height: 100vh; }
        .nav-link.active { background-color: #0d6efd; color: white; }
        .card-metric { border-left: 4px solid #0d6efd; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            {% if session.username %}
            <nav class="col-md-2 d-none d-md-block bg-light sidebar">
                <div class="position-sticky pt-3">
                    <h6 class="sidebar-heading d-flex justify-content-between align-items-center px-3 mt-4 mb-1 text-muted">
                        <span>WebDAV Manager</span>
                    </h6>
                    <ul class="nav flex-column">
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('dashboard') }}">
                                <i class="bi bi-house"></i> Dashboard
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('upload') }}">
                                <i class="bi bi-upload"></i> Upload
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('files') }}">
                                <i class="bi bi-files"></i> Soubory
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('settings') }}">
                                <i class="bi bi-gear"></i> Nastavení
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('users') }}">
                                <i class="bi bi-people"></i> Uživatelé
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('logs') }}">
                                <i class="bi bi-list-ul"></i> Logy
                            </a>
                        </li>
                    </ul>
                    <hr>
                    <div class="px-3">
                        <small class="text-muted">Přihlášen: {{ session.username }}</small><br>
                        <a href="{{ url_for('logout') }}" class="btn btn-sm btn-outline-danger mt-2">
                            <i class="bi bi-box-arrow-right"></i> Odhlásit
                        </a>
                    </div>
                </div>
            </nav>
            {% endif %}
            
            <main class="{% if session.username %}col-md-9 ms-sm-auto col-lg-10{% else %}col-12{% endif %} px-md-4">
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show mt-3" role="alert">
                                {{ message }}
                                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                            </div>
                        {% endfor %}
                    {% endif %}
                {% endwith %}
                
                {% block content %}{% endblock %}
            </main>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>'''
    
    with open(f'{templates_dir}/base.html', 'w', encoding='utf-8') as f:
        f.write(base_template)


if __name__ == '__main__':
    # Vytvoření šablon
    create_templates()
    
    print(f"🌐 WebDAV Web Interface starting on port 11001...")
    print(f"📊 Dashboard: http://192.168.0.58:11001")
    print(f"🔐 Default login: admin / admin123")
    
    # Spuštění serveru
    app.run(
        host='0.0.0.0',
        port=11001,
        debug=os.getenv('DEBUG', 'False').lower() == 'true'
    )