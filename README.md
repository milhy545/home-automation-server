# 🏠 Home Automation Server Configuration / Konfigurace Domácí Automatizace

---
🇬🇧 **English** | 🇨🇿 **Česky**
---

> **Production Server**: `192.168.0.58:2222` - Complete infrastructure as code  
> **Produkční Server**: `192.168.0.58:2222` - Kompletní infrastruktura jako kód

**English**: This repository contains the complete configuration and codebase for a production home automation server running on Alpine Linux. The server orchestrates 15+ Docker services and provides a comprehensive AI-integrated smart home platform.

**Česky**: Tento repozitář obsahuje kompletní konfiguraci a kódovou základnu pro produkční server domácí automatizace běžící na Alpine Linux. Server orchestruje 15+ Docker služeb a poskytuje komplexní AI-integrovanou platformu smart home.

## 🏗️ **Architecture Overview**

### **Server Specifications**
- **OS**: Alpine Linux (lightweight, security-focused)
- **IP**: 192.168.0.58 (local network)
- **SSH**: Port 2222 (key-based authentication)
- **Services**: 15+ Docker containers
- **Uptime**: 24/7 production environment

### **Core Services**

#### **🤖 MCP API Cluster (Ports 8001-8008)**
Containerized Model Context Protocol servers providing AI integration:

- **8001**: Enhanced Filesystem MCP - File operations with memory tracking
- **8002**: Git MCP - Version control operations
- **8003**: Enhanced Terminal MCP - Secure command execution
- **8004**: Database MCP - SQL operations and data management
- **8005**: Research MCP - Perplexity AI integration
- **8007**: Memory MCP - Advanced memory systems
- **8008**: Qdrant Vector Database - AI embeddings and semantic search

#### **🏠 Home Automation (Ports 10001-10003)**
- **10001**: Portainer - Docker container management
- **10002**: Home Assistant - Smart home automation platform
- **10003**: AdGuard Home - DNS filtering and ad blocking

#### **🌐 Network Services**
- **53**: DNS (AdGuard Home)
- **443/853**: HTTPS/DNS-over-TLS
- **5443**: DNS-over-HTTPS
- **6060**: Go2RTC - Real-time media streaming

## 📁 **Directory Structure**

```
/root/
├── archived-mcp-servers-20250723/    # MCP server backups
├── fei/                              # FEI AI assistant framework
├── perplexity-ha-integration/        # Perplexity AI integration
├── perplexity-ha-control/            # Perplexity control scripts
├── test-repo/                        # Testing environment
├── templates/                        # Configuration templates
├── COMPLETE_DOCUMENTATION.md         # Full system documentation
├── HAS-SERVER-SUMMARY.md            # Server summary
├── WebDAV_Uploader_PDF_Guide.md     # WebDAV integration guide
├── webdav_uploader.py               # WebDAV upload functionality
├── webdav_web_interface.py          # WebDAV web interface
├── claude-status.sh                 # System status monitoring
├── setup-claude-api.sh              # API setup automation
└── Various configuration scripts
```

## 🐳 **Docker Infrastructure**

### **Container Orchestration**
All services run in Docker containers with:
- **Restart Policy**: `unless-stopped`
- **Networking**: Bridge mode with port mapping
- **Volumes**: Shared data persistence
- **Health Checks**: Automatic service monitoring

### **Service Management**
- **Portainer**: Web-based container management
- **Auto-restart**: Failed containers automatically restart
- **Resource Limits**: CPU/memory constraints per service
- **Logging**: Centralized container logging

## 🔐 **Security Configuration**

### **Network Security**
- **SSH**: Key-based authentication only (no passwords)
- **Firewall**: Selective port opening
- **DNS Filtering**: AdGuard Home blocks malicious domains
- **SSL/TLS**: Encrypted communications where applicable

### **Access Control**
- **Multi-user**: Separate user contexts for services
- **Container Isolation**: Services run in isolated containers
- **Volume Permissions**: Restricted file system access
- **API Security**: Token-based authentication for APIs

## 🤖 **AI Integration Features**

