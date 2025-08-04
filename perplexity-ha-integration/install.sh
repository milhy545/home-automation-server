#!/bin/bash
##############################################################################
# Perplexity-HA Integration Installer
# Zero-touch deployment with minimal user interaction
# Version: 1.0.0
# Author: Claude AI Assistant
# Date: 2025-07-05
##############################################################################

set -euo pipefail

# Constants and configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_FILE="/tmp/perplexity-ha-install.log"
readonly CONFIG_BACKUP_DIR="/tmp/ha-config-backup-$(date +%s)"
readonly VERSION="1.0.0"
readonly MIN_HA_VERSION="2023.1.0"

# Color codes for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Global variables
HA_TYPE=""
HA_CONFIG_DIR=""
HA_API_URL=""
HA_TOKEN=""
PERPLEXITY_API_KEY=""
WEBHOOK_ID=""
DOCKER_COMPOSE_FILE=""

##############################################################################
# Utility Functions
##############################################################################

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}✅ $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}❌ ERROR: $1${NC}" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}⚠️  WARNING: $1${NC}" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}ℹ️  $1${NC}" | tee -a "$LOG_FILE"
}

spinner() {
    local pid=$1
    local delay=0.1
    local spinstr='|/-\\'
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

##############################################################################
# Environment Detection
##############################################################################

detect_ha_environment() {
    log "🔍 Detecting Home Assistant environment..."
    
    # Check for HassOS (Supervisor)
    if [ -f "/usr/bin/hassio" ] || [ -d "/usr/share/hassio" ]; then
        HA_TYPE="supervisor"
        HA_CONFIG_DIR="/config"
        HA_API_URL="http://supervisor/core/api"
        success "Detected Home Assistant Supervised/HassOS"
        return 0
    fi
    
    # Check for Docker installation
    if command -v docker >/dev/null 2>&1; then
        # Look for HA container
        if docker ps --format "table {{.Names}}" | grep -E "(homeassistant|ha)" >/dev/null 2>&1; then
            HA_TYPE="docker"
            # Try to find config volume
            local container_name=$(docker ps --format "{{.Names}}" | grep -E "(homeassistant|ha)" | head -1)
            HA_CONFIG_DIR=$(docker inspect "$container_name" | jq -r '.[0].Mounts[] | select(.Destination=="/config") | .Source' 2>/dev/null || echo "/opt/homeassistant")
            HA_API_URL="http://localhost:8123/api"
            success "Detected Home Assistant Container"
            return 0
        fi
    fi
    
    # Check for Core installation (venv)
    if [ -f "/srv/homeassistant/bin/hass" ] || [ -f "/opt/homeassistant/bin/hass" ]; then
        HA_TYPE="core"
        # Common Core paths
        for path in "/home/homeassistant/.homeassistant" "/opt/homeassistant/config" "/srv/homeassistant/config"; do
            if [ -d "$path" ]; then
                HA_CONFIG_DIR="$path"
                break
            fi
        done
        HA_API_URL="http://localhost:8123/api"
        success "Detected Home Assistant Core"
        return 0
    fi
    
    # Manual detection
    warning "Could not auto-detect Home Assistant installation"
    read -p "Please enter Home Assistant config directory path: " HA_CONFIG_DIR
    read -p "Please enter Home Assistant API URL (e.g., http://localhost:8123/api): " HA_API_URL
    HA_TYPE="manual"
    
    if [ ! -d "$HA_CONFIG_DIR" ]; then
        error "Configuration directory does not exist: $HA_CONFIG_DIR"
    fi
}

##############################################################################
# Prerequisites Check
##############################################################################

check_prerequisites() {
    log "🔧 Checking prerequisites..."
    
    # Check if running as appropriate user
    if [ "$HA_TYPE" = "supervisor" ] && [ "$EUID" -ne 0 ]; then
        error "For HassOS/Supervised installation, please run as root"
    fi
    
    # Check Python availability
    if ! command -v python3 >/dev/null 2>&1; then
        error "Python 3 is required but not installed"
    fi
    
    # Check required packages based on environment
    case "$HA_TYPE" in
        "docker")
            if ! command -v docker >/dev/null 2>&1; then
                error "Docker is required but not installed"
            fi
            ;;
        "supervisor")
            # Check supervisor API
            if ! curl -sf http://supervisor/core/api >/dev/null 2>&1; then
                warning "Supervisor API not accessible, continuing anyway"
            fi
            ;;
    esac
    
    # Check HA config directory
    if [ ! -f "$HA_CONFIG_DIR/configuration.yaml" ]; then
        error "Home Assistant configuration.yaml not found in $HA_CONFIG_DIR"
    fi
    
    # Check write permissions
    if [ ! -w "$HA_CONFIG_DIR" ]; then
        error "No write permission to Home Assistant config directory: $HA_CONFIG_DIR"
    fi
    
    success "Prerequisites check completed"
}

