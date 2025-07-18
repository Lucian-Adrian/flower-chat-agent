"""
Utility functions for XOFlowers AI Agent
Centralized logging configuration, monitoring, and shared utility functions
"""

import logging
import os
import sys
import time
import json
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pathlib import Path
from collections import defaultdict, deque
from dataclasses import dataclass, asdict


def setup_logger(name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Configure consistent logging across all modules
    Logs to both console and file with structured format
    
    Args:
        name: Logger name (typically __name__ from calling module)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Prevent duplicate handlers if logger already configured
    if logger.handlers:
        return logger
    
    # Set logging level
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # File handler for persistent logging
    log_file = logs_dir / "xoflowers_ai.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)  # Always log DEBUG to file
    
    # Detailed formatter for file logs
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Simpler formatter for console
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    console_handler.setFormatter(console_formatter)
    file_handler.setFormatter(file_formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


def log_ai_interaction(logger: logging.Logger, 
                      user_id: str, 
                      message: str, 
                      response: str, 
                      processing_time: float,
                      intent: Optional[str] = None,
                      confidence: Optional[float] = None) -> None:
    """
    Log AI interaction with structured format for analysis
    
    Args:
        logger: Logger instance
        user_id: User identifier
        message: User message
        response: AI response
        processing_time: Time taken to process in seconds
        intent: Detected intent (optional)
        confidence: Intent confidence score (optional)
    """
    log_data = {
        'user_id': user_id,
        'message_length': len(message),
        'response_length': len(response),
        'processing_time': round(processing_time, 3),
        'intent': intent,
        'confidence': round(confidence, 3) if confidence else None,
        'timestamp': datetime.now().isoformat()
    }
    
    logger.info(f"AI_INTERACTION: {log_data}")


def log_security_check(logger: logging.Logger,
                      user_id: str,
                      message: str,
                      is_safe: bool,
                      risk_level: str,
                      detected_issues: list) -> None:
    """
    Log security check results
    
    Args:
        logger: Logger instance
        user_id: User identifier
        message: User message (truncated for security)
        is_safe: Whether message passed security check
        risk_level: Risk level (low/medium/high)
        detected_issues: List of detected security issues
    """
    # Truncate message for security logging
    safe_message = message[:50] + "..." if len(message) > 50 else message
    
    log_data = {
        'user_id': user_id,
        'message_preview': safe_message,
        'is_safe': is_safe,
        'risk_level': risk_level,
        'issues_count': len(detected_issues),
        'issues': detected_issues,
        'timestamp': datetime.now().isoformat()
    }
    
    if is_safe:
        logger.info(f"SECURITY_PASS: {log_data}")
    else:
        logger.warning(f"SECURITY_BLOCK: {log_data}")


def log_performance_metrics(logger: logging.Logger,
                           operation: str,
                           duration: float,
                           success: bool,
                           details: Optional[Dict[str, Any]] = None) -> None:
    """
    Log performance metrics for system operations
    
    Args:
        logger: Logger instance
        operation: Operation name (e.g., 'chromadb_search', 'redis_get')
        duration: Operation duration in seconds
        success: Whether operation succeeded
        details: Additional operation details
    """
    log_data = {
        'operation': operation,
        'duration': round(duration, 3),
        'success': success,
        'timestamp': datetime.now().isoformat()
    }
    
    if details:
        log_data.update(details)
    
    if success:
        logger.info(f"PERFORMANCE: {log_data}")
    else:
        logger.error(f"PERFORMANCE_ERROR: {log_data}")


def log_fallback_activation(logger: logging.Logger,
                           service: str,
                           fallback_to: str,
                           reason: str,
                           user_id: Optional[str] = None) -> None:
    """
    Log when fallback systems are activated
    
    Args:
        logger: Logger instance
        service: Primary service that failed
        fallback_to: Fallback service being used
        reason: Reason for fallback
        user_id: User ID if applicable
    """
    log_data = {
        'primary_service': service,
        'fallback_service': fallback_to,
        'reason': reason,
        'user_id': user_id,
        'timestamp': datetime.now().isoformat()
    }
    
    logger.warning(f"FALLBACK_ACTIVATED: {log_data}")


def sanitize_for_logging(text: str, max_length: int = 100) -> str:
    """
    Sanitize text for safe logging (remove sensitive info, truncate)
    
    Args:
        text: Text to sanitize
        max_length: Maximum length to keep
    
    Returns:
        Sanitized text safe for logging
    """
    if not text:
        return ""
    
    # Remove potential sensitive patterns
    sanitized = text.replace('\n', ' ').replace('\r', ' ')
    
    # Truncate if too long
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "..."
    
    return sanitized


def get_log_level_from_env() -> str:
    """
    Get logging level from environment variable
    
    Returns:
        Log level string (defaults to INFO)
    """
    return os.getenv('LOG_LEVEL', 'INFO').upper()


def create_request_id() -> str:
    """
    Create unique request ID for tracking requests across logs
    
    Returns:
        Unique request identifier
    """
    from uuid import uuid4
    return str(uuid4())[:8]


# Performance Monitoring Classes and Functions

@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    operation: str
    duration: float
    success: bool
    timestamp: datetime
    details: Dict[str, Any]

@dataclass
class SystemHealth:
    """System health status"""
    redis_available: bool
    chromadb_available: bool
    openai_available: bool
    gemini_available: bool
    avg_response_time: float
    error_rate: float
    active_users: int
    cache_hit_rate: float
    timestamp: datetime

class PerformanceMonitor:
    """
    Comprehensive performance monitoring and metrics collection
    Thread-safe implementation for concurrent access
    """
    
    def __init__(self, max_metrics: int = 1000):
        self.max_metrics = max_metrics
        self._metrics = deque(maxlen=max_metrics)
        self._operation_stats = defaultdict(list)
        self._error_counts = defaultdict(int)
        self._user_activity = defaultdict(int)
        self._cache_stats = {'hits': 0, 'misses': 0}
        self._lock = threading.Lock()
        self.logger = setup_logger(__name__)
        
        # Start background cleanup task
        self._start_cleanup_task()
    
    def record_metric(self, operation: str, duration: float, success: bool, 
                     details: Optional[Dict[str, Any]] = None) -> None:
        """Record a performance metric"""
        with self._lock:
            metric = PerformanceMetric(
                operation=operation,
                duration=duration,
                success=success,
                timestamp=datetime.now(),
                details=details or {}
            )
            
            self._metrics.append(metric)
            self._operation_stats[operation].append(duration)
            
            if not success:
                self._error_counts[operation] += 1
            
            # Keep operation stats manageable
            if len(self._operation_stats[operation]) > 100:
                self._operation_stats[operation] = self._operation_stats[operation][-50:]
    
    def record_user_activity(self, user_id: str) -> None:
        """Record user activity for monitoring active users"""
        with self._lock:
            self._user_activity[user_id] = int(time.time())
    
    def record_cache_hit(self, hit: bool) -> None:
        """Record cache hit/miss statistics"""
        with self._lock:
            if hit:
                self._cache_stats['hits'] += 1
            else:
                self._cache_stats['misses'] += 1
    
    def get_operation_stats(self, operation: str) -> Dict[str, Any]:
        """Get statistics for a specific operation"""
        with self._lock:
            durations = self._operation_stats.get(operation, [])
            if not durations:
                return {'operation': operation, 'count': 0}
            
            return {
                'operation': operation,
                'count': len(durations),
                'avg_duration': sum(durations) / len(durations),
                'min_duration': min(durations),
                'max_duration': max(durations),
                'error_count': self._error_counts.get(operation, 0),
                'success_rate': 1 - (self._error_counts.get(operation, 0) / len(durations))
            }
    
    def get_system_health(self) -> SystemHealth:
        """Get comprehensive system health status"""
        with self._lock:
            # Calculate average response time
            all_durations = []
            for durations in self._operation_stats.values():
                all_durations.extend(durations)
            
            avg_response_time = sum(all_durations) / len(all_durations) if all_durations else 0
            
            # Calculate error rate
            total_operations = len(self._metrics)
            total_errors = sum(self._error_counts.values())
            error_rate = total_errors / total_operations if total_operations > 0 else 0
            
            # Calculate active users (last 5 minutes)
            current_time = int(time.time())
            active_users = sum(
                1 for last_activity in self._user_activity.values()
                if current_time - last_activity < 300  # 5 minutes
            )
            
            # Calculate cache hit rate
            total_cache_requests = self._cache_stats['hits'] + self._cache_stats['misses']
            cache_hit_rate = self._cache_stats['hits'] / total_cache_requests if total_cache_requests > 0 else 0
            
            return SystemHealth(
                redis_available=self._check_service_health('redis'),
                chromadb_available=self._check_service_health('chromadb'),
                openai_available=self._check_service_health('openai'),
                gemini_available=self._check_service_health('gemini'),
                avg_response_time=avg_response_time,
                error_rate=error_rate,
                active_users=active_users,
                cache_hit_rate=cache_hit_rate,
                timestamp=datetime.now()
            )
    
    def _check_service_health(self, service: str) -> bool:
        """Check if a service is healthy based on recent metrics"""
        recent_metrics = [
            m for m in self._metrics 
            if m.operation.startswith(service) and 
            datetime.now() - m.timestamp < timedelta(minutes=5)
        ]
        
        if not recent_metrics:
            return True  # No recent activity, assume healthy
        
        success_rate = sum(1 for m in recent_metrics if m.success) / len(recent_metrics)
        return success_rate > 0.8  # 80% success rate threshold
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        with self._lock:
            operations_summary = {}
            for operation in self._operation_stats.keys():
                operations_summary[operation] = self.get_operation_stats(operation)
            
            health = self.get_system_health()
            
            return {
                'system_health': asdict(health),
                'operations': operations_summary,
                'total_metrics': len(self._metrics),
                'cache_stats': self._cache_stats.copy(),
                'active_operations': list(self._operation_stats.keys()),
                'generated_at': datetime.now().isoformat()
            }
    
    def _start_cleanup_task(self) -> None:
        """Start background task to clean up old data"""
        def cleanup():
            while True:
                time.sleep(300)  # Run every 5 minutes
                self._cleanup_old_data()
        
        cleanup_thread = threading.Thread(target=cleanup, daemon=True)
        cleanup_thread.start()
    
    def _cleanup_old_data(self) -> None:
        """Clean up old user activity data"""
        with self._lock:
            current_time = int(time.time())
            # Remove user activity older than 1 hour
            expired_users = [
                user_id for user_id, last_activity in self._user_activity.items()
                if current_time - last_activity > 3600
            ]
            
            for user_id in expired_users:
                del self._user_activity[user_id]
            
            if expired_users:
                self.logger.debug(f"Cleaned up activity data for {len(expired_users)} inactive users")

# Global performance monitor instance
_performance_monitor = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor

# Enhanced logging functions with performance monitoring

def log_ai_interaction_with_monitoring(logger: logging.Logger, 
                                     user_id: str, 
                                     message: str, 
                                     response: str, 
                                     processing_time: float,
                                     intent: Optional[str] = None,
                                     confidence: Optional[float] = None,
                                     service_used: Optional[str] = None) -> None:
    """
    Enhanced AI interaction logging with performance monitoring
    """
    # Record performance metric
    monitor = get_performance_monitor()
    monitor.record_metric(
        operation=f"ai_interaction_{service_used}" if service_used else "ai_interaction",
        duration=processing_time,
        success=True,
        details={
            'intent': intent,
            'confidence': confidence,
            'message_length': len(message),
            'response_length': len(response)
        }
    )
    
    # Record user activity
    monitor.record_user_activity(user_id)
    
    # Log the interaction
    log_ai_interaction(logger, user_id, message, response, processing_time, intent, confidence)

def log_error_with_monitoring(logger: logging.Logger,
                            operation: str,
                            error: Exception,
                            duration: float = 0,
                            details: Optional[Dict[str, Any]] = None) -> None:
    """
    Log errors with performance monitoring
    """
    # Record performance metric for failed operation
    monitor = get_performance_monitor()
    monitor.record_metric(
        operation=operation,
        duration=duration,
        success=False,
        details={
            'error_type': type(error).__name__,
            'error_message': str(error),
            **(details or {})
        }
    )
    
    # Log the error
    error_data = {
        'operation': operation,
        'error_type': type(error).__name__,
        'error_message': str(error),
        'duration': round(duration, 3),
        'timestamp': datetime.now().isoformat()
    }
    
    if details:
        error_data.update(details)
    
    logger.error(f"OPERATION_ERROR: {error_data}")

def log_cache_operation(logger: logging.Logger,
                       operation: str,
                       cache_key: str,
                       hit: bool,
                       duration: float = 0) -> None:
    """
    Log cache operations with monitoring
    """
    # Record cache statistics
    monitor = get_performance_monitor()
    monitor.record_cache_hit(hit)
    
    if duration > 0:
        monitor.record_metric(
            operation=f"cache_{operation}",
            duration=duration,
            success=True,
            details={'hit': hit, 'key_hash': hash(cache_key) % 10000}
        )
    
    # Log cache operation
    cache_data = {
        'operation': operation,
        'hit': hit,
        'duration': round(duration, 3) if duration > 0 else 0,
        'timestamp': datetime.now().isoformat()
    }
    
    logger.debug(f"CACHE_{'HIT' if hit else 'MISS'}: {cache_data}")

# Context manager for performance timing

class PerformanceTimer:
    """Context manager for timing operations with automatic logging"""
    
    def __init__(self, operation: str, logger: logging.Logger, 
                 details: Optional[Dict[str, Any]] = None):
        self.operation = operation
        self.logger = logger
        self.details = details or {}
        self.start_time = None
        self.duration = 0
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.duration = time.time() - self.start_time
        success = exc_type is None
        
        # Record performance metric
        monitor = get_performance_monitor()
        monitor.record_metric(
            operation=self.operation,
            duration=self.duration,
            success=success,
            details=self.details
        )
        
        # Log performance
        if success:
            log_performance_metrics(self.logger, self.operation, self.duration, True, self.details)
        else:
            log_error_with_monitoring(
                self.logger, self.operation, exc_val, self.duration, self.details
            )

# Health check functions

def get_system_health_report() -> Dict[str, Any]:
    """Get comprehensive system health report"""
    monitor = get_performance_monitor()
    return monitor.get_performance_summary()

def log_system_health(logger: logging.Logger) -> None:
    """Log current system health status"""
    try:
        health_report = get_system_health_report()
        logger.info(f"SYSTEM_HEALTH: {json.dumps(health_report, indent=2)}")
    except Exception as e:
        logger.error(f"Failed to generate system health report: {e}")

# Global logger for utility functions
_utils_logger = None

def get_utils_logger() -> logging.Logger:
    """Get logger for utility functions"""
    global _utils_logger
    if _utils_logger is None:
        _utils_logger = setup_logger(__name__)
    return _utils_logger