# WebDAV Uploader - Kompletní dokumentace

## 📋 Obsah
1. [Přehled systému](#přehled-systému)
2. [Architektura](#architektura)
3. [Instalace a konfigurace](#instalace-a-konfigurace)
4. [API dokumentace](#api-dokumentace)
5. [Webové rozhraní](#webové-rozhraní)
6. [Bezpečnost](#bezpečnost)
7. [Testování](#testování)
8. [Údržba a monitoring](#údržba-a-monitoring)
9. [Troubleshooting](#troubleshooting)
10. [FAQ](#faq)

---

## 🎯 Přehled systému

**WebDAV Uploader** je kompletní řešení pro nahrávání souborů do WebDAV serveru s následujícími komponenty:

### Komponenty systému
- **API Server** (port 5000) - REST API pro nahrávání souborů
- **Web Interface** (port 11001) - Webové rozhraní podobné Webmin
- **Test Suite** - Kompletní testovací sada
- **Documentation** - Tato dokumentace a PDF návod

### Klíčové funkce
- ✅ **Bezpečné nahrávání** souborů do WebDAV
- ✅ **Webové rozhraní** s autentifikací
- ✅ **Správa uživatelů** s rolemi (admin/user)
- ✅ **Monitoring a logy** všech operací
- ✅ **Bezpečnostní opatření** (rate limiting, file validation)
- ✅ **Multi-format support** (JSON API, multipart upload)

---

## 🏗️ Architektura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │────│  Web Interface  │────│   API Server    │
│                 │    │   Port 11001    │    │   Port 5000     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  SQLite Users   │    │  WebDAV Server  │
                       │   Database      │    │   External      │
                       └─────────────────┘    └─────────────────┘
```

### Datový tok
1. **Uživatel** se přihlásí přes webové rozhraní
2. **Web Interface** ověří autentifikaci v SQLite databázi
3. **Soubor** se nahraje přes web formulář
4. **API Server** zpracuje soubor a nahraje do WebDAV
5. **Logy** se zaznamenají do databáze

---

## 🚀 Instalace a konfigurace

### Rychlá instalace

```bash
# 1. Spuštění instalačního skriptu
cd /root
./install_webdav_uploader.sh

# 2. Konfigurace WebDAV serveru
nano /root/webdav_config.env

# 3. Spuštění služeb
systemctl start webdav-uploader
python3 /root/webdav_web_interface.py
```

### Detailní instalace

#### Krok 1: Příprava prostředí
```bash
# Vytvoření virtual environment
python3 -m venv /root/venv
source /root/venv/bin/activate

# Instalace závislostí
pip install -r requirements.txt
```

#### Krok 2: Konfigurace WebDAV
```bash
# Editace konfigurace
nano /root/webdav_config.env
```

**Příklad konfigurace:**
```env
# WebDAV Server Configuration
WEBDAV_HOSTNAME=https://your-webdav-server.com
WEBDAV_LOGIN=webdav_user
WEBDAV_PASSWORD=secure_password
WEBDAV_ROOT=/uploads/

# Server Configuration
PORT=5000
DEBUG=False
```

#### Krok 3: Databáze uživatelů
```bash
# Databáze se vytvoří automaticky při prvním spuštění
# Výchozí admin účet: admin / admin123
```

#### Krok 4: Firewall konfigurace
```bash
# Povolení portů
iptables -I INPUT -p tcp --dport 5000 -s 192.168.0.0/24 -j ACCEPT   # API
iptables -I INPUT -p tcp --dport 11001 -s 192.168.0.0/24 -j ACCEPT  # Web
iptables-save > /etc/iptables/rules-save
```

#### Krok 5: Systemd služby
```bash
# API Server service
cat > /etc/systemd/system/webdav-api.service << 'EOF'
[Unit]
Description=WebDAV Uploader API Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root
Environment=PYTHONPATH=/root
EnvironmentFile=/root/webdav_config.env
ExecStart=/root/venv/bin/python /root/webdav_uploader.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Web Interface service
cat > /etc/systemd/system/webdav-web.service << 'EOF'
[Unit]
Description=WebDAV Web Interface
After=network.target webdav-api.service

[Service]
Type=simple
User=root
WorkingDirectory=/root
Environment=PYTHONPATH=/root
ExecStart=/root/venv/bin/python /root/webdav_web_interface.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Aktivace služeb
systemctl daemon-reload
systemctl enable webdav-api webdav-web
systemctl start webdav-api webdav-web
```

---

## 📡 API dokumentace

### Base URL
```
http://192.168.0.58:5000
```

### Autentifikace
Všechny endpointy (kromě `/health`) vyžadují **HTTP Basic Authentication**.

**Výchozí účty:**
- `perplexity:secure-password-123` (API uživatel)
- `admin:admin-password-456` (Admin)

### Endpointy

#### 1. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "OK",
  "timestamp": "2025-07-05T20:00:00.000000",
  "version": "1.0.0"
}
```

#### 2. Upload File (Multipart)
```http
POST /upload
Content-Type: multipart/form-data
Authorization: Basic <base64_encoded_credentials>

Form data:
- file: <file_binary>
- path: <optional_path>
```

**Response:**
```json
{
  "message": "Soubor úspěšně nahrán",
  "filename": "document.pdf",
  "remote_path": "/uploads/subfolder/document.pdf",
  "size": 1024000
}
```

#### 3. Upload File (JSON)
```http
POST /upload
Content-Type: application/json
Authorization: Basic <base64_encoded_credentials>

{
  "filename": "document.txt",
  "data": "SGVsbG8gV29ybGQ=",  // base64 encoded
  "path": "/subfolder"
}
```

#### 4. List Files
```http
GET /list?path=/uploads/subfolder
Authorization: Basic <base64_encoded_credentials>
```

**Response:**
```json
{
  "path": "/uploads/subfolder",
  "files": [
    "document1.pdf",
    "image.jpg",
    "text.txt"
  ]
}
```

#### 5. Get Configuration
```http
GET /config
Authorization: Basic <base64_encoded_credentials>
```

**Response:**
```json
{
  "webdav_config": {
    "webdav_hostname": "https://webdav-server.com",
    "webdav_login": "user",
    "webdav_password": "***",
    "webdav_root": "/uploads/"
  },
  "allowed_extensions": ["pdf", "jpg", "txt", "docx"],
  "max_file_size": 52428800
}
```

### Error Responses

```json
{
  "error": "Popis chyby"
}
```

**HTTP Status Codes:**
- `200` - OK
- `400` - Špatný požadavek
- `401` - Neautorizováno
- `413` - Soubor příliš velký
- `500` - Serverová chyba

### Curl příklady

```bash
# Health check
curl http://192.168.0.58:5000/health

# Upload souboru
curl -u perplexity:secure-password-123 -X POST \
  -F 'file=@document.pdf' \
  -F 'path=/documents' \
  http://192.168.0.58:5000/upload

# Upload přes JSON
curl -u perplexity:secure-password-123 -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "test.txt",
    "data": "SGVsbG8gV29ybGQ=",
    "path": "/test"
  }' \
  http://192.168.0.58:5000/upload

# Seznam souborů
curl -u perplexity:secure-password-123 \
  http://192.168.0.58:5000/list

# Konfigurace
curl -u perplexity:secure-password-123 \
  http://192.168.0.58:5000/config
```

---

## 🌐 Webové rozhraní

### URL a přístup
```
http://192.168.0.58:11001
```

**Výchozí přihlášení:**
- Username: `admin`
- Password: `admin123`

### Struktura rozhraní

#### 1. Dashboard
- **Přehled systému** - status API serveru, statistiky
- **Rychlé akce** - odkazy na upload, správu souborů
- **Monitoring** - aktivní uživatelé, přihlášení dnes

#### 2. Upload souborů
- **Drag & Drop interface** pro snadné nahrávání
- **Progress bar** s real-time statusem
- **Validace souborů** před uploadem
- **Podporované formáty** s ikonami

#### 3. Správa souborů
- **Tabulkový přehled** všech souborů
- **Akce nad soubory** - download, info, delete
- **Filtrování** podle typu a data
- **Bulk operace** pro více souborů

#### 4. Nastavení systému
- **WebDAV konfigurace** - server, credentials
- **Bezpečnostní nastavení** - timeout, pokusy o přihlášení
- **Test připojení** k WebDAV serveru
- **Export/import** konfigurace

#### 5. Správa uživatelů
- **Přehled všech uživatelů** s rolemi
- **Přidání nového uživatele** s validací
- **Editace existujících** uživatelů
- **Aktivace/deaktivace** účtů

#### 6. Systémové logy
- **Přístupové logy** s filtrováním
- **Real-time monitoring** aktivit
- **Export logů** do CSV
- **Statistiky** úspěšnosti operací

### Bezpečnostní funkce webového rozhraní

#### Autentifikace
- **Session-based** autentifikace
- **Automatic logout** po timeoutu
- **Remember me** funkčnost
- **Secure session** handling

#### Autorizace
- **Role-based access** (admin/user)
- **Page-level protection** pro admin funkce
- **Action-level control** pro citlivé operace

#### Bezpečnostní opatření
- **Rate limiting** pro přihlášení
- **Account lockout** po neúspěšných pokusech
- **Session timeout** automatické odhlášení
- **CSRF protection** pro formuláře
- **Input validation** pro všechny vstupy
- **XSS protection** v templates

---

## 🔒 Bezpečnost

### Autentifikace a autorizace

#### API Server
```python
# HTTP Basic Authentication
@require_auth
def protected_endpoint():
    # Ověření uživatele v slovníku USERS
    return authenticate_user(username, password)
```

#### Web Interface
```python
# Session-based authentication
@require_login
def dashboard():
    # Kontrola platné session v databázi
    return validate_session(session_id)

@require_admin  
def admin_function():
    # Navíc kontrola admin role
    return check_admin_role(username)
```

### Validace souborů

#### Povolené typy
```python
ALLOWED_EXTENSIONS = {
    'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 
    'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
    'md', 'json', 'xml', 'csv'
}
```

#### Sanitizace názvů
```python
from werkzeug.utils import secure_filename

# Bezpečný název souboru
safe_name = secure_filename(user_filename)
```

#### Kontrola velikosti
```python
# Limit 50MB
MAX_CONTENT_LENGTH = 50 * 1024 * 1024

# Kontrola před zpracováním
if file_size > MAX_CONTENT_LENGTH:
    return jsonify({'error': 'Soubor je příliš velký'}), 413
```

### Ochrana proti útokům

#### Path Traversal
```python
# Automatická ochrana pomocí secure_filename()
filename = secure_filename(user_input)
# Výsledek: ../../../etc/passwd → etc_passwd
```

#### SQL Injection  
```python
# Parametrizované dotazy
cursor.execute(
    'SELECT * FROM users WHERE username = ?', 
    (username,)
)
```

#### XSS Protection
```jinja2
<!-- Automatické escapování v Jinja2 templates -->
{{ user_input|e }}
```

#### CSRF Protection
```python
# Flask-WTF CSRF tokens
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)
```

### Logování bezpečnostních událostí

```python
def log_security_event(username, ip, event, success, details):
    logger.info(f"SECURITY: {username}@{ip} - {event}: {success} - {details}")
    
    # Uložení do databáze
    cursor.execute('''
        INSERT INTO access_logs (username, ip_address, action, success, details)
        VALUES (?, ?, ?, ?, ?)
    ''', (username, ip, event, success, details))
```

### Konfigurace bezpečnosti

#### Rate Limiting
```python
CONFIG = {
    'MAX_LOGIN_ATTEMPTS': 5,
    'LOCKOUT_DURATION': 30,  # minut
    'SESSION_TIMEOUT': 24,   # hodin
}
```

#### Hesla
```python
# Hashování hesel pomocí Werkzeug
from werkzeug.security import generate_password_hash, check_password_hash

# Uložení
password_hash = generate_password_hash(plain_password)

# Ověření
is_valid = check_password_hash(stored_hash, plain_password)
```

---

## 🧪 Testování

### Test Suite přehled

**Celkem testů:** 21  
**Kategorie:**
- **Funkční testy** (11) - API endpointy, upload, autentifikace
- **Bezpečnostní testy** (6) - XSS, SQL injection, path traversal
- **Integrační testy** (4) - kompletní workflow, error handling

### Spuštění testů

```bash
# Příprava prostředí
source /root/venv/bin/activate

# Spuštění všech testů
python3 /root/test_webdav_uploader.py

# Spuštění specifické kategorie
python3 -m unittest test_webdav_uploader.TestSecurity

# Verbose output
python3 -m unittest test_webdav_uploader -v
```

### Test kategorie

#### 1. Funkční testy
```python
class TestWebDAVUploader(unittest.TestCase):
    def test_health_endpoint(self):
        """Test health check endpointu"""
        
    def test_authentication_valid(self):
        """Test platného přihlášení"""
        
    def test_upload_multipart_success(self):
        """Test úspěšného upload přes multipart"""
        
    def test_upload_json_success(self):
        """Test úspěšného upload přes JSON"""
```

#### 2. Bezpečnostní testy
```python
class TestSecurity(unittest.TestCase):
    def test_path_traversal_protection(self):
        """Test ochrany proti path traversal"""
        
    def test_sql_injection_attempts(self):
        """Test pokusů o SQL injection"""
        
    def test_xss_prevention(self):
        """Test prevence XSS útoků"""
```

#### 3. Integrační testy
```python
class TestIntegration(unittest.TestCase):
    def test_full_workflow(self):
        """Test kompletního workflow"""
```

### Mock objekty pro testování

```python
@patch('webdav_uploader.create_webdav_client')
def test_upload_success(self, mock_webdav):
    # Mock WebDAV client
    mock_client = MagicMock()
    mock_client.upload_sync.return_value = True
    mock_webdav.return_value = mock_client
    
    # Test upload
    response = self.app.post('/upload', ...)
    self.assertEqual(response.status_code, 200)
```

### Continuous Integration

```bash
# Pre-commit hook
#!/bin/bash
echo "Spouštím testy před commitem..."
source /root/venv/bin/activate
python3 /root/test_webdav_uploader.py

if [ $? -ne 0 ]; then
    echo "❌ Testy selhaly! Commit zamítnut."
    exit 1
fi

echo "✅ Všechny testy prošly!"
```

### Test coverage

```bash
# Instalace coverage
pip install coverage

# Spuštění s coverage
coverage run /root/test_webdav_uploader.py
coverage report
coverage html  # HTML report
```

---

## 📊 Údržba a monitoring

### Systemd služby

#### Status kontrola
```bash
# Status všech služeb
systemctl status webdav-api webdav-web

# Detailní info o službě
systemctl show webdav-api

# Restart služeb
systemctl restart webdav-api webdav-web
```

#### Logy služeb
```bash
# Real-time logy
journalctl -u webdav-api -f
journalctl -u webdav-web -f

# Logy za posledních 24 hodin
journalctl -u webdav-api --since "24 hours ago"

# Logy s chybami
journalctl -u webdav-api -p err
```

### Monitoring skripty

#### Server Health Check
```bash
#!/bin/bash
# /root/health_check.sh

echo "🔍 WebDAV Uploader Health Check"
echo "================================"

# API Server check
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/health)
if [ "$API_STATUS" = "200" ]; then
    echo "✅ API Server: Online"
else
    echo "❌ API Server: Offline (HTTP $API_STATUS)"
fi

# Web Interface check  
WEB_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:11001)
if [ "$WEB_STATUS" = "302" ]; then
    echo "✅ Web Interface: Online"
else
    echo "❌ Web Interface: Offline (HTTP $WEB_STATUS)"
fi

# Database check
if [ -f "/root/webdav_users.db" ]; then
    DB_SIZE=$(stat -c%s "/root/webdav_users.db")
    echo "✅ Database: OK (${DB_SIZE} bytes)"
else
    echo "❌ Database: Missing"
fi

# Disk space check
DISK_USAGE=$(df /root | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    echo "✅ Disk Space: OK (${DISK_USAGE}% used)"
else
    echo "⚠️ Disk Space: Warning (${DISK_USAGE}% used)"
fi

echo "================================"
echo "Check completed: $(date)"
```

#### Performance Monitoring
```bash
#!/bin/bash
# /root/performance_monitor.sh

# CPU a Memory usage
echo "📊 Performance Stats"
echo "==================="

# Python procesy
ps aux | grep python3 | grep -E "(webdav_uploader|webdav_web_interface)" | while read line; do
    PID=$(echo $line | awk '{print $2}')
    CPU=$(echo $line | awk '{print $3}')
    MEM=$(echo $line | awk '{print $4}')
    CMD=$(echo $line | awk '{print $11}')
    
    echo "Process: $(basename $CMD)"
    echo "  PID: $PID"
    echo "  CPU: ${CPU}%"
    echo "  Memory: ${MEM}%"
    echo ""
done

# Síťové spojení
echo "🌐 Network Connections:"
netstat -tlnp | grep -E "(5000|11001)" | while read line; do
    PORT=$(echo $line | awk '{print $4}' | cut -d: -f2)
    PID=$(echo $line | awk '{print $7}' | cut -d/ -f1)
    echo "  Port $PORT: PID $PID"
done
```

### Backup strategie

#### Automatický backup
```bash
#!/bin/bash
# /root/backup_webdav.sh

BACKUP_DIR="/opt/backups/webdav"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

echo "🔄 Starting WebDAV backup..."

# Database backup
cp /root/webdav_users.db "$BACKUP_DIR/users_${DATE}.db"

# Configuration backup
tar -czf "$BACKUP_DIR/config_${DATE}.tar.gz" \
    /root/webdav_*.py \
    /root/templates/ \
    /root/webdav_config.env \
    /root/requirements*.txt

# Cleanup old backups (keep 30 days)
find "$BACKUP_DIR" -name "*.db" -mtime +30 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete

echo "✅ Backup completed: $BACKUP_DIR"
```

#### Cron job pro backup
```bash
# Přidání do crontab
echo "0 2 * * * /root/backup_webdav.sh >> /var/log/webdav-backup.log 2>&1" | crontab -
```

### Log rotation

```bash
# /etc/logrotate.d/webdav
/var/log/webdav-*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        systemctl reload webdav-api webdav-web
    endscript
}
```

### Alerting

#### Email notifikace při chybách
```bash
#!/bin/bash
# /root/alert_on_error.sh

LOG_FILE="/var/log/webdav-error.log"
LAST_CHECK="/tmp/webdav_last_check"

# Get timestamp of last check
if [ -f "$LAST_CHECK" ]; then
    SINCE=$(cat "$LAST_CHECK")
else
    SINCE=$(date -d "1 hour ago" +%s)
fi

# Check for errors since last check
ERROR_COUNT=$(journalctl -u webdav-api -u webdav-web --since "@$SINCE" -p err | wc -l)

if [ "$ERROR_COUNT" -gt 0 ]; then
    echo "⚠️ WebDAV Uploader Alert: $ERROR_COUNT errors detected"
    # Send email (configure mail server)
    # mail -s "WebDAV Alert" admin@example.com < error_details.txt
fi

# Update last check timestamp
date +%s > "$LAST_CHECK"
```

---

## 🔧 Troubleshooting

### Časté problémy a řešení

#### 1. API Server se nespouští

**Příznaky:**
```bash
curl: (7) Failed to connect to localhost port 5000: Connection refused
```

**Diagnóza:**
```bash
# Kontrola služby
systemctl status webdav-api

# Kontrola logů
journalctl -u webdav-api -n 20

# Kontrola portu
netstat -tlnp | grep 5000
```

**Řešení:**
```bash
# Kontrola konfigurace
cat /root/webdav_config.env

# Test manuálního spuštění
source /root/venv/bin/activate
python3 /root/webdav_uploader.py

# Restart služby
systemctl restart webdav-api
```

#### 2. WebDAV připojení selhává

**Příznaky:**
```json
{"error": "Chyba připojení k WebDAV serveru"}
```

**Diagnóza:**
```bash
# Test WebDAV připojení
curl -u username:password https://webdav-server.com/

# Kontrola DNS
nslookup webdav-server.com

# Test z serveru
wget --spider https://webdav-server.com/
```

**Řešení:**
```bash
# Ověření credentials v config
nano /root/webdav_config.env

# Test jiného WebDAV klienta
pip install webdavclient3
python3 -c "
from webdav3.client import Client
options = {'webdav_hostname': 'https://your-server.com', 'webdav_login': 'user', 'webdav_password': 'pass'}
client = Client(options)
print(client.list('/'))
"
```

#### 3. Upload souborů selhává

**Příznaky:**
```json
{"error": "Nepodporovaný typ souboru"}
```

**Diagnóza:**
```bash
# Kontrola povoleních typů
curl -u user:pass http://localhost:5000/config

# Test s jednoduchým souborem
echo "test" > test.txt
curl -u user:pass -F 'file=@test.txt' http://localhost:5000/upload
```

**Řešení:**
```python
# Přidání nového typu do ALLOWED_EXTENSIONS
ALLOWED_EXTENSIONS.add('new_extension')
```

#### 4. Webové rozhraní nedostupné

**Příznaky:**
```bash
curl: (7) Failed to connect to localhost port 11001: Connection refused
```

**Diagnóza:**
```bash
# Kontrola služby
systemctl status webdav-web

# Kontrola procesu
ps aux | grep webdav_web_interface

# Test manuálního spuštění
python3 /root/webdav_web_interface.py
```

#### 5. Databáze poškozena

**Příznaky:**
```
sqlite3.DatabaseError: database disk image is malformed
```

**Řešení:**
```bash
# Backup current database
cp /root/webdav_users.db /root/webdav_users.db.backup

# Try to repair
sqlite3 /root/webdav_users.db ".dump" | sqlite3 /root/webdav_users_new.db
mv /root/webdav_users_new.db /root/webdav_users.db

# Or restore from backup
cp /opt/backups/webdav/users_YYYYMMDD_HHMMSS.db /root/webdav_users.db
```

### Debug mode

#### Zapnutí debug módu
```bash
# V webdav_config.env
DEBUG=True

# Restart služeb
systemctl restart webdav-api webdav-web
```

#### Verbose logování
```python
# V Python kódu
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Performance tuning

#### Pro velké soubory
```python
# Zvýšení limitů
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB

# Timeout pro WebDAV
webdav_timeout = 300  # 5 minut
```

#### Pro více uživatelů
```python
# Použití production WSGI serveru
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 webdav_uploader:app
```

---

## ❓ FAQ

### Obecné otázky

**Q: Jak změním heslo pro admin účet?**
```bash
# Přes webové rozhraní: Uživatelé -> Edit -> Admin
# Nebo přímo v databázi:
sqlite3 /root/webdav_users.db "UPDATE users SET password_hash = '...' WHERE username = 'admin'"
```

**Q: Jak přidám nový typ souboru?**
```python
# V /root/webdav_uploader.py
ALLOWED_EXTENSIONS.add('new_extension')
```

**Q: Jak zvýším limit velikosti souboru?**
```python
# V /root/webdav_uploader.py
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
```

**Q: Jak nastavím HTTPS?**
```python
# Použijte reverse proxy (nginx/apache) nebo:
app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')
```

### Bezpečnostní otázky

**Q: Je systém bezpečný pro produkci?**
- ✅ Ano, obsahuje všechna základní bezpečnostní opatření
- ⚠️ Doporučujeme HTTPS pro produkci
- ⚠️ Pravidelné aktualizace a monitoring

**Q: Jak resetovat uzamčený účet?**
```sql
-- Přes sqlite3
UPDATE users SET failed_attempts = 0, locked_until = NULL WHERE username = 'user';
```

**Q: Jak sledovat bezpečnostní události?**
```bash
# Přes webové rozhraní: Logy -> filtr podle akce
# Nebo přímo v databázi:
sqlite3 /root/webdav_users.db "SELECT * FROM access_logs WHERE success = 0"
```

### Technické otázky

**Q: Jak integrovat s jiným WebDAV serverem?**
```bash
# Změna konfigurace v webdav_config.env
WEBDAV_HOSTNAME=https://new-server.com
WEBDAV_LOGIN=new_user
WEBDAV_PASSWORD=new_password
```

**Q: Jak přidat vlastní autentifikaci?**
```python
# Implementace custom auth provideru
def custom_authenticate(username, password):
    # LDAP, OAuth, database, atd.
    return True/False
```

**Q: Jak škálovat pro více uživatelů?**
```bash
# Použijte load balancer + více instancí
# PostgreSQL místo SQLite pro databázi
# Redis pro session storage
```

### Troubleshooting otázky

**Q: Proč se upload zasekává?**
- Kontrola síťového připojení k WebDAV
- Kontrola velikosti souboru vs. limit
- Kontrola dostupného místa na serveru

**Q: Proč nefunguje přihlášení?**
- Kontrola credentials v databázi
- Kontrola uzamčení účtu
- Kontrola session timeout

**Q: Jak obnovit výchozí nastavení?**
```bash
# Smazání databáze (vytvoří se nová s admin účtem)
rm /root/webdav_users.db
systemctl restart webdav-web
```

---

## 📞 Podpora a kontakt

### Dokumentace
- **Tato dokumentace**: `/root/COMPLETE_DOCUMENTATION.md`
- **README**: `/root/README_webdav_uploader.md`  
- **PDF návod**: `WebDAV_Uploader_Guide.pdf`

### Logy a diagnostika
```bash
# Systémové logy
journalctl -u webdav-api -u webdav-web

# Aplikační logy
tail -f /var/log/webdav-*.log

# Databázové dotazy
sqlite3 /root/webdav_users.db ".schema"
```

### Užitečné příkazy
```bash
# Kompletní restart
systemctl restart webdav-api webdav-web

# Health check
curl http://localhost:5000/health
curl -I http://localhost:11001

# Backup před změnami
tar -czf webdav_backup_$(date +%Y%m%d).tar.gz /root/webdav_* /root/templates/
```

---

**Verze dokumentace:** 1.0  
**Datum:** 2025-07-05  
**Autor:** Claude AI Assistant  
**Licence:** MIT License

---

*Tato dokumentace je živý dokument. Pro nejnovější verzi a aktualizace sledujte změny v projektu.*