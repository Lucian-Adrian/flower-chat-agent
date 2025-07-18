# XOFlowers AI Agent - Deployment Guide (2025)

**CURRENT IMPLEMENTATION** - FastAPI with ChromaDB, Redis Fallback, and Multi-Platform Bot Integration

This guide covers deploying the **current working version** of the XOFlowers AI Agent with all 2025 enhancements.

## 🚀 Quick Start

### Development Deployment
```bash
# 1. Clone and setup
git clone <repository>
cd xoflowers-agent

# 2. Copy environment template  
cp .env.example .env

# 3. Edit .env with your configuration
# Required: OPENAI_API_KEY or GEMINI_API_KEY
# Required: TELEGRAM_BOT_TOKEN
# Optional: Instagram API credentials

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run main FastAPI application
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# 6. Check health
curl http://localhost:8000/health
```

### Production Deployment
```bash
# 1. Validate configuration
python scripts/validate-deployment.py

# 2. Deploy production stack
./deploy.sh -e production --backup

# 3. Or on Windows  
.\deploy.ps1 -Environment production -Backup

# 4. Check all services
docker-compose ps
curl http://localhost:8000/health
```

## 🎯 Current Architecture

The **2025 implementation** uses:

- **FastAPI** as main application (`src/api/main.py`)
- **ChromaDB** for product search (692 products)
- **Redis** with in-memory fallback for context
- **Gemini Chat** with OpenAI fallback for AI
- **Integrated bots** for Telegram and Instagram
- **Docker Compose** for production deployment

## 🔧 Environment Configuration

### Required Variables (Production)
```bash
# At least one AI service API key
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key

# At least one platform integration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token
```

#### Application Settings
```bash
ENVIRONMENT=production          # development|staging|production
LOG_LEVEL=INFO                 # DEBUG|INFO|WARNING|ERROR|CRITICAL
DEBUG=false                    # true|false
```

#### Service Configuration
```bash
# Redis (for conversation context)
REDIS_HOST=redis               # Container: redis, Local: localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=                # Optional

# ChromaDB (for product search)
CHROMADB_PATH=/app/chroma_db_flowers
CHROMADB_COLLECTION=xoflowers_products
```

#### Platform Integration
```bash
# Telegram
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_WEBHOOK_URL=https://your-domain.com/api/telegram/webhook

# Instagram
INSTAGRAM_VERIFY_TOKEN=your_verify_token
INSTAGRAM_ACCESS_TOKEN=your_access_token
INSTAGRAM_WEBHOOK_URL=https://your-domain.com/api/instagram/webhook
```

#### Performance & Security
```bash
MAX_MESSAGE_LENGTH=1000
SECURITY_ENABLED=true
CACHE_TTL_SECONDS=600
MAX_CONCURRENT_REQUESTS=20
REQUEST_TIMEOUT_SECONDS=25
```

#### Monitoring
```bash
HEALTH_CHECK_ENABLED=true
METRICS_ENABLED=true
PERFORMANCE_MONITORING=true
```

### Environment Files

- `.env.example` - Template with all available options
- `.env` - Local development configuration
- `.env.production` - Production configuration template

## Docker Deployment

### Single Container
```bash
# Build image
docker build -t xoflowers-ai .

# Run container
docker run -d \
  --name xoflowers-ai \
  -p 8000:8000 \
  --env-file .env.production \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/chroma_db_flowers:/app/chroma_db_flowers \
  xoflowers-ai
```

### Docker Compose (Recommended)

#### Development
```bash
docker-compose up -d
```

#### Production
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Docker Compose Services

- **xoflowers-ai** - Main application
- **redis** - Conversation context storage
- **nginx** - Reverse proxy and load balancer
- **prometheus** - Metrics collection (optional)
- **grafana** - Monitoring dashboards (optional)

## Health Checks & Monitoring

### Health Check Endpoints

#### `/health` - Comprehensive Health Check
Returns detailed status of all services:
```json
{
  "status": "healthy",
  "timestamp": "2025-07-17T10:30:00Z",
  "version": "1.0.0",
  "uptime_seconds": 3600,
  "services": {
    "ai_engine": {"status": "healthy"},
    "redis": {"status": "healthy"},
    "chromadb": {"status": "healthy"}
  }
}
```

#### `/health/live` - Liveness Probe
Simple check that application is running:
```json
{
  "status": "alive",
  "timestamp": "2025-07-17T10:30:00Z"
}
```

#### `/health/ready` - Readiness Probe
Check if application is ready to serve traffic:
```json
{
  "status": "ready",
  "timestamp": "2025-07-17T10:30:00Z",
  "services": {
    "ai_engine": "ready"
  }
}
```