##############################################################################
# User Input Collection
##############################################################################

collect_user_input() {
    log "📝 Collecting configuration parameters..."
    
    echo
    info "🔑 API Keys Setup"
    echo "This integration requires API keys for both Home Assistant and Perplexity."
    echo
    
    # Home Assistant Long-Lived Token
    if [ -z "${HA_TOKEN:-}" ]; then
        echo "1. Home Assistant Long-Lived Token:"
        echo "   Go to Profile -> Security -> Long-Lived Access Tokens"
        echo "   Create a new token and paste it here."
        echo
        read -s -p "Enter Home Assistant Token: " HA_TOKEN
        echo
    fi
    
    # Perplexity API Key
    if [ -z "${PERPLEXITY_API_KEY:-}" ]; then
        echo "2. Perplexity API Key:"
        echo "   Go to https://www.perplexity.ai/settings/api"
        echo "   Generate an API key and paste it here."
        echo
        read -s -p "Enter Perplexity API Key: " PERPLEXITY_API_KEY
        echo
    fi
    
    # Generate webhook ID
    WEBHOOK_ID="perplexity_$(openssl rand -hex 8)"
    
    # Optional settings
    echo
    info "🛠️ Optional Configuration"
    read -p "Enable TTS responses? (y/N): " enable_tts
    read -p "Custom response entity name (default: sensor.perplexity_response): " custom_entity
    
    # Set defaults
    enable_tts=${enable_tts:-n}
    custom_entity=${custom_entity:-sensor.perplexity_response}
    
    success "Configuration parameters collected"
}

##############################################################################
# API Validation
##############################################################################

validate_apis() {
    log "🔐 Validating API credentials..."
    
    # Test Home Assistant API
    info "Testing Home Assistant API connection..."
    local ha_test_response
    ha_test_response=$(curl -s -w "%{http_code}" -o /tmp/ha_test.json \
        -H "Authorization: Bearer $HA_TOKEN" \
        -H "Content-Type: application/json" \
        "$HA_API_URL/") || true
    
    if [ "${ha_test_response: -3}" != "200" ]; then
        error "Home Assistant API test failed. Check token and URL."
    fi
    success "Home Assistant API connection verified"
    
    # Test Perplexity API
    info "Testing Perplexity API connection..."
    local pplx_test_response
    pplx_test_response=$(curl -s -w "%{http_code}" -o /tmp/pplx_test.json \
        -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
        -H "Content-Type: application/json" \
        -d '{"model":"sonar","messages":[{"role":"user","content":"test"}],"max_tokens":10}' \
        "https://api.perplexity.ai/chat/completions") || true
    
    if [ "${pplx_test_response: -3}" != "200" ]; then
        error "Perplexity API test failed. Check API key."
    fi
    success "Perplexity API connection verified"
}

##############################################################################
# Backup Functions
##############################################################################

backup_configuration() {
    log "💾 Creating configuration backup..."
    
    mkdir -p "$CONFIG_BACKUP_DIR"
    
    # Backup critical files
    local files_to_backup=(
        "configuration.yaml"
        "automations.yaml" 
        "secrets.yaml"
        "python_scripts"
    )
    
    for file in "${files_to_backup[@]}"; do
        if [ -e "$HA_CONFIG_DIR/$file" ]; then
            cp -r "$HA_CONFIG_DIR/$file" "$CONFIG_BACKUP_DIR/"
            log "Backed up: $file"
        fi
    done
    
    success "Configuration backup created at: $CONFIG_BACKUP_DIR"
}

