# 🐚 Oh My Zsh Configuration - Optimized for Servers
# Path to your oh-my-zsh installation
export ZSH="$HOME/.oh-my-zsh"

# Theme - lightweight and informative
ZSH_THEME="robbyrussell"

# Plugins - essential for development and server management
plugins=(
    git
    docker
    docker-compose
    python
    pip
    systemd
    sudo
    history
    colored-man-pages
    command-not-found
    zsh-autosuggestions
    zsh-syntax-highlighting
)

# Oh My Zsh settings
DISABLE_AUTO_UPDATE="true"  # Prevent automatic updates
DISABLE_UPDATE_PROMPT="true"
COMPLETION_WAITING_DOTS="true"
HIST_STAMPS="yyyy-mm-dd"

# History settings
HISTSIZE=10000
SAVEHIST=10000
setopt HIST_VERIFY
setopt SHARE_HISTORY
setopt APPEND_HISTORY
setopt INC_APPEND_HISTORY
setopt HIST_IGNORE_DUPS
setopt HIST_IGNORE_ALL_DUPS
setopt HIST_REDUCE_BLANKS

# Load Oh My Zsh
source $ZSH/oh-my-zsh.sh

# Custom aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
alias ..='cd ..'
alias ...='cd ../..'
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'

# Docker aliases
alias dps='docker ps'
alias dpa='docker ps -a'
alias di='docker images'
alias dex='docker exec -it'
alias dlogs='docker logs -f'
alias dstop='docker stop $(docker ps -q)'
alias drm='docker rm $(docker ps -aq)'
alias drmi='docker rmi $(docker images -q)'

# Git aliases
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gl='git pull'
alias gd='git diff'
alias gb='git branch'
alias gco='git checkout'

# System aliases
alias h='history'
alias j='jobs -l'
alias path='echo -e ${PATH//:/\\n}'
alias now='date +"%T"'
alias nowtime=now
alias nowdate='date +"%d-%m-%Y"'

# Network aliases
alias ports='netstat -tulanp'
alias listening='netstat -tlnp'
alias connections='netstat -an'

# Process aliases
alias psg='ps aux | grep -v grep | grep -i -e VSZ -e'
alias myps='ps -f -u $USER'

# MCP Server aliases (for our project)
alias mcp-status='docker ps | grep mcp'
alias mcp-logs='docker logs -f'
alias mcp-restart='cd /opt/mcp-servers && docker-compose restart'
alias mcp-stop='cd /opt/mcp-servers && docker-compose stop'
alias mcp-start='cd /opt/mcp-servers && docker-compose up -d'

# Custom functions
# Extract various archive formats
extract() {
    if [ -f $1 ] ; then
        case $1 in
            *.tar.bz2)   tar xjf $1     ;;
            *.tar.gz)    tar xzf $1     ;;
            *.bz2)       bunzip2 $1     ;;
            *.rar)       unrar e $1     ;;
            *.gz)        gunzip $1      ;;
            *.tar)       tar xf $1      ;;
            *.tbz2)      tar xjf $1     ;;
            *.tgz)       tar xzf $1     ;;
            *.zip)       unzip $1       ;;
            *.Z)         uncompress $1  ;;
            *.7z)        7z x $1        ;;
            *)     echo "'$1' cannot be extracted via extract()" ;;
        esac
    else
        echo "'$1' is not a valid file"
    fi
}

# Create directory and cd into it
mkcd() {
    mkdir -p "$1" && cd "$1"
}

# Find process by name
psgrep() {
    ps aux | grep -v grep | grep "$@" -i --color=auto
}

# Kill process by name
killps() {
    local pid pname sig="-TERM"
    if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
        echo "Usage: killps [-SIGNAL] pattern"
        return;
    fi
    if [ $# = 2 ]; then sig=$1 ; shift ; fi
    for pid in $(ps -eo pid,comm | grep "$1" | awk '{print $1}') ; do
        pname=$(ps -p $pid -o comm --no-headers)
        if ask "Kill process $pid <$pname> with signal $sig?"
            then kill $sig $pid
        fi
    done
}

# Ask for confirmation
ask() {
    echo -n "$@" '[y/n] ' ; read ans
    case "$ans" in
        y*|Y*) return 0 ;;
        *) return 1 ;;
    esac
}

# System information
sysinfo() {
    echo "=== System Information ==="
    echo "Hostname: $(hostname)"
    echo "Uptime: $(uptime)"
    echo "Load: $(cat /proc/loadavg)"
    echo "Memory: $(free -h | grep Mem)"
    echo "Disk: $(df -h / | tail -1)"
    echo "=========================="
}

# Export environment variables
export EDITOR=nano
export PAGER=less
export BROWSER=firefox

# Add local bin to PATH if it exists
if [ -d "$HOME/.local/bin" ]; then
    export PATH="$HOME/.local/bin:$PATH"
fi

# Add custom scripts to PATH
if [ -d "$HOME/bin" ]; then
    export PATH="$HOME/bin:$PATH"
fi

# Welcome message
echo "🐚 Oh My Zsh loaded successfully!"
echo "💡 Type 'sysinfo' for system information"
echo "🔧 Type 'mcp-status' to check MCP servers"
export GEMINI_API_KEY="TVUJ_API_KLIC"
export GEMINI_API_KEY=AIzaSyDkp4jsiG0FEyvyzy2XhBW5yAg7LBqvcYE
