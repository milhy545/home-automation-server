#!/bin/bash

# Claude Code API Key Setup Helper

echo "Claude Code API Key Setup"
echo "=========================="
echo ""
echo "You need to configure your Anthropic API key to use Claude Code."
echo ""
echo "Option 1: Environment variable (recommended for server)"
echo "Add to /etc/environment:"
echo "ANTHROPIC_API_KEY=your_api_key_here"
echo ""
echo "Option 2: Interactive setup"
echo "Run: claude-code"
echo ""
echo "Current environment:"
if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "✓ ANTHROPIC_API_KEY is set"
else
    echo "✗ ANTHROPIC_API_KEY is not set"
fi
echo ""
echo "To set API key now:"
read -p "Enter your Anthropic API key (or press Enter to skip): " api_key
if [ -n "$api_key" ]; then
    echo "export ANTHROPIC_API_KEY=$api_key" >> /etc/environment
    export ANTHROPIC_API_KEY="$api_key"
    echo "✓ API key configured"
else
    echo "Skipped API key configuration"
fi
