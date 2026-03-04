#!/bin/bash
# HelioTheAnalyst Portfolio Monorepo - Run All Demos
# Runs all project demos in sequence (mock mode - no credentials needed)

set -e

PROJECTS_DIR="projects"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_header() {
    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}========================================${NC}"
}

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

run_demo() {
    local project="$1"
    local demo_script="$2"
    local proj_dir="$PROJECTS_DIR/$project"
    
    log_header "Running Demo: $project"
    
    if [ ! -d "$proj_dir" ]; then
        log_error "Project directory not found: $proj_dir"
        return 1
    fi
    
    if [ ! -f "$proj_dir/$demo_script" ]; then
        log_warn "Demo script not found: $proj_dir/$demo_script"
        return 0
    fi
    
    cd "$proj_dir"
    
    if [ ! -d ".venv" ]; then
        log_warn "Virtual environment not found for $project, skipping..."
        cd - > /dev/null
        return 0
    fi
    
    log_info "Running $demo_script..."
    if .venv/bin/python "$demo_script"; then
        log_success "Demo completed: $project"
    else
        log_error "Demo failed: $project"
    fi
    
    cd - > /dev/null
    echo ""
}

# Main execution
log_header "HelioTheAnalyst Portfolio - Running All Demos"
log_info "All demos run in MOCK mode (no real credentials needed)"
echo ""

# Track results
declare -a RESULTS
declare -a PROJECTS

# Shopify Integration
PROJECTS+=("shopify-integration-system")
if run_demo "shopify-integration-system" "scripts/run_demo.py"; then
    RESULTS+=("✓")
else
    RESULTS+=("✗")
fi

# HelioScraper
PROJECTS+=("helioscraper")
if run_demo "helioscraper" "scripts/run_demo.py"; then
    RESULTS+=("✓")
else
    RESULTS+=("✗")
fi

# Order Processing
PROJECTS+=("order-processing-automation")
if run_demo "order-processing-automation" "scripts/run_demo.py"; then
    RESULTS+=("✓")
else
    RESULTS+=("✗")
fi

# API Docs Testing
PROJECTS+=("api-docs-testing-framework")
if run_demo "api-docs-testing-framework" "scripts/run_demo.py"; then
    RESULTS+=("✓")
else
    RESULTS+=("✗")
fi

# Summary
echo ""
log_header "Demo Summary"

for i in "${!PROJECTS[@]}"; do
    if [ "${RESULTS[$i]}" = "✓" ]; then
        echo -e "  ${GREEN}✓${NC} ${PROJECTS[$i]}"
    else
        echo -e "  ${RED}✗${NC} ${PROJECTS[$i]}"
    fi
done

echo ""
log_info "Interactive demos (run separately):"
echo "  - make run-analytics    # Streamlit data analysis suite"
echo "  - make run-inventory    # Tkinter inventory GUI"
echo ""
log_success "All demos completed!"
