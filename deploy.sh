#!/bin/bash

# Phone Selector App Deployment Script

echo "🚀 Phone Selector App Deployment"
echo "================================"

# Function to build the Docker image
build_image() {
    echo "📦 Building Docker image..."
    docker build -t phone-selector-app .
    if [ $? -eq 0 ]; then
        echo "✅ Docker image built successfully!"
    else
        echo "❌ Failed to build Docker image"
        exit 1
    fi
}

# Function to run the container
run_container() {
    echo "🏃 Running container..."
    docker run -d \
        --name phone-selector \
        -p 8050:8050 \
        --env DEBUG=false \
        --restart unless-stopped \
        phone-selector-app
    
    if [ $? -eq 0 ]; then
        echo "✅ Container started successfully!"
        echo "🌐 App available at: http://localhost:8050"
    else
        echo "❌ Failed to start container"
        exit 1
    fi
}

# Function to stop and remove existing container
cleanup() {
    echo "🧹 Cleaning up existing container..."
    docker stop phone-selector 2>/dev/null || true
    docker rm phone-selector 2>/dev/null || true
}

# Function to show logs
show_logs() {
    echo "📋 Container logs:"
    docker logs -f phone-selector
}

# Function to show container status
show_status() {
    echo "📊 Container status:"
    docker ps -f name=phone-selector
}

# Parse command line arguments
case "$1" in
    "build")
        build_image
        ;;
    "run")
        cleanup
        run_container
        ;;
    "deploy")
        cleanup
        build_image
        run_container
        ;;
    "logs")
        show_logs
        ;;
    "status")
        show_status
        ;;
    "stop")
        echo "🛑 Stopping container..."
        docker stop phone-selector
        ;;
    "restart")
        echo "🔄 Restarting container..."
        docker restart phone-selector
        ;;
    "clean")
        cleanup
        echo "✅ Cleanup completed"
        ;;
    *)
        echo "Usage: $0 {build|run|deploy|logs|status|stop|restart|clean}"
        echo ""
        echo "Commands:"
        echo "  build   - Build Docker image"
        echo "  run     - Run container (stops existing first)"
        echo "  deploy  - Build image and run container"
        echo "  logs    - Show container logs"
        echo "  status  - Show container status"
        echo "  stop    - Stop container"
        echo "  restart - Restart container"
        echo "  clean   - Remove container"
        exit 1
        ;;
esac