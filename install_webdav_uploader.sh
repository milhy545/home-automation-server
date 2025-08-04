#!/bin/bash

# WebDAV Uploader Installation Script
# Instaluje závislosti a nastavuje WebDAV uploader

echo "🚀 Instalace WebDAV Uploader..."

# Instalace Python závislostí
echo "📦 Instalace Python balíčků..."
pip3 install -r requirements.txt

# Nastavení práv
chmod +x webdav_uploader.py

# Vytvoření systemd služby
echo "⚙️ Vytváření systemd služby..."
cat > /etc/systemd/system/webdav-uploader.service << 'EOF'
[Unit]
Description=WebDAV Uploader API Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root
Environment=PYTHONPATH=/root
EnvironmentFile=/root/webdav_config.env
ExecStart=/usr/bin/python3 /root/webdav_uploader.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
systemctl daemon-reload

echo "✅ Instalace dokončena!"
echo ""
echo "📋 Další kroky:"
echo "1. Upravte konfiguraci v: /root/webdav_config.env"
echo "2. Spusťte službu: systemctl start webdav-uploader"
echo "3. Povolte autostart: systemctl enable webdav-uploader"
echo ""
echo "🔧 Testování:"
echo "python3 webdav_uploader.py"
echo ""
echo "📡 API endpoints:"
echo "- GET  /health - kontrola stavu"
echo "- POST /upload - nahrání souboru"
echo "- GET  /list   - výpis souborů"
echo "- GET  /config - zobrazení konfigurace"
echo ""
echo "🔐 Autentifikace: Basic Auth"
echo "- perplexity:secure-password-123"
echo "- admin:admin-password-456"