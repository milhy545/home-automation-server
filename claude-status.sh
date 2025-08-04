#!/bin/bash

# Claude Code Status Checker

echo "=== Claude Code CLI Status ==="
echo "Date: $(date)"
echo ""

# Check if Claude Code is installed
if command -v claude-code &> /dev/null; then
    echo "✓ Claude Code CLI installed: $(claude-code --version)"
else
    echo "✗ Claude Code CLI not found"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    echo "✓ Node.js: $(node --version)"
else
    echo "✗ Node.js not found"
fi

# Check NPM
if command -v npm &> /dev/null; then
    echo "✓ NPM: $(npm --version)"
else
    echo "✗ NPM not found"
fi

echo ""

# Check service status
if rc-service claude-code status &> /dev/null; then
    echo "✓ Claude Code service is running"
else
    echo "✗ Claude Code service is not running"
fi

# Check port
if netstat -tlnp | grep :8080 &> /dev/null; then
    echo "✓ Claude Code listening on port 8080"
else
    echo "✗ Claude Code not listening on port 8080"
fi

echo ""

# Check API key
if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "✓ ANTHROPIC_API_KEY is configured"
else
    echo "✗ ANTHROPIC_API_KEY is not configured"
    echo "  Run: /root/setup-claude-api.sh"
fi

echo ""

# Check configuration
if [ -f "/root/.claude/settings.local.json" ]; then
    echo "✓ Claude configuration exists"
    echo "Configuration:"
    cat /root/.claude/settings.local.json | head -10
else
    echo "✗ Claude configuration not found"
fi

echo ""
echo "=== Access Information ==="
echo "URL: http://192.168.0.58:8080"
echo "Local: claude-code (command line)"
