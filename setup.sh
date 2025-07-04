#!/bin/bash

# Design Gallery Project Setup Script
# This script helps set up the Design Gallery project with Cloudflare services

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

prompt_user() {
    local prompt="$1"
    local default="$2"
    local var_name="$3"
    
    if [ -n "$default" ]; then
        read -p "$prompt [$default]: " input
        eval "$var_name=\"${input:-$default}\""
    else
        read -p "$prompt: " input
        eval "$var_name=\"$input\""
    fi
}

check_dependencies() {
    log_info "Checking dependencies..."
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js is not installed. Please install Node.js 18+ and try again."
        exit 1
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        log_error "npm is not installed. Please install npm and try again."
        exit 1
    fi
    
    # Check wrangler
    if ! command -v wrangler &> /dev/null; then
        log_warning "Wrangler CLI is not installed. Installing..."
        npm install -g wrangler
    fi
    
    log_success "All dependencies are available"
}

setup_backend() {
    log_info "Setting up backend..."
    
    cd backend
    
    # Install dependencies
    log_info "Installing backend dependencies..."
    npm install
    
    # Check if database exists
    log_info "Checking Cloudflare D1 database..."
    if ! wrangler d1 list | grep -q "design-gallery-db"; then
        log_info "Creating D1 database..."
        wrangler d1 create design-gallery-db
        log_warning "Please update the database_id in wrangler.toml with the ID shown above"
        read -p "Press Enter after updating wrangler.toml..."
    fi
    
    # Check if R2 bucket exists
    log_info "Checking Cloudflare R2 bucket..."
    if ! wrangler r2 bucket list | grep -q "design-gallery-images"; then
        log_info "Creating R2 bucket..."
        wrangler r2 bucket create design-gallery-images
    fi
    
    # Set up JWT secret
    log_info "Setting up JWT secret..."
    if ! wrangler secret list | grep -q "JWT_SECRET"; then
        log_info "JWT_SECRET not found. Please enter a strong secret (32+ characters):"
        wrangler secret put JWT_SECRET
    else
        log_success "JWT_SECRET already configured"
    fi
    
    # Run database schema
    log_info "Setting up database schema..."
    wrangler d1 execute design-gallery-db --file=schema.sql
    
    log_success "Backend setup completed!"
    cd ..
}

setup_frontend() {
    log_info "Setting up frontend..."
    
    cd AD-APP
    
    # Install dependencies
    log_info "Installing frontend dependencies..."
    npm install
    
    # Create environment configuration
    if [ ! -f ".env" ]; then
        log_info "Creating environment configuration..."
        prompt_user "Enter your Worker URL" "https://design-gallery-worker.your-subdomain.workers.dev" WORKER_URL
        
        cat > .env << EOF
# API Configuration
API_BASE_URL=$WORKER_URL

# App Configuration
APP_NAME=Design Gallery
APP_VERSION=1.0.0
EOF
        log_success "Environment configuration created"
    else
        log_success "Environment configuration already exists"
    fi
    
    log_success "Frontend setup completed!"
    cd ..
}

deploy_backend() {
    log_info "Deploying backend to Cloudflare..."
    
    cd backend
    
    # Test locally first
    log_info "Running local tests..."
    if npm test; then
        log_success "Local tests passed"
    else
        log_warning "Some tests failed, but continuing with deployment"
    fi
    
    # Deploy to Cloudflare
    log_info "Deploying to Cloudflare Workers..."
    npm run deploy
    
    # Test production deployment
    prompt_user "Enter your production Worker URL for testing" "https://design-gallery-worker.your-subdomain.workers.dev" PROD_URL
    
    log_info "Testing production deployment..."
    if node test-api.js --url "$PROD_URL" --auth; then
        log_success "Production deployment tests passed"
    else
        log_warning "Some production tests failed"
    fi
    
    cd ..
}

cleanup_docs() {
    log_info "Cleaning up old documentation files..."
    
    # List of old documentation files to remove
    OLD_DOCS=(
        "MISSING_REQUIREMENTS.md"
        "teschincal_specification_doc.md"
        "FILTERING_FUNCTIONALITY_REPORT.md"
        "START_HERE.md"
        "IMPLEMENTATION_STEPS.md"
        "QUICK_FIX_GUIDE.md"
        "CRITICAL_FIXES.md"
        "CLOUDFLARE_IMPLEMENTATION_GUIDE.md"
        "GALLERY_IMPLEMENTATION_STEPS.md"
        "fucntional_requirements.md"
    )
    
    for doc in "${OLD_DOCS[@]}"; do
        if [ -f "$doc" ]; then
            log_info "Removing $doc..."
            rm "$doc"
        fi
    done
    
    log_success "Documentation cleanup completed"
    log_info "All documentation is now consolidated in COMPREHENSIVE_PROJECT_GUIDE.md"
}

show_next_steps() {
    log_info "Setup completed! Here are the next steps:"
    echo ""
    echo "1. Frontend Development:"
    echo "   cd AD-APP && npm start"
    echo ""
    echo "2. Backend Development:"
    echo "   cd backend && npm run dev"
    echo ""
    echo "3. Testing:"
    echo "   cd backend && npm test"
    echo ""
    echo "4. Production Deployment:"
    echo "   cd backend && npm run deploy"
    echo ""
    echo "5. Documentation:"
    echo "   Read COMPREHENSIVE_PROJECT_GUIDE.md for detailed information"
    echo ""
    log_success "Happy coding! 🚀"
}

main() {
    echo "=================================================="
    echo "🎨 Design Gallery Project Setup"
    echo "=================================================="
    echo ""
    
    # Parse command line arguments
    SKIP_DEPS=false
    BACKEND_ONLY=false
    FRONTEND_ONLY=false
    DEPLOY=false
    CLEANUP=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-deps)
                SKIP_DEPS=true
                shift
                ;;
            --backend-only)
                BACKEND_ONLY=true
                shift
                ;;
            --frontend-only)
                FRONTEND_ONLY=true
                shift
                ;;
            --deploy)
                DEPLOY=true
                shift
                ;;
            --cleanup)
                CLEANUP=true
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [options]"
                echo ""
                echo "Options:"
                echo "  --skip-deps      Skip dependency checking"
                echo "  --backend-only   Setup backend only"
                echo "  --frontend-only  Setup frontend only"
                echo "  --deploy         Deploy backend after setup"
                echo "  --cleanup        Clean up old documentation files"
                echo "  --help, -h       Show this help message"
                echo ""
                echo "Examples:"
                echo "  $0                     # Full setup"
                echo "  $0 --backend-only      # Backend setup only"
                echo "  $0 --deploy            # Setup and deploy"
                echo "  $0 --cleanup           # Clean up documentation"
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Check dependencies
    if [ "$SKIP_DEPS" = false ]; then
        check_dependencies
    fi
    
    # Setup based on options
    if [ "$FRONTEND_ONLY" = true ]; then
        setup_frontend
    elif [ "$BACKEND_ONLY" = true ]; then
        setup_backend
    else
        setup_backend
        setup_frontend
    fi
    
    # Deploy if requested
    if [ "$DEPLOY" = true ]; then
        deploy_backend
    fi
    
    # Cleanup if requested
    if [ "$CLEANUP" = true ]; then
        cleanup_docs
    fi
    
    # Show next steps
    show_next_steps
}

# Run main function with all arguments
main "$@" 