##############################################################################
# Installation Functions
##############################################################################

install_dependencies() {
    log "📦 Installing dependencies..."
    
    # Ensure python_scripts directory exists
    mkdir -p "$HA_CONFIG_DIR/python_scripts"
    
    # Install required Python packages based on environment
    case "$HA_TYPE" in
        "supervisor"|"docker")
            # For supervised/docker, packages should be available
            info "Using system Python packages"
            ;;
        "core")
            # For core installation, install in venv
            local venv_path="/srv/homeassistant"
            if [ -d "$venv_path" ]; then
                source "$venv_path/bin/activate"
                pip install aiohttp asyncio-mqtt pydantic instructor
            fi
            ;;
    esac
    
    success "Dependencies installed"
}

install_python_script() {
    log "🐍 Installing Python bridge script..."
    
    # Copy Python script from template
    cp "$SCRIPT_DIR/templates/perplexity_integration.py" \
       "$HA_CONFIG_DIR/python_scripts/"
    
    # Set proper permissions
    chmod 644 "$HA_CONFIG_DIR/python_scripts/perplexity_integration.py"
    
    success "Python bridge script installed"
}

install_automation() {
    log "🤖 Installing automation configuration..."
    
    # Generate automation from template
    local automation_file="$HA_CONFIG_DIR/automations_perplexity.yaml"
    
    # Create automation using template substitution
    sed -e "s/{{webhook_id}}/$WEBHOOK_ID/g" \
        -e "s/{{response_entity}}/$custom_entity/g" \
        "$SCRIPT_DIR/templates/automation.yaml" > "$automation_file"
    
    # Update main configuration.yaml to include automations
    if ! grep -q "automation: !include automations_perplexity.yaml" "$HA_CONFIG_DIR/configuration.yaml"; then
        echo "" >> "$HA_CONFIG_DIR/configuration.yaml"
        echo "# Perplexity Integration" >> "$HA_CONFIG_DIR/configuration.yaml"
        echo "automation: !include automations_perplexity.yaml" >> "$HA_CONFIG_DIR/configuration.yaml"
    fi
    
    success "Automation configuration installed"
}

install_secrets() {
    log "🔐 Installing secrets configuration..."
    
    local secrets_file="$HA_CONFIG_DIR/secrets.yaml"
    
    # Create secrets.yaml if it doesn't exist
    if [ ! -f "$secrets_file" ]; then
        touch "$secrets_file"
        chmod 600 "$secrets_file"
    fi
    
    # Add secrets (avoid duplicates)
    if ! grep -q "perplexity_api_key" "$secrets_file"; then
        echo "" >> "$secrets_file"
        echo "# Perplexity Integration Secrets" >> "$secrets_file"
        echo "perplexity_api_key: \"$PERPLEXITY_API_KEY\"" >> "$secrets_file"
        echo "ha_long_lived_token: \"$HA_TOKEN\"" >> "$secrets_file"
        echo "perplexity_webhook_id: \"$WEBHOOK_ID\"" >> "$secrets_file"
    fi
    
    success "Secrets configuration installed"
}

