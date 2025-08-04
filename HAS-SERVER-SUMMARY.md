# HAS Server Complete Setup Summary

**Server:** 192.168.0.58 (Home Automation Server)  
**OS:** Alpine Linux 3.19  
**Hardware:** AMD E-300 APU, 4GB RAM  
**Date:** July 5, 2025  

## 🔧 System Configuration

### Base System
- **Alpine Linux 3.19** clean installation
- **SSH Server** on port 2222 (security hardened)
- **Firewall configured** with iptables (only necessary ports open)
- **Docker & Docker Compose** installed and running
- **System optimization** for 4GB RAM environment

### Network Configuration
- **Hostname:** has-server
- **IP:** 192.168.0.58 (static DHCP)
- **DNS:** 8.8.8.8, 8.8.4.4
- **Timezone:** Europe/Prague

## 🐳 Docker Services

### 1. Portainer (Container Management)
- **URL:** http://192.168.0.58:10001
- **HTTPS:** https://192.168.0.58:19443
- **Credentials:** milhy777 / Admin123Pass
- **Security:** Firewall restricted to local network, no-new-privileges
- **Data:** Docker volume `portainer_data`

### 2. Home Assistant (Home Automation)
- **URL:** http://192.168.0.58:10002
- **Mount:** /opt/homeassistant/config:/config
- **Memory limit:** 1GB (optimized for 4GB RAM)
- **Status:** Running, needs initial configuration

### 3. AdGuard Home (DNS Filtering)
- **URL:** http://192.168.0.58:10003
- **DNS:** 192.168.0.58:53 (UDP/TCP)
- **Config:** /opt/adguard/conf
- **Work data:** /opt/adguard/work
- **Memory limit:** 256MB

## 🛡️ Security Hardening

### SSH Configuration
- **Port:** 2222 (non-standard)
- **Root login:** Disabled
- **Password auth:** Disabled (key-based only)
- **User:** milhy777 with sudo privileges

### Firewall Rules
```
Port 53   - AdGuard DNS (UDP/TCP)
Port 2222 - SSH
Port 8080 - Claude Code CLI
Port 10001 - Portainer
Port 10002 - Home Assistant  
Port 10003 - AdGuard Home
```

### User Management
- **Primary user:** milhy777 (sudo, docker groups)
- **Default password:** admin123 (force change on first login)
- **Shell:** zsh with Oh My Zsh

## 📁 Backup System

### Automated Backup
- **Location:** /opt/backups/
- **Scripts:** /opt/has-backup-system/
- **Schedule:** Daily 2:00 AM, Weekly Sunday 3:00 AM
- **Retention:** 30 days
- **Logs:** /var/log/has-backup.log

### Backup Components
- Home Assistant configuration
- AdGuard Home settings and data
- Portainer configuration
- Docker images
- System configuration files
- SSH keys and certificates

### Management Commands
```bash
backup-manager backup   # Manual backup
backup-manager restore  # Interactive restore
backup-manager status   # System status
backup-manager list     # List backups
backup-manager clean    # Clean old backups
```

## 🤖 Claude Code CLI

### Installation
- **Version:** 1.0.43 (latest)
- **Binary:** /usr/local/bin/claude-code
- **Alias:** claude-code (standard is 'claude')
- **Node.js:** v20.15.1
- **NPM:** 10.2.5

### Configuration
- **Config:** /root/.claude/settings.local.json
- **Permissions:** All tools allowed ("*")
- **Authentication:** OAuth (subscription-based)
- **Service:** OpenRC service available

### Usage
```bash
claude-code              # Interactive CLI
claude-code --help       # Show help
claude-code -p "prompt"  # Non-interactive
```

## 📊 System Monitoring

### Available Tools
- **Docker stats:** `docker stats`
- **System resources:** `htop`, `free -h`, `df -h`
- **Network:** `netstat -tlnp`
- **Logs:** `tail -f /var/log/messages`

### Status Scripts
- **Server status:** `/home/milhy777/server-status.sh`
- **Backup status:** `/opt/has-backup-system/backup-status.sh`
- **Claude status:** `/root/claude-status.sh`

## 🔗 Service URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| Portainer | http://192.168.0.58:10001 | milhy777 / Admin123Pass |
| Home Assistant | http://192.168.0.58:10002 | Setup required |
| AdGuard Home | http://192.168.0.58:10003 | Setup required |
| SSH Access | ssh milhy777@192.168.0.58 -p 2222 | Key-based |

## 🗂️ Important Directories

```
/opt/homeassistant/     - Home Assistant data
/opt/adguard/           - AdGuard Home data  
/opt/backups/           - Backup storage
/opt/has-backup-system/ - Backup scripts
/etc/ssh/               - SSH configuration
/etc/iptables/          - Firewall rules
/var/log/               - System logs
```

## ⚙️ System Optimization

### Memory Management
- **Swappiness:** 10 (minimal swap usage)
- **Cache pressure:** 50 (balanced caching)
- **Container limits:** Applied to prevent OOM

### CPU Optimization
- **Governor:** ondemand (power efficient)
- **Docker:** Optimized for 2-core AMD E-300

### Storage
- **File system:** EXT4
- **Docker storage:** overlay2 driver
- **Log rotation:** Configured (10MB max)

## 🔄 Recent Changes History

1. **System cleanup** - Removed unused services and packages
2. **Docker optimization** - Memory limits and security hardening
3. **Security hardening** - SSH, firewall, user permissions
4. **Service installation** - Portainer, Home Assistant, AdGuard
5. **Backup system** - Automated backup and restore capabilities
6. **Claude Code installation** - Latest CLI with OAuth authentication

## 🌐 Webmin Configuration

### Installation & Access
- **URL:** https://192.168.0.58:10000
- **Credentials:** milhy777 / admin123  
- **SSL:** Self-signed certificate (browser warning expected)
- **IP restrictions:** Only accessible from 192.168.0.58 (localhost)

### Current Theme Issue ⚠️
**CRITICAL PROBLEM:** After theme change in Webmin, most configuration options are missing:
- **Missing:** Terminal access module
- **Missing:** Many system administration options
- **Missing:** Advanced configuration menus
- **Previous version:** Had full terminal and comprehensive settings
- **Current state:** Severely limited functionality

### Webmin Modules Status
- **System:** ✅ Basic system info available
- **Hardware:** ✅ Disk usage, memory info
- **Networking:** ❌ Limited network configuration
- **Terminal:** ❌ **MISSING** (was available in previous version)
- **File Manager:** ❓ Status unknown
- **Package Management:** ❓ Status unknown
- **User Management:** ❓ Status unknown

### Potential Solutions Needed
1. **Theme rollback** to previous/default theme
2. **Module verification** - check if modules are disabled or missing
3. **Webmin reinstallation** with default configuration
4. **Alternative:** Use SSH terminal instead of Webmin terminal

## 🚨 Known Issues

1. **🔴 CRITICAL - Webmin theme issue** - Most settings and terminal missing after theme change
2. **Home Assistant** - Requires initial setup wizard
3. **AdGuard Home** - Needs initial configuration  
4. **Claude Code service** - Manual start required (OAuth dependency)

## 📝 Next Steps

1. Configure Home Assistant through web interface
2. Set up AdGuard Home filtering rules
3. Configure Portainer with additional container orchestration
4. Set up external backup destination (NAS/Cloud)
5. Implement monitoring and alerting system

---

**This summary was generated on:** July 5, 2025  
**System administrator:** Claude (AI Assistant)  
**Contact:** SSH to server and run `claude-code` for AI assistance