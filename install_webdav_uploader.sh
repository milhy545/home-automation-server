#!/bin/bash

# WebDAV Uploader Installation Script
# Installs dependencies and configures WebDAV uploader

echo "🚀 Installing WebDAV Uploader..."

# Install Python dependencies
echo "📦 Installing Python packages..."
pip3 install -r requirements.txt

# Set permissions
chmod +x webdav_uploader.py

# Create systemd service
echo "⚙️ Creating systemd service..."
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

echo "✅ Installation completed!"
echo ""
echo "📋 Next steps:"
echo "1. Edit configuration in: /root/webdav_config.env"
echo "2. Start the service: systemctl start webdav-uploader"
echo "3. Enable autostart: systemctl enable webdav-uploader"
echo ""
echo "🔧 Testing:"
echo "python3 webdav_uploader.py"
echo ""
echo "📡 API endpoints:"
echo "- GET  /health - health check"
echo "- POST /upload - file upload"
echo "- GET  /list   - list files"
echo "- GET  /config - show configuration"
echo ""
echo "🔐 Authentication: Basic Auth"
echo "- perplexity:secure-password-123"
echo "- admin:admin-password-456"