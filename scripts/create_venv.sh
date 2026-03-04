#!/bin/bash
# HelioTheAnalyst Portfolio Monorepo - Virtual Environment Creator
# Usage: ./scripts/create_venv.sh [project-name]
#        ./scripts/create_venv.sh all

set -e

PROJECTS_DIR="projects"
PROJECT="${1:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

create_venv() {
    local proj_dir="$1"
    local proj_name=$(basename "$proj_dir")
    
    log_info "Setting up $proj_name..."
    
    cd "$proj_dir"
    
    # Remove existing venv if corrupted
    if [ -d ".venv" ]; then
        log_warn "Removing existing .venv in $proj_name"
        rm -rf .venv
    fi
    
    # Create virtual environment
    if command -v python3.11 &> /dev/null; then
        python3.11 -m venv .venv
    elif command -v python3 &> /dev/null; then
        python3 -m venv .venv
    else
        log_error "Python 3 not found!"
        exit 1
    fi
    
    # Activate and install
    source .venv/bin/activate
    pip install --upgrade pip setuptools wheel
    
    if [ -f "pyproject.toml" ]; then
        pip install -e ".[dev]"
    elif [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    elif [ -f "requirements-dev.txt" ]; then
        pip install -r requirements-dev.txt
    fi
    
    deactivate
    cd - > /dev/null
    
    log_success "Virtual environment created for $proj_name"
}

# Main execution
if [ -z "$PROJECT" ]; then
    echo "Usage: $0 [project-name|all]"
    echo ""
    echo "Available projects:"
    ls -1 "$PROJECTS_DIR"
    exit 1
fi

if [ "$PROJECT" = "all" ]; then
    log_info "Creating virtual environments for all projects..."
    for proj in "$PROJECTS_DIR"/*; do
        if [ -d "$proj" ]; then
            create_venv "$proj"
        fi
    done
    log_success "All virtual environments created!"
else
    proj_path="$PROJECTS_DIR/$PROJECT"
    if [ ! -d "$proj_path" ]; then
        log_error "Project '$PROJECT' not found!"
        exit 1
    fi
    create_venv "$proj_path"
fi

echo ""
log_success "Setup complete! Activate with: source projects/$PROJECT/.venv/bin/activate"
