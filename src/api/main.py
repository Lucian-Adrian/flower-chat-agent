"""
FastAPI Main Application for XOFlowers AI Agent
Async message processing endpoint with Pydantic validation and comprehensive error handling
"""

import asyncio
import time
from datetime import datetime
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
import uvicorn

from src.utils.system_definitions import get_service_config, get_business_info, get_performance_config
from src.helpers.utils import setup_logger, log_performance_metrics, create_request_id
from src.intelligence.ai_engine import process_message_ai
from src.api.telegram_integration import get_telegram_router
from src.api.instagram_integration import get_instagram_router


# Pydantic Models for Request/Response Validation
class MessageRequest(BaseModel):
    """Request model for message processing"""
    message: str = Field(..., min_length=1, max_length=1000, description="User message text")
    user_id: str = Field(..., min_length=1, max_length=100, description="Unique user identifier")
    platform: Optional[str] = Field("api", description="Platform source (telegram, instagram, api)")
    context: Optional[Dict[str, Any]] = Field(None, description="Optional conversation context")
    
    @validator('message')
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()
    
    @validator('user_id')
    def validate_user_id(cls, v):
        if not v or not v.strip():
            raise ValueError('User ID cannot be empty')
        return v.strip()
    
    @validator('platform')
    def validate_platform(cls, v):
        allowed_platforms = ['telegram', 'instagram', 'api', 'web']
        if v and v not in allowed_platforms:
            raise ValueError(f'Platform must be one of: {allowed_platforms}')
        return v


class MessageResponse(BaseModel):
    """Response model for message processing"""
    response: str = Field(..., description="AI-generated response text")
    success: bool = Field(..., description="Whether processing was successful")
    request_id: str = Field(..., description="Unique request identifier")
    processing_time: float = Field(..., description="Processing time in seconds")
    intent: Optional[str] = Field(None, description="Detected user intent")
    confidence: Optional[float] = Field(None, description="Intent confidence score")
    context_updated: bool = Field(False, description="Whether conversation context was updated")
    service_used: Optional[str] = Field(None, description="AI service used for processing")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional processing metadata")


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Current timestamp")
    version: str = Field(..., description="API version")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    services: Dict[str, str] = Field(..., description="Status of dependent services")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")
    request_id: Optional[str] = Field(None, description="Request identifier")
    timestamp: datetime = Field(..., description="Error timestamp")


# Global variables for application state
app_start_time = time.time()
logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting XOFlowers AI Agent API")
    logger.info("Initializing AI services...")
    
    # Pre-warm AI engine
    try:
        from src.intelligence.ai_engine import get_ai_engine
        ai_engine = get_ai_engine()
        logger.info("AI engine initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize AI engine: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down XOFlowers AI Agent API")


# Create FastAPI application
app = FastAPI(
    title="XOFlowers AI Agent API",
    description="AI-powered conversational agent for XOFlowers flower shop",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include platform-specific routers
app.include_router(get_telegram_router())
app.include_router(get_instagram_router())


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.warning(f"HTTP exception [{request_id}]: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            error_code=f"HTTP_{exc.status_code}",
            request_id=request_id,
            timestamp=datetime.now()
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.error(f"Unhandled exception [{request_id}]: {type(exc).__name__}: {exc}")
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            error_code="INTERNAL_ERROR",
            request_id=request_id,
            timestamp=datetime.now()
        ).dict()
    )


# Middleware for request tracking
@app.middleware("http")
async def add_request_id_middleware(request: Request, call_next):
    """Add request ID to all requests for tracking"""
    request_id = create_request_id()
    request.state.request_id = request_id
    
    start_time = time.time()
    response = await call_next(request)
    processing_time = time.time() - start_time
    
    # Add request ID to response headers
    response.headers["X-Request-ID"] = request_id
    
    # Log request
    logger.info(f"Request [{request_id}]: {request.method} {request.url.path} - "
               f"{response.status_code} - {processing_time:.3f}s")
    
    return response