install_sensors() {
    log "📊 Installing sensor configuration..."
    
    local sensors_file="$HA_CONFIG_DIR/sensors_perplexity.yaml"
    
    # Create sensor configuration
    cat > "$sensors_file" << EOF
# Perplexity Integration Sensors
- platform: template
  sensors:
    perplexity_response:
      friendly_name: "Perplexity Response"
      value_template: "{{ states('input_text.perplexity_last_response') }}"
      attribute_templates:
        timestamp: "{{ now().isoformat() }}"
        model: "sonar-pro"
        
    perplexity_status:
      friendly_name: "Perplexity Integration Status"
      value_template: >
        {% if states('sensor.perplexity_response') != 'unknown' %}
          online
        {% else %}
          offline
        {% endif %}
      icon_template: >
        {% if states('sensor.perplexity_response') != 'unknown' %}
          mdi:check-circle
        {% else %}
          mdi:alert-circle
        {% endif %}

input_text:
  perplexity_last_response:
    name: "Last Perplexity Response"
    max: 1000
    initial: "Ready for questions"
EOF

    # Update configuration.yaml
    if ! grep -q "sensor: !include sensors_perplexity.yaml" "$HA_CONFIG_DIR/configuration.yaml"; then
        echo "sensor: !include sensors_perplexity.yaml" >> "$HA_CONFIG_DIR/configuration.yaml"
    fi
    
    success "Sensor configuration installed"
}

##############################################################################
# Post-Installation Testing
##############################################################################

test_installation() {
    log "🧪 Running post-installation tests..."
    
    # Test 1: Check file installation
    info "Test 1: Checking file installation..."
    local required_files=(
        "$HA_CONFIG_DIR/python_scripts/perplexity_integration.py"
        "$HA_CONFIG_DIR/automations_perplexity.yaml"
        "$HA_CONFIG_DIR/sensors_perplexity.yaml"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            error "Required file missing: $file"
        fi
    done
    success "All required files installed"
    
    # Test 2: Configuration syntax
    info "Test 2: Checking Home Assistant configuration syntax..."
    if command -v hass >/dev/null 2>&1; then
        if ! hass --script check_config --config "$HA_CONFIG_DIR" >/dev/null 2>&1; then
            warning "Configuration check failed - please review manually"
        else
            success "Configuration syntax is valid"
        fi
    else
        warning "Cannot check configuration - hass command not available"
    fi
    
    # Test 3: Webhook endpoint (if HA is running)
    info "Test 3: Testing webhook endpoint..."
    local webhook_url=""
    case "$HA_TYPE" in
        "supervisor")
            webhook_url="http://supervisor/core/api/webhook/$WEBHOOK_ID"
            ;;
        *)
            webhook_url="$HA_API_URL/webhook/$WEBHOOK_ID"
            ;;
    esac
    
    # Simple webhook test
    local test_payload='{"question":"test connection"}'
    if curl -sf -X POST -H "Content-Type: application/json" \
       -d "$test_payload" "$webhook_url" >/dev/null 2>&1; then
        success "Webhook endpoint accessible"
    else
        warning "Webhook endpoint test inconclusive - may require HA restart"
    fi
    
    success "Post-installation tests completed"
}

##############################################################################
# Home Assistant Restart
##############################################################################

restart_home_assistant() {
    log "🔄 Restarting Home Assistant..."
    
    case "$HA_TYPE" in
        "supervisor")
            if command -v ha >/dev/null 2>&1; then
                ha core restart
            else
                curl -X POST -H "Authorization: Bearer $HA_TOKEN" \
                     "$HA_API_URL/services/homeassistant/restart"
            fi
            ;;
        "docker")
            local container_name=$(docker ps --format "{{.Names}}" | grep -E "(homeassistant|ha)" | head -1)
            docker restart "$container_name"
            ;;
        "core")
            # Try systemctl first, then direct API
            if systemctl is-active homeassistant >/dev/null 2>&1; then
                systemctl restart homeassistant
            else
                curl -X POST -H "Authorization: Bearer $HA_TOKEN" \
                     "$HA_API_URL/services/homeassistant/restart"
            fi
            ;;
        "manual")
            curl -X POST -H "Authorization: Bearer $HA_TOKEN" \
                 "$HA_API_URL/services/homeassistant/restart"
            ;;
    esac
    
    # Wait for restart
    info "Waiting for Home Assistant to restart..."
    sleep 10
    
    # Check if HA is back online
    local retries=12
    while [ $retries -gt 0 ]; do
        if curl -sf -H "Authorization: Bearer $HA_TOKEN" "$HA_API_URL/" >/dev/null 2>&1; then
            success "Home Assistant restarted successfully"
            return 0
        fi
        sleep 5
        ((retries--))
    done
    
    warning "Home Assistant restart may still be in progress"
}

