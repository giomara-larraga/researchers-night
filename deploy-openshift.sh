#!/bin/bash

# OpenShift Deployment Script for Phone Selector App
# ==================================================

set -e

# Configuration
PROJECT_NAME="phone-selector"
APP_NAME="phone-selector"
GIT_REPO="https://github.com/giomara-larraga/researchers-night.git"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if oc CLI is installed
check_oc_cli() {
    if ! command -v oc &> /dev/null; then
        log_error "OpenShift CLI (oc) is not installed or not in PATH"
        log_info "Please install it from: https://docs.openshift.com/container-platform/latest/cli_reference/openshift_cli/getting-started-cli.html"
        exit 1
    fi
    log_success "OpenShift CLI found"
}

# Check if logged into OpenShift
check_login() {
    if ! oc whoami &> /dev/null; then
        log_error "Not logged into OpenShift cluster"
        log_info "Please run: oc login <your-cluster-url>"
        exit 1
    fi
    log_success "Logged into OpenShift as: $(oc whoami)"
}

# Create or switch to project
setup_project() {
    log_info "Setting up project: $PROJECT_NAME"
    
    if oc get project $PROJECT_NAME &> /dev/null; then
        log_info "Project $PROJECT_NAME already exists, switching to it"
        oc project $PROJECT_NAME
    else
        log_info "Creating new project: $PROJECT_NAME"
        oc new-project $PROJECT_NAME --display-name="Phone Selector App" --description="Multi-criteria phone selection application"
    fi
    
    log_success "Project $PROJECT_NAME is ready"
}

# Deploy using template
deploy_with_template() {
    log_info "Deploying application using template..."
    
    oc process -f openshift/template.yaml \
        -p APP_NAME=$APP_NAME \
        -p GIT_REPO=$GIT_REPO \
        -p MEMORY_LIMIT=512Mi \
        -p CPU_LIMIT=500m | oc apply -f -
    
    log_success "Application deployed using template"
}

# Deploy individual resources
deploy_resources() {
    log_info "Deploying individual OpenShift resources..."
    
    # Apply all YAML files in order
    local files=(
        "openshift/imagestream.yaml"
        "openshift/buildconfig.yaml"
        "openshift/configmap.yaml"
        "openshift/deployment.yaml"
        "openshift/service.yaml"
        "openshift/route.yaml"
    )
    
    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            log_info "Applying $file"
            oc apply -f "$file"
        else
            log_warning "File $file not found, skipping"
        fi
    done
    
    log_success "All resources deployed"
}

# Start build
start_build() {
    log_info "Starting build process..."
    
    if oc get bc phone-selector-build &> /dev/null; then
        oc start-build phone-selector-build --follow
    elif oc get bc $APP_NAME &> /dev/null; then
        oc start-build $APP_NAME --follow
    else
        log_warning "No build config found, build will be triggered automatically"
    fi
}

# Wait for deployment
wait_for_deployment() {
    log_info "Waiting for deployment to be ready..."
    
    # Wait for deployment to be available
    oc rollout status deployment/$APP_NAME --timeout=300s
    
    log_success "Deployment is ready"
}

# Get application URL
get_app_url() {
    log_info "Getting application URL..."
    
    local route_name
    if oc get route phone-selector-route &> /dev/null; then
        route_name="phone-selector-route"
    elif oc get route $APP_NAME &> /dev/null; then
        route_name=$APP_NAME
    else
        log_warning "No route found"
        return
    fi
    
    local url=$(oc get route $route_name -o jsonpath='{.spec.host}')
    if [ -n "$url" ]; then
        log_success "Application URL: https://$url"
        echo ""
        log_info "🌐 Your Phone Selector app is available at: https://$url"
    fi
}

# Show deployment status
show_status() {
    log_info "Deployment Status:"
    echo "=================="
    
    echo ""
    log_info "Pods:"
    oc get pods -l app=$APP_NAME
    
    echo ""
    log_info "Services:"
    oc get svc -l app=$APP_NAME
    
    echo ""
    log_info "Routes:"
    oc get routes -l app=$APP_NAME
    
    echo ""
    log_info "Builds:"
    oc get builds
}

# Show logs
show_logs() {
    log_info "Application logs:"
    local pod=$(oc get pods -l app=$APP_NAME -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    
    if [ -n "$pod" ]; then
        oc logs -f "$pod"
    else
        log_error "No running pods found"
    fi
}

# Clean up deployment
cleanup() {
    log_warning "Cleaning up deployment..."
    
    # Delete all resources with app label
    oc delete all -l app=$APP_NAME
    oc delete configmap -l app=$APP_NAME
    oc delete route -l app=$APP_NAME
    
    log_success "Cleanup completed"
}

# Main deployment function
deploy() {
    log_info "🚀 Starting OpenShift deployment for Phone Selector App"
    echo "========================================================"
    
    check_oc_cli
    check_login
    setup_project
    
    # Choose deployment method
    if [ -f "openshift/template.yaml" ]; then
        deploy_with_template
    else
        deploy_resources
    fi
    
    start_build
    wait_for_deployment
    get_app_url
    
    echo ""
    log_success "🎉 Deployment completed successfully!"
    echo ""
    show_status
}

# Parse command line arguments
case "${1:-deploy}" in
    "deploy")
        deploy
        ;;
    "status")
        check_oc_cli
        check_login
        show_status
        ;;
    "logs")
        check_oc_cli
        check_login
        show_logs
        ;;
    "url")
        check_oc_cli
        check_login
        get_app_url
        ;;
    "build")
        check_oc_cli
        check_login
        start_build
        ;;
    "clean")
        check_oc_cli
        check_login
        cleanup
        ;;
    "help"|"-h"|"--help")
        echo "OpenShift Deployment Script for Phone Selector App"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  deploy  - Deploy the application (default)"
        echo "  status  - Show deployment status"
        echo "  logs    - Show application logs"
        echo "  url     - Get application URL"
        echo "  build   - Start a new build"
        echo "  clean   - Clean up deployment"
        echo "  help    - Show this help message"
        ;;
    *)
        log_error "Unknown command: $1"
        log_info "Use '$0 help' for usage information"
        exit 1
        ;;
esac