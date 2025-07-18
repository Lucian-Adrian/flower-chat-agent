#!/bin/bash

# Docker Health Check Script for XOFlowers AI Agent
# This script is used by Docker to check container health

set -e

# Configuration
HEALTH_URL="http://localhost:8000/health/live"
TIMEOUT=10
MAX_RETRIES=3

# Function to check health
check_health() {
    local attempt=1
    
    while [ $attempt -le $MAX_RETRIES ]; do
        echo "Health check attempt $attempt/$MAX_RETRIES"
        
        # Use curl to check health endpoint
        if curl -f -s --max-time $TIMEOUT "$HEALTH_URL" > /dev/null 2>&1; then
            echo "Health check passed"
            return 0
        fi
        
        echo "Health check failed (attempt $attempt)"
        attempt=$((attempt + 1))
        
        # Wait before retry (except on last attempt)
        if [ $attempt -le $MAX_RETRIES ]; then
            sleep 2
        fi
    done
    
    echo "Health check failed after $MAX_RETRIES attempts"
    return 1
}

# Run health check
check_health