#!/bin/bash

# XOFlowers AI Agent Deployment Script
# This script helps deploy the application in different environments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT="production"
COMPOSE_FILE="docker-compose.yml"
OVERRIDE_FILE=""
BUILD_IMAGES=false
PULL_IMAGES=true
BACKUP_DATA=false

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -e, --environment ENV    Set environment (development|staging|production) [default: production]"
    echo "  -b, --build             Build images locally instead of pulling"
    echo "  -n, --no-pull           Don't pull images before starting"
    echo "  --backup                Create backup before deployment"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                      Deploy production environment"
    echo "  $0 -e development       Deploy development environment"
    echo "  $0 -b --backup          Build images and create backup"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -b|--build)
            BUILD_IMAGES=true
            PULL_IMAGES=false
            shift
            ;;
        -n|--no-pull)
            PULL_IMAGES=false
            shift
            ;;
        --backup)
            BACKUP_DATA=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate environment
case $ENVIRONMENT in
    development|staging|production)
        ;;
    *)
        print_error "Invalid environment: $ENVIRONMENT"
        print_error "Valid environments: development, staging, production"
        exit 1
        ;;
esac

# Set compose files based on environment
if [[ "$ENVIRONMENT" == "production" ]]; then
    OVERRIDE_FILE="docker-compose.prod.yml"
elif [[ "$ENVIRONMENT" == "staging" ]]; then
    OVERRIDE_FILE="docker-compose.staging.yml"
fi

print_status "Starting deployment for environment: $ENVIRONMENT"

# Check if required files exist
if [[ ! -f "$COMPOSE_FILE" ]]; then
    print_error "Docker compose file not found: $COMPOSE_FILE"
    exit 1
fi

if [[ -n "$OVERRIDE_FILE" && ! -f "$OVERRIDE_FILE" ]]; then
    print_error "Override compose file not found: $OVERRIDE_FILE"
    exit 1
fi

# Check if environment file exists
ENV_FILE=".env"
if [[ "$ENVIRONMENT" == "production" ]]; then
    ENV_FILE=".env.production"
elif [[ "$ENVIRONMENT" == "staging" ]]; then
    ENV_FILE=".env.staging"
fi

if [[ ! -f "$ENV_FILE" ]]; then
    print_warning "Environment file not found: $ENV_FILE"
    print_warning "Using default environment variables"
fi

# Create backup if requested
if [[ "$BACKUP_DATA" == true ]]; then
    print_status "Creating backup..."
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup Redis data
    if docker volume ls | grep -q "xoflowers_redis_data"; then
        print_status "Backing up Redis data..."
        docker run --rm -v xoflowers_redis_data:/data -v "$(pwd)/$BACKUP_DIR":/backup alpine tar czf /backup/redis_data.tar.gz -C /data .
    fi
    
    # Backup ChromaDB data
    if [[ -d "chroma_db_flowers" ]]; then
        print_status "Backing up ChromaDB data..."
        tar czf "$BACKUP_DIR/chroma_db_flowers.tar.gz" chroma_db_flowers/
    fi
    
    # Backup logs
    if [[ -d "logs" ]]; then
        print_status "Backing up logs..."
        tar czf "$BACKUP_DIR/logs.tar.gz" logs/
    fi
    
    print_success "Backup created in: $BACKUP_DIR"
fi

# Build Docker compose command
COMPOSE_CMD="docker-compose -f $COMPOSE_FILE"
if [[ -n "$OVERRIDE_FILE" ]]; then
    COMPOSE_CMD="$COMPOSE_CMD -f $OVERRIDE_FILE"
fi

# Stop existing containers
print_status "Stopping existing containers..."
$COMPOSE_CMD down

# Pull or build images
if [[ "$BUILD_IMAGES" == true ]]; then
    print_status "Building images..."
    $COMPOSE_CMD build --no-cache
elif [[ "$PULL_IMAGES" == true ]]; then
    print_status "Pulling latest images..."
    $COMPOSE_CMD pull
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs chroma_db_flowers data

# Set proper permissions
print_status "Setting permissions..."
chmod 755 logs chroma_db_flowers data

# Start services
print_status "Starting services..."
$COMPOSE_CMD up -d

# Wait for services to be healthy
print_status "Waiting for services to be healthy..."
sleep 10

# Check service health
print_status "Checking service health..."
HEALTH_CHECK_RETRIES=30
HEALTH_CHECK_INTERVAL=5

for i in $(seq 1 $HEALTH_CHECK_RETRIES); do
    if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Application is healthy!"
        break
    elif [[ $i -eq $HEALTH_CHECK_RETRIES ]]; then
        print_error "Application failed to become healthy after $((HEALTH_CHECK_RETRIES * HEALTH_CHECK_INTERVAL)) seconds"
        print_error "Check logs with: $COMPOSE_CMD logs"
        exit 1
    else
        print_status "Waiting for application to become healthy... (attempt $i/$HEALTH_CHECK_RETRIES)"
        sleep $HEALTH_CHECK_INTERVAL
    fi
done

# Show running services
print_status "Running services:"
$COMPOSE_CMD ps

# Show useful commands
print_success "Deployment completed successfully!"
echo ""
print_status "Useful commands:"
echo "  View logs:           $COMPOSE_CMD logs -f"
echo "  Check status:        $COMPOSE_CMD ps"
echo "  Stop services:       $COMPOSE_CMD down"
echo "  Restart service:     $COMPOSE_CMD restart xoflowers-ai"
echo "  Health check:        curl http://localhost:8000/health"
echo "  API documentation:   http://localhost:8000/docs"

if [[ "$ENVIRONMENT" == "production" ]]; then
    echo ""
    print_warning "Production deployment notes:"
    echo "  - Configure SSL certificates in nginx.conf"
    echo "  - Set up proper domain name and DNS"
    echo "  - Configure monitoring and alerting"
    echo "  - Set up log rotation and backup strategies"
    echo "  - Review security settings and firewall rules"
fi