# API Endpoints
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with basic API information"""
    return {
        "service": "XOFlowers AI Agent API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check endpoint for container orchestration"""
    uptime = time.time() - app_start_time
    
    # Check service dependencies
    services_status = {}
    overall_healthy = True
    
    # Check AI engine
    try:
        from src.intelligence.ai_engine import get_ai_engine
        ai_engine = get_ai_engine()
        cache_stats = ai_engine.get_cache_stats()
        services_status["ai_engine"] = {
            "status": "healthy",
            "cache_entries": cache_stats.get('active_entries', 0),
            "max_concurrent_openai": cache_stats.get('max_concurrent_openai', 0),
            "max_concurrent_gemini": cache_stats.get('max_concurrent_gemini', 0)
        }
    except Exception as e:
        services_status["ai_engine"] = {"status": "unhealthy", "error": str(e)}
        overall_healthy = False
    
    # Check Redis (optional)
    try:
        from src.data.redis_client import health_check_redis
        redis_health = health_check_redis()
        services_status["redis"] = redis_health
        if redis_health.get('status') != 'healthy':
            overall_healthy = False
    except Exception as e:
        services_status["redis"] = {"status": "unavailable", "error": str(e)}
    
    # Check ChromaDB (optional)
    try:
        from src.data.chromadb_client import health_check_chromadb
        chromadb_health = health_check_chromadb()
        services_status["chromadb"] = chromadb_health
        if chromadb_health.get('status') != 'healthy':
            overall_healthy = False
    except Exception as e:
        services_status["chromadb"] = {"status": "unavailable", "error": str(e)}
    
    # Check performance monitoring
    try:
        from src.helpers.utils import get_system_health_report
        health_report = get_system_health_report()
        services_status["performance_monitor"] = {
            "status": "healthy",
            "active_users": health_report['system_health']['active_users'],
            "avg_response_time": health_report['system_health']['avg_response_time'],
            "error_rate": health_report['system_health']['error_rate'],
            "cache_hit_rate": health_report['system_health']['cache_hit_rate']
        }
    except Exception as e:
        services_status["performance_monitor"] = {"status": "error", "error": str(e)}
    
    return HealthResponse(
        status="healthy" if overall_healthy else "degraded",
        timestamp=datetime.now(),
        version="1.0.0",
        uptime_seconds=uptime,
        services=services_status
    )


@app.get("/health/live", response_model=Dict[str, str])
async def liveness_probe():
    """Kubernetes/Docker liveness probe - simple check that app is running"""
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health/ready", response_model=Dict[str, Any])
async def readiness_probe():
    """Kubernetes/Docker readiness probe - check if app is ready to serve traffic"""
    try:
        # Quick check of critical services
        from src.intelligence.ai_engine import get_ai_engine
        ai_engine = get_ai_engine()
        
        # Test basic AI functionality
        test_result = await process_message_ai(
            user_message="test",
            user_id="health_check",
            context={}
        )
        
        if test_result.get('success', False):
            return {
                "status": "ready",
                "timestamp": datetime.now().isoformat(),
                "services": {
                    "ai_engine": "ready"
                }
            }
        else:
            return {
                "status": "not_ready",
                "timestamp": datetime.now().isoformat(),
                "reason": "AI engine test failed"
            }
            
    except Exception as e:
        logger.error(f"Readiness probe failed: {e}")
        return {
            "status": "not_ready",
            "timestamp": datetime.now().isoformat(),
            "reason": str(e)
        }


