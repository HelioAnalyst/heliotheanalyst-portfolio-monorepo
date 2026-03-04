#!/bin/bash
# HelioTheAnalyst Portfolio Monorepo - Full CI Check
# Runs linting, type checking, and tests for all projects

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

check_project() {
    local project="$1"
    local proj_dir="$PROJECTS_DIR/$project"
    local venv_path="$proj_dir/.venv"
    
    log_header "Checking: $project"
    
    if [ ! -d "$proj_dir" ]; then
        log_error "Project directory not found: $proj_dir"
        return 1
    fi
    
    if [ ! -d "$venv_path" ]; then
        log_warn "Virtual environment not found for $project, skipping..."
        return 0
    fi
    
    cd "$proj_dir"
    
    # Ruff linting
    log_info "Running ruff linter..."
    if .venv/bin/ruff check src tests 2>/dev/null; then
        log_success "Linting passed"
        LINT_RESULT=0
    else
        log_warn "Linting found issues"
        LINT_RESULT=1
    fi
    
    # Ruff formatting check
    log_info "Checking formatting..."
    if .venv/bin/ruff format --check src tests 2>/dev/null; then
        log_success "Formatting OK"
        FORMAT_RESULT=0
    else
        log_warn "Formatting issues found"
        FORMAT_RESULT=1
    fi
    
    # MyPy type checking
    log_info "Running mypy..."
    if .venv/bin/mypy src 2>/dev/null | grep -q "Success"; then
        log_success "Type checking passed"
        TYPE_RESULT=0
    else
        log_warn "Type checking found issues"
        TYPE_RESULT=1
    fi
    
    # Pytest
    log_info "Running tests..."
    if .venv/bin/pytest tests/ -q --tb=line 2>/dev/null; then
        log_success "Tests passed"
        TEST_RESULT=0
    else
        log_warn "Some tests failed"
        TEST_RESULT=1
    fi
    
    cd - > /dev/null
    
    # Return combined result
    return $((LINT_RESULT + FORMAT_RESULT + TYPE_RESULT + TEST_RESULT))
}

# Main execution
log_header "HelioTheAnalyst Portfolio - Full CI Check"
echo ""

TOTAL_ISSUES=0

for project in "$PROJECTS_DIR"/*; do
    if [ -d "$project" ]; then
        proj_name=$(basename "$project")
        if ! check_project "$proj_name"; then
            ((TOTAL_ISSUES++)) || true
        fi
    fi
done

# Summary
echo ""
log_header "CI Check Summary"

if [ $TOTAL_ISSUES -eq 0 ]; then
    log_success "All checks passed!"
    exit 0
else
    log_warn "Found issues in $TOTAL_ISSUES project(s)"
    echo ""
    log_info "Run 'make format' to fix formatting issues"
    log_info "Run 'make lint' to see linting details"
    log_info "Run 'make test' to see test details"
    exit 1
fi