### **Multi-Provider Support**
- **Anthropic Claude**: Advanced reasoning and coding
- **OpenAI**: GPT models for various tasks
- **Perplexity**: Research and real-time information

### **Memory Systems**
- **Vector Database**: Qdrant for semantic search
- **Session Memory**: Persistent conversation context
- **Knowledge Base**: Accumulated system knowledge

### **Automation**
- **Smart Responses**: Context-aware AI responses
- **Process Optimization**: AI-driven system optimization
- **Adaptive Learning**: System learns from usage patterns

## 🛠️ **Key Scripts & Tools**

### **System Management**
- `claude-status.sh` - System health monitoring
- `setup-claude-api.sh` - API configuration automation
- `install_webdav_uploader.sh` - WebDAV setup

### **WebDAV Integration**
- `webdav_uploader.py` - File upload functionality
- `webdav_web_interface.py` - Web-based file management
- `webdav_config.env` - Configuration templates

### **Testing & Validation**
- `test_perplexity_key.py` - API key validation
- `test_webdav_uploader.py` - WebDAV functionality testing

## 📊 **Performance Metrics**

### **Resource Utilization**
- **CPU Usage**: Optimized for low-power hardware
- **Memory**: Efficient container resource management
- **Storage**: Minimal Alpine Linux footprint
- **Network**: High-throughput API processing

### **Service Reliability**
- **Uptime**: 99%+ availability
- **Response Time**: Sub-second API responses
- **Error Rate**: <1% service failures
- **Recovery Time**: Automatic restart within 30 seconds

## 🚀 **Deployment**

### **Prerequisites**
- Alpine Linux host system
- Docker and Docker Compose
- SSH key-based access
- Network configuration (static IP recommended)

### **Installation**
1. Clone this repository to your server
2. Configure environment variables (see templates)
3. Run setup scripts for each service
4. Deploy containers using Docker Compose
5. Configure network routing and firewall

### **Configuration**
- Copy template files and customize for your environment
- Update API keys and credentials
- Configure network settings and port mappings
- Set up backup and monitoring

## 🔄 **Maintenance**

### **Regular Tasks**
- Container health monitoring
- Log rotation and cleanup  
- Security updates for base images
- Backup of configuration and data

### **Monitoring**
- System resource usage
- Container status and health
- API response times and error rates
- Network connectivity and performance

## 📚 **Documentation**

Detailed documentation available in:
- `COMPLETE_DOCUMENTATION.md` - Full system documentation
- `HAS-SERVER-SUMMARY.md` - Server overview and status
- `WebDAV_Uploader_PDF_Guide.md` - WebDAV integration guide

## 🎯 **Use Cases**

### **Development Environment**
- Remote AI-powered development
- Git operations and code management
- Database operations and testing
- Research and documentation

### **Home Automation**
- Smart device control and monitoring
- Network-wide ad blocking and DNS filtering  
- Media streaming and content management
- System monitoring and alerts

### **AI Integration**
- Multi-provider AI access
- Persistent memory and context
- Automated system optimization
- Research and information processing

## 🏆 **Architecture Benefits**

### **Modularity**
- Each service runs independently
- Easy to add, remove, or update services
- Isolated failure domains
- Scalable architecture

### **Efficiency** 
- Minimal resource footprint
- Optimized for low-power hardware
- Fast startup and response times
- Efficient network utilization

### **Reliability**
- Automatic service recovery
- Health monitoring and alerting
- Backup and disaster recovery
- High availability design

---

## ⚠️ **Important Notes**

### **Privacy & Security**
- This repository contains **PUBLIC** configuration files only
- All databases, memory files, and personal data are excluded
- SSH keys, API credentials, and secrets are not included
- Environment files contain templates only - configure with your own values

### **Setup Requirements**
- You'll need to provide your own API keys for AI services
- Configure SSH keys for secure access
- Set up your own database and memory storage
- Customize network configuration for your environment

### **Production Ready**
This is a **live production configuration** running 24/7. All services are tested and optimized for reliability and performance.

---

**🚀 Ready to deploy your own AI-integrated Home Automation Server!**

*For questions or support, see the documentation files or create an issue.*