@app.post("/api/chat", response_model=MessageResponse)
async def process_message(request: MessageRequest, background_tasks: BackgroundTasks, 
                         http_request: Request) -> MessageResponse:
    """
    Main message processing endpoint
    
    Process user messages through AI pipeline and return responses
    """
    request_id = http_request.state.request_id
    start_time = time.time()
    
    logger.info(f"Processing message [{request_id}] from user {request.user_id} "
               f"via {request.platform}")
    
    try:
        # Validate request timing
        performance_config = get_performance_config()
        timeout = performance_config['response_timeout_seconds']
        
        # Process message through AI pipeline with timeout
        result = await asyncio.wait_for(
            process_message_ai(
                user_message=request.message,
                user_id=request.user_id,
                context=request.context
            ),
            timeout=timeout
        )
        
        processing_time = time.time() - start_time
        
        # Log performance metrics in background
        background_tasks.add_task(
            log_performance_metrics,
            logger,
            "message_processing",
            processing_time,
            result.get('success', False),
            {
                "request_id": request_id,
                "user_id": request.user_id,
                "platform": request.platform,
                "intent": result.get('intent'),
                "service_used": result.get('service_used')
            }
        )
        
        # Prepare response
        response = MessageResponse(
            response=result.get('response', ''),
            success=result.get('success', False),
            request_id=request_id,
            processing_time=processing_time,
            intent=result.get('intent'),
            confidence=result.get('confidence'),
            context_updated=result.get('context_updated', False),
            service_used=result.get('service_used'),
            metadata={
                "platform": request.platform,
                "security_blocked": result.get('security_blocked', False),
                "risk_level": result.get('risk_level'),
                "detected_issues": result.get('detected_issues', [])
            }
        )
        
        logger.info(f"Message processed successfully [{request_id}] - "
                   f"{processing_time:.3f}s - Intent: {result.get('intent')} - "
                   f"Service: {result.get('service_used')}")
        
        return response
        
    except asyncio.TimeoutError:
        processing_time = time.time() - start_time
        logger.error(f"Message processing timeout [{request_id}] after {processing_time:.3f}s")
        
        # Log timeout in background
        background_tasks.add_task(
            log_performance_metrics,
            logger,
            "message_processing",
            processing_time,
            False,
            {
                "request_id": request_id,
                "error": "timeout",
                "timeout_seconds": timeout
            }
        )
        
        raise HTTPException(
            status_code=408,
            detail=f"Request timeout after {timeout} seconds"
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Message processing failed [{request_id}]: {type(e).__name__}: {e}")
        
        # Log error in background
        background_tasks.add_task(
            log_performance_metrics,
            logger,
            "message_processing",
            processing_time,
            False,
            {
                "request_id": request_id,
                "error": str(e),
                "error_type": type(e).__name__
            }
        )
        
        raise HTTPException(
            status_code=500,
            detail="Failed to process message"
        )


@app.get("/metrics", response_model=Dict[str, Any])
async def get_metrics():
    """Get comprehensive system metrics and performance data"""
    try:
        from src.helpers.utils import get_system_health_report
        health_report = get_system_health_report()
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "metrics": health_report
        }
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve system metrics"
        )


@app.get("/api/business-info", response_model=Dict[str, Any])
async def get_business_info():
    """Get business information endpoint"""
    try:
        business_info = get_business_info()
        return {
            "success": True,
            "data": business_info
        }
    except Exception as e:
        logger.error(f"Failed to get business info: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve business information"
        )


@app.get("/api/status", response_model=Dict[str, Any])
async def get_api_status():
    """Get detailed API status"""
    uptime = time.time() - app_start_time
    
    return {
        "service": "XOFlowers AI Agent API",
        "status": "running",
        "uptime_seconds": uptime,
        "uptime_formatted": f"{uptime // 3600:.0f}h {(uptime % 3600) // 60:.0f}m {uptime % 60:.0f}s",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


# Development server runner
if __name__ == "__main__":
    # Get configuration
    service_config = get_service_config()
    fastapi_config = service_config['fastapi']
    
    logger.info(f"Starting FastAPI server on {fastapi_config['host']}:{fastapi_config['port']}")
    
    uvicorn.run(
        "src.api.main:app",
        host=fastapi_config['host'],
        port=fastapi_config['port'],
        reload=fastapi_config['reload'],
        log_level=fastapi_config['log_level']
    )