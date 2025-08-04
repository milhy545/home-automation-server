# WebDAV Uploader API Server

## Přehled

Tento Python skript vytváří Flask API server, který umožňuje Perplexity Assistantovi ukládat výstupy přímo do WebDAV složky na serveru.

## Funkce

- ✅ **API endpoint** pro příjem dat přes HTTP POST
- ✅ **Ověření uživatele** pomocí Basic Auth
- ✅ **Nahrání do WebDAV** serveru s autentifikací
- ✅ **Konfigurace** cesty k WebDAV serveru a adresáře
- ✅ **Bezpečnostní opatření** - sanitizace názvů, kontrola typů
- ✅ **Podpora různých formátů** - multipart/form-data i JSON
- ✅ **Logování** a monitoring
- ✅ **Systemd integrace** pro produkční nasazení

## Instalace

```bash
# Spuštění instalačního skriptu
./install_webdav_uploader.sh

# Ruční instalace
pip3 install -r requirements.txt
```

## Konfigurace

Upravte `/root/webdav_config.env`:

```bash
# WebDAV Server Configuration  
WEBDAV_HOSTNAME=https://your-webdav-server.com
WEBDAV_LOGIN=username
WEBDAV_PASSWORD=password
WEBDAV_ROOT=/uploads/

# Server Configuration
PORT=5000
DEBUG=False
```

## Spuštění

### Development
```bash
python3 webdav_uploader.py
```

### Production (systemd)
```bash
systemctl start webdav-uploader
systemctl enable webdav-uploader
systemctl status webdav-uploader
```

## API Endpoints

### 1. Health Check
```bash
GET /health
```

### 2. Upload File (Multipart)
```bash
curl -u perplexity:secure-password-123 -X POST \
  -F 'file=@example.txt' \
  -F 'path=/subfolder' \
  http://localhost:5000/upload
```

### 3. Upload File (JSON)
```bash
curl -u perplexity:secure-password-123 -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "test.txt",
    "data": "SGVsbG8gV29ybGQ=",
    "path": "/subfolder"
  }' \
  http://localhost:5000/upload
```

### 4. List Files
```bash
curl -u perplexity:secure-password-123 \
  http://localhost:5000/list?path=/uploads/
```

### 5. Get Configuration
```bash
curl -u perplexity:secure-password-123 \
  http://localhost:5000/config
```

## Autentifikace

**Výchozí uživatelé:**
- `perplexity:secure-password-123`
- `admin:admin-password-456`

**Změna hesel:** Upravte slovník `USERS` v `/root/webdav_uploader.py`

## Podporované formáty

- **Text:** txt, md, json, xml, csv
- **Dokumenty:** pdf, doc, docx, xls, xlsx, ppt, pptx  
- **Obrázky:** png, jpg, jpeg, gif

## Bezpečnost

- ✅ Basic Auth autentifikace
- ✅ Sanitizace názvů souborů
- ✅ Kontrola povolených typů
- ✅ Omezení velikosti (50MB)
- ✅ Logování všech operací

## Monitoring

```bash
# Logy systemd služby
journalctl -u webdav-uploader -f

# Status služby
systemctl status webdav-uploader

# Kontrola zdraví
curl http://localhost:5000/health
```

## Troubleshooting

### Chyba připojení k WebDAV
- Zkontrolujte WEBDAV_HOSTNAME, LOGIN, PASSWORD
- Ověřte síťové připojení
- Zkuste manuální připojení přes webdav klienta

### Chyba autentifikace
- Zkontrolujte přihlašovací údaje v požadavku
- Ověřte formát Basic Auth

### Chyba nahrávání
- Zkontrolujte oprávnění na WebDAV serveru
- Ověřte, že cílová složka existuje
- Zkontrolujte velikost souboru (max 50MB)

## Příklady použití

### Python client
```python
import requests
import base64

# Nahrání souboru
with open('example.txt', 'rb') as f:
    files = {'file': f}
    response = requests.post(
        'http://localhost:5000/upload',
        files=files,
        auth=('perplexity', 'secure-password-123')
    )
    print(response.json())

# Nahrání přes JSON
data = {
    'filename': 'test.txt',
    'data': base64.b64encode(b'Hello World').decode(),
    'path': '/perplexity-outputs'
}
response = requests.post(
    'http://localhost:5000/upload',
    json=data,
    auth=('perplexity', 'secure-password-123')
)
print(response.json())
```

### Curl examples
```bash
# Nahrání s cestou
curl -u perplexity:secure-password-123 -X POST \
  -F 'file=@document.pdf' \
  -F 'path=/documents/2025' \
  http://localhost:5000/upload

# Výpis souborů
curl -u perplexity:secure-password-123 \
  http://localhost:5000/list

# Konfigurace
curl -u perplexity:secure-password-123 \
  http://localhost:5000/config
```

## Integrace s Perplexity

Server je připraven pro integraci s Perplexity Assistantem. Perplexity může používat API endpoints pro:

1. **Ukládání výstupů** - POST /upload
2. **Kontrolu dostupnosti** - GET /health  
3. **Správu souborů** - GET /list
4. **Monitorování** - GET /config

## Autor

Vytvořeno Claude AI Assistant na základě požadavků uživatele.
Datum: 2025-07-05