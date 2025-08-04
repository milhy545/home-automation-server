# WebDAV Uploader - Step-by-Step PDF Guide

## 📖 Návod krok za krokem s obrázky

### Obsah
1. [Přehled systému](#1-přehled-systému)
2. [Instalace](#2-instalace)
3. [První spuštění](#3-první-spuštění)
4. [Webové rozhraní](#4-webové-rozhraní)
5. [Nahrávání souborů](#5-nahrávání-souborů)
6. [Správa uživatelů](#6-správa-uživatelů)
7. [Konfigurace](#7-konfigurace)
8. [Monitoring](#8-monitoring)
9. [API použití](#9-api-použití)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Přehled systému

### Architektura systému

```
┌─────────────────────┐
│   Uživatel          │
│   (Web Browser)     │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐    ┌─────────────────────┐
│   Web Interface     │────│   API Server        │
│   Port 11001        │    │   Port 5000         │
│   (Flask)           │    │   (Flask)           │
└─────────┬───────────┘    └─────────┬───────────┘
          │                          │
          ▼                          ▼
┌─────────────────────┐    ┌─────────────────────┐
│   SQLite Database   │    │   WebDAV Server     │
│   (Users & Logs)    │    │   (External)        │
└─────────────────────┘    └─────────────────────┘
```

### Komponenty
- **API Server** - REST API pro upload (port 5000)
- **Web Interface** - Webová administrace (port 11001)
- **SQLite DB** - Uživatelé a logy
- **WebDAV Server** - Externí úložiště souborů

---

## 2. Instalace

### Krok 2.1: Příprava prostředí

**Terminal příkazy:**
```bash
# Přechod do root adresáře
cd /root

# Kontrola existujících souborů
ls -la webdav_*
```

**Očekávaný výstup:**
```
-rwxr-xr-x 1 root root  15234 Jul  5 20:00 webdav_uploader.py
-rwxr-xr-x 1 root root  25678 Jul  5 20:00 webdav_web_interface.py
-rw-r--r-- 1 root root     87 Jul  5 20:00 requirements.txt
-rwxr-xr-x 1 root root   2345 Jul  5 20:00 install_webdav_uploader.sh
```

### Krok 2.2: Instalace závislostí

**Vytvoření virtual environment:**
```bash
python3 -m venv /root/venv
source /root/venv/bin/activate
```

**Instalace Python balíčků:**
```bash
pip install -r requirements.txt
```

**Očekávaný výstup:**
```
Successfully installed Flask-2.3.3 webdavclient3-3.14.6 Werkzeug-2.3.7
```

### Krok 2.3: Konfigurace

**Editace konfiguračního souboru:**
```bash
nano /root/webdav_config.env
```

**Příklad konfigurace:**
```env
# WebDAV Server Configuration
WEBDAV_HOSTNAME=https://your-webdav-server.com
WEBDAV_LOGIN=webdav_username
WEBDAV_PASSWORD=webdav_password
WEBDAV_ROOT=/uploads/

# Server Configuration
PORT=5000
DEBUG=False
```

---

## 3. První spuštění

### Krok 3.1: Spuštění API serveru

**Aktivace virtual environment:**
```bash
source /root/venv/bin/activate
```

**Spuštění API serveru:**
```bash
python3 /root/webdav_uploader.py
```

**Očekávaný výstup:**
```
* Running on all addresses (0.0.0.0)
* Running on http://127.0.0.1:5000
* Running on http://192.168.0.58:5000
Press CTRL+C to quit
```

### Krok 3.2: Test API serveru

**Otevření nového terminálu a test:**
```bash
curl http://192.168.0.58:5000/health
```

**Očekávaný výstup:**
```json
{
  "status": "OK",
  "timestamp": "2025-07-05T20:00:00.000000",
  "version": "1.0.0"
}
```

### Krok 3.3: Spuštění webového rozhraní

**V novém terminálu:**
```bash
source /root/venv/bin/activate
python3 /root/webdav_web_interface.py
```

**Očekávaný výstup:**
```
🌐 WebDAV Web Interface starting on port 11001...
📊 Dashboard: http://192.168.0.58:11001
🔐 Default login: admin / admin123
* Running on all addresses (0.0.0.0)
* Running on http://192.168.0.58:11001
```

---

## 4. Webové rozhraní

### Krok 4.1: Přístup k webovému rozhraní

**Otevření v prohlížeči:**
```
http://192.168.0.58:11001
```

**Screenshot místo:**
```
┌─────────────────────────────────────────┐
│  WebDAV Uploader - Přihlášení           │
├─────────────────────────────────────────┤
│                                         │
│  🔐 Přihlášení                          │
│                                         │
│  Uživatelské jméno: [admin        ]    │
│  Heslo:            [••••••••••    ]    │
│                                         │
│  [    Přihlásit se    ]                │
│                                         │
│  WebDAV Uploader Manager v1.0           │
└─────────────────────────────────────────┘
```

### Krok 4.2: Přihlášení

**Přihlašovací údaje:**
- **Username:** admin
- **Password:** admin123

**Po úspěšném přihlášení se zobrazí dashboard:**

```
┌─────────────────────────────────────────────────────┐
│ WebDAV Manager                                       │
├─────────────────────────────────────────────────────┤
│ 🏠 Dashboard      │                                 │
│ 📤 Upload         │     📊 Dashboard                │
│ 📁 Soubory        │                                 │
│ ⚙️ Nastavení      │  ┌─────────┬─────────┬─────────┐│
│ 👥 Uživatelé     │  │API:✅   │Users:1  │Today:0  ││
│ 📋 Logy          │  │Online   │Active   │Logins   ││
│                   │  └─────────┴─────────┴─────────┘│
│ Přihlášen: admin  │                                 │
│ [Odhlásit]        │  🚀 Rychlé akce:               │
│                   │  [📤 Nahrát soubor]            │
│                   │  [📁 Spravovat soubory]        │
└─────────────────────────────────────────────────────┘
```

---

## 5. Nahrávání souborů

### Krok 5.1: Přístup k upload stránce

**Kliknutí na "Upload" v menu nebo na "Nahrát soubor" na dashboardu.**

**Upload rozhraní:**
```
┌─────────────────────────────────────────────────────┐
│ 📤 Nahrávání souborů                                │
├─────────────────────────────────────────────────────┤
│                                         │           │
│  Vyberte soubor:                       │  ℹ️ Info   │
│  [Procházet soubory...]                │           │
│                                         │ Formáty:  │
│  Cesta (volitelně):                    │ • PDF,DOC │
│  [/subfolder              ]            │ • XLS,PPT │
│                                         │ • TXT,MD  │
│  [📤 Nahrát soubor]                    │ • PNG,JPG │
│                                         │           │
│  ████████████████████████████████████   │ Limity:   │
│  90% - Nahrávání...                    │ • 50 MB   │
│                                         │ • 30s     │
└─────────────────────────────────────────────────────┘
```

### Krok 5.2: Výběr souboru

**Postupy:**
1. Kliknutí na "Procházet soubory..."
2. Výběr souboru z počítače
3. Volitelné zadání cesty (např. `/dokumenty/2025`)
4. Kliknutí na "Nahrát soubor"

**Podporované formáty:**
- **Dokumenty:** PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX
- **Text:** TXT, MD, JSON, XML, CSV
- **Obrázky:** PNG, JPG, JPEG, GIF

### Krok 5.3: Úspěšné nahrání

**Po úspěšném nahrání:**
```
┌─────────────────────────────────────────┐
│ ✅ Úspěch                               │
│ Soubor "dokument.pdf" byl úspěšně       │
│ nahrán do "/uploads/dokumenty/".        │
│                                         │
│ [OK]                                    │
└─────────────────────────────────────────┘
```

---

## 6. Správa uživatelů

### Krok 6.1: Přístup ke správě uživatelů

**Kliknutí na "Uživatelé" v menu (pouze pro admin).**

**Seznam uživatelů:**
```
┌─────────────────────────────────────────────────────┐
│ 👥 Správa uživatelů               [+ Přidat uživatele]│
├─────────────────────────────────────────────────────┤
│ Jméno  │Email        │Role   │Status   │Vytvořen     │Akce│
├─────────────────────────────────────────────────────┤
│ admin  │admin@local  │Admin  │✅Aktivní│2025-07-05  │✏️❌│
│ user1  │user1@test   │User   │✅Aktivní│2025-07-05  │✏️⏸️❌│
│ user2  │user2@test   │User   │⏸️Pozast.│2025-07-04  │✏️▶️❌│
└─────────────────────────────────────────────────────┘
```

### Krok 6.2: Přidání nového uživatele

**Kliknutí na "Přidat uživatele":**

**Modal dialog:**
```
┌─────────────────────────────────────────┐
│ ➕ Přidat nového uživatele              │
├─────────────────────────────────────────┤
│ Uživatelské jméno: [newuser      ]     │
│ Email:            [user@email.com]     │
│ Heslo:            [••••••••••    ]     │
│ Potvrdit heslo:   [••••••••••    ]     │
│                                         │
│ ☐ Admin práva                          │
│                                         │
│ [Zrušit]           [➕ Přidat uživatele]│
└─────────────────────────────────────────┘
```

### Krok 6.3: Editace uživatele

**Kliknutí na ✏️ u uživatele:**

**Edit dialog:**
```
┌─────────────────────────────────────────┐
│ ✏️ Upravit uživatele: user1             │
├─────────────────────────────────────────┤
│ Email:         [user1@test.com   ]     │
│ Nové heslo:    [                 ]     │
│ (nechte prázdné pro zachování)          │
│                                         │
│ ☑️ Admin práva                          │
│                                         │
│ [Zrušit]              [💾 Uložit změny] │
└─────────────────────────────────────────┘
```

---

## 7. Konfigurace

### Krok 7.1: Přístup k nastavení

**Kliknutí na "Nastavení" v menu (pouze pro admin).**

**Konfigurační rozhraní:**
```
┌─────────────────────────────────────────────────────┐
│ ⚙️ Nastavení systému                                │
├─────────────────────────────────────────────────────┤
│ 🔧 WebDAV konfigurace           │ ℹ️ Aktuální konfig │
│                                 │                   │
│ WebDAV Server:                  │ Server: webdav... │
│ [https://webdav-server.com]     │ Max size: 50 MB   │
│                                 │ Types: 12 formátů │
│ Username: [webdav_user    ]     │                   │
│ Password: [••••••••••     ]     │ 🛠️ Akce:          │
│                                 │ [🔄 Restart API]  │
│ Root folder: [/uploads/   ]     │ [🗑️ Clear logs]   │
│ Max size (MB): [50        ]     │ [📥 Export conf]  │
│                                 │                   │
│ [💾 Uložit] [📡 Test připojení] │                   │
└─────────────────────────────────────────────────────┘
```

### Krok 7.2: Test WebDAV připojení

**Kliknutí na "Test připojení":**

**Loading stav:**
```
┌─────────────────────────────────────────┐
│ 📡 Testování připojení...              │
│ ⏳ Připojování k WebDAV serveru...      │
└─────────────────────────────────────────┘
```

**Výsledek:**
```
┌─────────────────────────────────────────┐
│ ✅ Test připojení úspěšný               │
│ Server odpověděl správně.               │
│ Přístup k /uploads/ ověřen.             │
│                                         │
│ [OK]                                    │
└─────────────────────────────────────────┘
```

### Krok 7.3: Bezpečnostní nastavení

**Sekce bezpečnostní nastavení:**
```
┌─────────────────────────────────────────┐
│ 🛡️ Bezpečnostní nastavení              │
├─────────────────────────────────────────┤
│ Max. pokusů o přihlášení: [5   ]       │
│ Doba uzamčení (min):      [30  ]       │
│ Timeout relace (h):       [24  ]       │
│                                         │
│ ☑️ Povolit logování přístupů           │
│                                         │
│ [🛡️ Uložit bezpečnostní nastavení]     │
└─────────────────────────────────────────┘
```

---

## 8. Monitoring

### Krok 8.1: Zobrazení logů

**Kliknutí na "Logy" v menu:**

**Log rozhraní:**
```
┌─────────────────────────────────────────────────────┐
│ 📋 Systémové logy                   [🔄][📥][🗑️]   │
├─────────────────────────────────────────────────────┤
│ 🔍 Filtry:                                         │
│ User:[všichni▼] Akce:[všechny▼] Výsledek:[všechny▼]│
│                                                     │
│ Čas     │User │IP          │Akce      │Výsledek│Det│
├─────────────────────────────────────────────────────┤
│20:15:23 │admin│192.168.0.50│Login     │✅      │OK │
│20:14:15 │user1│192.168.0.51│Upload    │✅      │PDF│
│20:13:45 │user2│192.168.0.52│Login     │❌      │Fail│
│20:12:33 │admin│192.168.0.50│Config    │✅      │Edit│
│                                                     │
│ 📊 Statistiky: ✅ 85 Úspěch | ❌ 12 Chyba          │
└─────────────────────────────────────────────────────┘
```

### Krok 8.2: Filtrování logů

**Použití filtrů:**
1. **User filter** - výběr konkrétního uživatele
2. **Action filter** - typ akce (login, upload, config)
3. **Result filter** - úspěšné/neúspěšné operace
4. **Date filter** - datum

**Filtrovaný výsledek:**
```
┌─────────────────────────────────────────────────────┐
│ 🔍 Filtry: User:[user1] Akce:[upload] Výsledek:[❌] │
├─────────────────────────────────────────────────────┤
│ Čas     │User │IP          │Akce      │Výsledek│Det│
├─────────────────────────────────────────────────────┤
│20:10:15 │user1│192.168.0.51│Upload    │❌      │Size│
│19:45:23 │user1│192.168.0.51│Upload    │❌      │Type│
│                                                     │
│ 📊 Zobrazeno: 2 z 97 záznamů                       │
└─────────────────────────────────────────────────────┘
```

### Krok 8.3: Export logů

**Kliknutí na 📥 (Export):**

**Export dialog:**
```
┌─────────────────────────────────────────┐
│ 📥 Export logů                          │
├─────────────────────────────────────────┤
│ Formát: [CSV ▼]                        │
│ Období: [Poslední týden ▼]             │
│ Filtry: [Aplikovat současné ▼]         │
│                                         │
│ [Zrušit]              [📥 Stáhnout CSV]│
└─────────────────────────────────────────┘
```

---

## 9. API použití

### Krok 9.1: Základní API testy

**Health check přes curl:**
```bash
curl http://192.168.0.58:5000/health
```

**Očekávaný výstup:**
```json
{
  "status": "OK",
  "timestamp": "2025-07-05T20:30:00.000000",
  "version": "1.0.0"
}
```

### Krok 9.2: Upload souboru přes API

**Multipart upload:**
```bash
curl -u perplexity:secure-password-123 -X POST \
  -F 'file=@document.pdf' \
  -F 'path=/dokumenty' \
  http://192.168.0.58:5000/upload
```

**Očekávaný výstup:**
```json
{
  "message": "Soubor úspěšně nahrán",
  "filename": "document.pdf",
  "remote_path": "/uploads/dokumenty/document.pdf",
  "size": 1048576
}
```

### Krok 9.3: JSON upload

**Base64 encoded upload:**
```bash
# Příprava base64 dat
echo "Hello World" | base64

curl -u perplexity:secure-password-123 -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "test.txt",
    "data": "SGVsbG8gV29ybGQK",
    "path": "/test"
  }' \
  http://192.168.0.58:5000/upload
```

### Krok 9.4: Seznam souborů

**List files API:**
```bash
curl -u perplexity:secure-password-123 \
  http://192.168.0.58:5000/list?path=/uploads/dokumenty
```

**Očekávaný výstup:**
```json
{
  "path": "/uploads/dokumenty",
  "files": [
    "document.pdf",
    "presentation.pptx",
    "spreadsheet.xlsx"
  ]
}
```

### Krok 9.5: Konfigurace API

**Get config:**
```bash
curl -u perplexity:secure-password-123 \
  http://192.168.0.58:5000/config
```

**Očekávaný výstup:**
```json
{
  "webdav_config": {
    "webdav_hostname": "https://webdav-server.com",
    "webdav_login": "user",
    "webdav_password": "***",
    "webdav_root": "/uploads/"
  },
  "allowed_extensions": ["pdf", "docx", "txt", "jpg"],
  "max_file_size": 52428800
}
```

---

## 10. Troubleshooting

### Krok 10.1: API server se nespouští

**Problém:** API server na portu 5000 neodpovídá.

**Diagnóza:**
```bash
# Kontrola procesu
ps aux | grep webdav_uploader

# Kontrola portu
netstat -tlnp | grep 5000

# Test manuálního spuštění
source /root/venv/bin/activate
python3 /root/webdav_uploader.py
```

**Možné chyby a řešení:**

**Chyba: Port již používán**
```
OSError: [Errno 98] Address already in use
```
**Řešení:**
```bash
# Nalezení procesu na portu 5000
sudo lsof -i :5000
# Ukončení procesu
sudo kill -9 <PID>
```

**Chyba: Chybí dependencies**
```
ModuleNotFoundError: No module named 'webdav3'
```
**Řešení:**
```bash
source /root/venv/bin/activate
pip install -r requirements.txt
```

### Krok 10.2: WebDAV připojení selhává

**Problém:** Upload vrací chybu "Chyba připojení k WebDAV serveru".

**Diagnóza:**
```bash
# Test WebDAV serveru
curl -u username:password https://webdav-server.com/

# Kontrola konfigurace
cat /root/webdav_config.env

# Test z Python konzole
python3 -c "
from webdav3.client import Client
options = {'webdav_hostname': 'https://server.com', 'webdav_login': 'user', 'webdav_password': 'pass'}
client = Client(options)
print(client.list('/'))
"
```

**Možné problémy:**

**Neplatné credentials:**
```
webdav3.exceptions.WebDavException: 401 Unauthorized
```
**Řešení:** Ověřit username/password v config souboru.

**Neexistující server:**
```
webdav3.exceptions.WebDavException: No connection with https://server.com
```
**Řešení:** Ověřit URL a dostupnost serveru.

### Krok 10.3: Web interface nedostupné

**Problém:** Webové rozhraní na portu 11001 neodpovídá.

**Diagnóza:**
```bash
# Kontrola procesu
ps aux | grep webdav_web_interface

# Kontrola portu
netstat -tlnp | grep 11001

# Kontrola logů
tail -f /var/log/webdav-web.log
```

**Test přístupu:**
```bash
curl -I http://192.168.0.58:11001
```

**Očekávaný výstup:**
```
HTTP/1.1 302 FOUND
Location: http://192.168.0.58:11001/login
```

### Krok 10.4: Databázové problémy

**Problém:** Chyby s uživatelskou databází.

**Kontrola databáze:**
```bash
# Kontrola existence
ls -la /root/webdav_users.db

# Test databáze
sqlite3 /root/webdav_users.db ".schema"
```

**Oprava poškozené databáze:**
```bash
# Backup
cp /root/webdav_users.db /root/webdav_users.db.backup

# Oprava
sqlite3 /root/webdav_users.db ".dump" | sqlite3 /root/webdav_users_new.db
mv /root/webdav_users_new.db /root/webdav_users.db
```

### Krok 10.5: Upload problémy

**Problém:** Soubory se nenahrávají.

**Časté chyby:**

**Příliš velký soubor:**
```json
{"error": "Soubor je příliš velký"}
```
**Řešení:** Zvětšit `MAX_CONTENT_LENGTH` nebo zmenšit soubor.

**Nepodporovaný typ:**
```json
{"error": "Nepodporovaný typ souboru"}
```
**Řešení:** Přidat příponu do `ALLOWED_EXTENSIONS`.

**WebDAV chyba:**
```json
{"error": "Chyba při nahrávání: 403 Forbidden"}
```
**Řešení:** Ověřit oprávnění na WebDAV serveru.

### Krok 10.6: Debug mode

**Zapnutí debug módu:**
```bash
# V webdav_config.env
DEBUG=True

# Restart služeb
systemctl restart webdav-api webdav-web
```

**Verbose logování:**
```python
# Přidat do Python souborů
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📋 Checklist pro instalaci

### ✅ Pre-installation
- [ ] Alpine Linux 3.19 nainstalován
- [ ] Python 3.11+ dostupný
- [ ] Síťové připojení funkční
- [ ] Dostatečný disk space (min 1GB)

### ✅ Installation steps
- [ ] Virtual environment vytvořen
- [ ] Dependencies nainstalovány
- [ ] Konfigurační soubor upraven
- [ ] WebDAV server nakonfigurován
- [ ] Firewall pravidla nastavena

### ✅ Testing
- [ ] API health check prošel
- [ ] Web interface dostupné
- [ ] Přihlášení admin účtem funguje
- [ ] Test upload souboru úspěšný
- [ ] WebDAV připojení ověřeno

### ✅ Production setup
- [ ] Systemd služby vytvořeny
- [ ] Auto-start nastaven
- [ ] Backup strategie implementována
- [ ] Monitoring nastaveno
- [ ] Logy nakonfigurovány

---

## 🔗 Užitečné odkazy a příkazy

### Rychlé příkazy
```bash
# Status check
curl http://192.168.0.58:5000/health
curl -I http://192.168.0.58:11001

# Restart služeb
systemctl restart webdav-api webdav-web

# Zobrazení logů
journalctl -u webdav-api -f
tail -f /var/log/webdav-web.log

# Backup
tar -czf webdav_backup_$(date +%Y%m%d).tar.gz /root/webdav_*
```

### Přístupové údaje
- **Web Interface:** http://192.168.0.58:11001
- **API Endpoint:** http://192.168.0.58:5000
- **Default Login:** admin / admin123
- **API Auth:** perplexity:secure-password-123

### Soubory
- **API Server:** `/root/webdav_uploader.py`
- **Web Interface:** `/root/webdav_web_interface.py`
- **Config:** `/root/webdav_config.env`
- **Database:** `/root/webdav_users.db`
- **Tests:** `/root/test_webdav_uploader.py`

---

**Verze návodu:** 1.0  
**Datum:** 2025-07-05  
**Pro:** WebDAV Uploader System  
**Autor:** Claude AI Assistant

---

*Tento návod obsahuje všechny potřebné kroky pro úspěšnou instalaci, konfiguraci a používání WebDAV Uploader systému. Pro nejnovější verzi dokumentace sledujte změny v projektu.*