### Container Health Checks

Docker containers include built-in health checks:
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD /usr/local/bin/healthcheck.sh
```

### Monitoring Stack

Optional monitoring with Prometheus and Grafana:
```bash
# Deploy with monitoring
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Access Grafana
open http://localhost:3000
# Default: admin/admin

# Access Prometheus
open http://localhost:9090
```

## Deployment Scripts

### Bash Script (Linux/macOS)
```bash
./deploy.sh [OPTIONS]

Options:
  -e, --environment ENV    Set environment (development|staging|production)
  -b, --build             Build images locally
  -n, --no-pull           Don't pull images
  --backup                Create backup before deployment
  -h, --help              Show help
```

### PowerShell Script (Windows)
```powershell
.\deploy.ps1 [OPTIONS]

Parameters:
  -Environment ENV        Set environment
  -Build                  Build images locally
  -NoPull                 Don't pull images
  -Backup                 Create backup before deployment
  -Help                   Show help
```

## Configuration Validation

### Pre-deployment Validation
```bash
# Validate configuration
python scripts/validate-deployment.py

# Example output:
# 🔍 XOFlowers AI Agent - Deployment Configuration Validation
# ✅ Configuration Valid: true
# 🟢 Configuration is valid and ready for deployment!
```

### Validation Checks
- Environment variable presence and format
- API key availability
- Service connectivity (Redis, ChromaDB)
- Performance setting validation
- Security configuration verification

## Production Considerations

### Security
- Set strong Redis password if exposed
- Configure SSL certificates in nginx.conf
- Use secrets management for API keys
- Enable firewall rules
- Regular security updates

### Performance
- Monitor resource usage
- Configure appropriate resource limits
- Set up log rotation
- Implement backup strategies
- Monitor response times

### Scaling
- Use container orchestration (Kubernetes, Docker Swarm)
- Implement horizontal scaling
- Configure load balancing
- Set up auto-scaling policies

### Monitoring & Alerting
- Set up log aggregation
- Configure metric collection
- Implement alerting rules
- Monitor business metrics
- Track error rates and response times

## Troubleshooting

### Common Issues

#### Container Won't Start
```bash
# Check logs
docker-compose logs xoflowers-ai

# Common causes:
# - Missing environment variables
# - Port conflicts
# - Volume mount issues
```

#### Health Check Failures
```bash
# Check health endpoint directly
curl http://localhost:8000/health

# Check container health
docker inspect xoflowers-ai | grep Health -A 10
```

#### Service Dependencies
```bash
# Check Redis connectivity
docker-compose exec redis redis-cli ping

# Check ChromaDB data
ls -la chroma_db_flowers/
```

### Log Analysis
```bash
# View application logs
docker-compose logs -f xoflowers-ai

# View all service logs
docker-compose logs -f

# Filter by service
docker-compose logs -f redis
```

### Performance Issues
```bash
# Check resource usage
docker stats

# Monitor metrics endpoint
curl http://localhost:8000/metrics

# Check system health
curl http://localhost:8000/health
```

## Backup & Recovery

### Automated Backups
The deployment scripts include backup functionality:
```bash
# Create backup before deployment
./deploy.sh --backup

# Backup location
ls backups/
```

### Manual Backup
```bash
# Backup Redis data
docker run --rm -v xoflowers_redis_data:/data -v $(pwd)/backup:/backup alpine tar czf /backup/redis_data.tar.gz -C /data .

# Backup ChromaDB
tar czf backup/chroma_db_flowers.tar.gz chroma_db_flowers/

# Backup logs
tar czf backup/logs.tar.gz logs/
```

### Recovery
```bash
# Restore Redis data
docker run --rm -v xoflowers_redis_data:/data -v $(pwd)/backup:/backup alpine tar xzf /backup/redis_data.tar.gz -C /data

# Restore ChromaDB
tar xzf backup/chroma_db_flowers.tar.gz

# Restart services
docker-compose restart
```

## Environment-Specific Configurations

### Development
- Debug logging enabled
- Hot reload for code changes
- Exposed ports for debugging
- Minimal resource limits

### Staging
- Production-like configuration
- Reduced resource allocation
- Test data and configurations
- Monitoring enabled

### Production
- Optimized performance settings
- Resource limits and reservations
- SSL/TLS configuration
- Comprehensive monitoring
- Backup strategies
- Security hardening

## API Documentation

Once deployed, access the interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Support

For deployment issues:
1. Check this documentation
2. Validate configuration with `scripts/validate-deployment.py`
3. Review logs with `docker-compose logs`
4. Check health endpoints
5. Consult troubleshooting section