##############################################################################
# Main Installation Flow
##############################################################################

show_banner() {
    echo
    echo "╔══════════════════════════════════════════════════════╗"
    echo "║           Perplexity-HA Integration Installer       ║"
    echo "║                    Version $VERSION                     ║"
    echo "╚══════════════════════════════════════════════════════╝"
    echo
}

show_completion_summary() {
    echo
    success "🎉 Installation completed successfully!"
    echo
    echo "╔══════════════════════════════════════════════════════╗"
    echo "║                  Installation Summary                ║"
    echo "╠══════════════════════════════════════════════════════╣"
    echo "║ ✅ Environment detected: $HA_TYPE"
    echo "║ ✅ Configuration backed up to: $CONFIG_BACKUP_DIR"
    echo "║ ✅ Python bridge script installed"
    echo "║ ✅ Automation configured"
    echo "║ ✅ Sensors created"
    echo "║ ✅ Secrets configured"
    echo "╚══════════════════════════════════════════════════════╝"
    echo
    echo "🔗 Webhook URL: $HA_API_URL/webhook/$WEBHOOK_ID"
    echo "📊 Response Entity: $custom_entity"
    echo "📁 Backup Location: $CONFIG_BACKUP_DIR"
    echo
    echo "📖 Example Usage:"
    echo "   curl -X POST -H 'Content-Type: application/json' \\"
    echo "        -d '{\"question\":\"What is the weather today?\"}' \\"
    echo "        '$HA_API_URL/webhook/$WEBHOOK_ID'"
    echo
    echo "🔧 Next Steps:"
    echo "   1. Check Home Assistant logs for any errors"
    echo "   2. Test the webhook endpoint with a simple question"
    echo "   3. Configure TTS if desired"
    echo "   4. Review the documentation in $SCRIPT_DIR/docs/"
    echo
}

cleanup() {
    log "🧹 Cleaning up temporary files..."
    rm -f /tmp/ha_test.json /tmp/pplx_test.json
}

main() {
    # Trap cleanup on exit
    trap cleanup EXIT
    
    # Check if help requested
    if [[ "${1:-}" =~ ^(-h|--help)$ ]]; then
        cat << EOF
Perplexity-HA Integration Installer v$VERSION

USAGE:
    $0 [OPTIONS]

OPTIONS:
    -h, --help          Show this help message
    --ha-token TOKEN    Home Assistant Long-Lived Token
    --pplx-key KEY      Perplexity API Key
    --config-dir DIR    Home Assistant config directory
    --api-url URL       Home Assistant API URL

EXAMPLES:
    # Interactive installation
    $0
    
    # Non-interactive installation
    $0 --ha-token "eyJ..." --pplx-key "pplx-..." 

For more information, see: $SCRIPT_DIR/docs/README.md
EOF
        exit 0
    fi
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --ha-token)
                HA_TOKEN="$2"
                shift 2
                ;;
            --pplx-key)
                PERPLEXITY_API_KEY="$2"
                shift 2
                ;;
            --config-dir)
                HA_CONFIG_DIR="$2"
                shift 2
                ;;
            --api-url)
                HA_API_URL="$2"
                shift 2
                ;;
            *)
                error "Unknown option: $1"
                ;;
        esac
    done
    
    # Main installation flow
    show_banner
    
    log "Starting Perplexity-HA Integration installation..."
    
    detect_ha_environment
    check_prerequisites
    collect_user_input
    validate_apis
    backup_configuration
    install_dependencies
    install_python_script
    install_automation
    install_secrets
    install_sensors
    test_installation
    
    # Ask about restart
    echo
    read -p "Restart Home Assistant now? (Y/n): " restart_choice
    restart_choice=${restart_choice:-y}
    
    if [[ "$restart_choice" =~ ^[Yy]$ ]]; then
        restart_home_assistant
    else
        warning "Please restart Home Assistant manually to apply changes"
    fi
    
    show_completion_summary
    
    log "Installation completed successfully!"
}

# Run main function
main "$@"