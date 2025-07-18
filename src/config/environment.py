"""
Environment Configuration Management for XOFlowers AI Agent
Centralized environment variable handling with validation and defaults
"""

import os
from typing import Optional, Dict, Any, Union
from pathlib import Path
from dataclasses import dataclass

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    env_file = Path('.env')
    if env_file.exists():
        load_dotenv(env_file)
        print(f"Loaded environment variables from {env_file}")
    else:
        print("No .env file found, using system environment variables")
except ImportError:
    print("python-dotenv not installed, using system environment variables only")


@dataclass
class EnvironmentConfig:
    """Environment configuration data structure"""
    # Application Settings
    environment: str
    log_level: str
    debug: bool
    
    # API Keys
    openai_api_key: Optional[str]
    gemini_api_key: Optional[str]
    
    # Redis Configuration
    redis_host: str
    redis_port: int
    redis_db: int
    redis_password: Optional[str]
    
    # ChromaDB Configuration
    chromadb_path: str
    chromadb_collection: str
    
    # Telegram Configuration
    telegram_bot_token: Optional[str]
    telegram_webhook_url: Optional[str]
    
    # Instagram Configuration
    instagram_verify_token: Optional[str]
    instagram_access_token: Optional[str]
    instagram_webhook_url: Optional[str]
    
    # Security Settings
    max_message_length: int
    security_enabled: bool
    
    # Performance Settings
    cache_ttl_seconds: int
    max_concurrent_requests: int
    request_timeout_seconds: int
    
    # Monitoring Settings
    health_check_enabled: bool
    metrics_enabled: bool
    performance_monitoring: bool
    
    # Business Information
    business_name: str
    business_phone: str
    business_email: str
    business_website: str
    business_location: str


def get_env_var(key: str, default: Optional[Union[str, int, bool]] = None, 
                required: bool = False, var_type: type = str) -> Any:
    """
    Get environment variable with type conversion and validation
    
    Args:
        key: Environment variable key
        default: Default value if not found
        required: Whether the variable is required
        var_type: Type to convert to (str, int, bool)
    
    Returns:
        Environment variable value with proper type
    
    Raises:
        ValueError: If required variable is missing or type conversion fails
    """
    value = os.getenv(key)
    
    if value is None:
        if required:
            raise ValueError(f"Required environment variable '{key}' is not set")
        return default
    
    # Type conversion
    try:
        if var_type == bool:
            return value.lower() in ('true', '1', 'yes', 'on')
        elif var_type == int:
            return int(value)
        elif var_type == str:
            return value
        else:
            return var_type(value)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Failed to convert environment variable '{key}' to {var_type.__name__}: {e}")


def load_environment_config() -> EnvironmentConfig:
    """
    Load and validate all environment configuration
    
    Returns:
        EnvironmentConfig with all settings
    
    Raises:
        ValueError: If required configuration is missing or invalid
    """
    try:
        config = EnvironmentConfig(
            # Application Settings
            environment=get_env_var('ENVIRONMENT', 'development'),
            log_level=get_env_var('LOG_LEVEL', 'INFO'),
            debug=get_env_var('DEBUG', False, var_type=bool),
            
            # API Keys (optional, will use fallbacks if not provided)
            openai_api_key=get_env_var('OPENAI_API_KEY'),
            gemini_api_key=get_env_var('GEMINI_API_KEY'),
            
            # Redis Configuration
            redis_host=get_env_var('REDIS_HOST', 'localhost'),
            redis_port=get_env_var('REDIS_PORT', 6379, var_type=int),
            redis_db=get_env_var('REDIS_DB', 0, var_type=int),
            redis_password=get_env_var('REDIS_PASSWORD'),
            
            # ChromaDB Configuration
            chromadb_path=get_env_var('CHROMADB_PATH', './chroma_db_flowers'),
            chromadb_collection=get_env_var('CHROMADB_COLLECTION', 'xoflowers_products'),
            
            # Telegram Configuration
            telegram_bot_token=get_env_var('TELEGRAM_BOT_TOKEN'),
            telegram_webhook_url=get_env_var('TELEGRAM_WEBHOOK_URL'),
            
            # Instagram Configuration
            instagram_verify_token=get_env_var('INSTAGRAM_VERIFY_TOKEN'),
            instagram_access_token=get_env_var('INSTAGRAM_ACCESS_TOKEN'),
            instagram_webhook_url=get_env_var('INSTAGRAM_WEBHOOK_URL'),
            
            # Security Settings
            max_message_length=get_env_var('MAX_MESSAGE_LENGTH', 1000, var_type=int),
            security_enabled=get_env_var('SECURITY_ENABLED', True, var_type=bool),
            
            # Performance Settings
            cache_ttl_seconds=get_env_var('CACHE_TTL_SECONDS', 300, var_type=int),
            max_concurrent_requests=get_env_var('MAX_CONCURRENT_REQUESTS', 10, var_type=int),
            request_timeout_seconds=get_env_var('REQUEST_TIMEOUT_SECONDS', 30, var_type=int),
            
            # Monitoring Settings
            health_check_enabled=get_env_var('HEALTH_CHECK_ENABLED', True, var_type=bool),
            metrics_enabled=get_env_var('METRICS_ENABLED', True, var_type=bool),
            performance_monitoring=get_env_var('PERFORMANCE_MONITORING', True, var_type=bool),
            
            # Business Information
            business_name=get_env_var('BUSINESS_NAME', 'XOFlowers'),
            business_phone=get_env_var('BUSINESS_PHONE', '+373 XX XXX XXX'),
            business_email=get_env_var('BUSINESS_EMAIL', 'contact@xoflowers.md'),
            business_website=get_env_var('BUSINESS_WEBSITE', 'https://xoflowers.md'),
            business_location=get_env_var('BUSINESS_LOCATION', 'Chișinău, Moldova')
        )
        
        # Validate configuration
        _validate_config(config)
        
        return config
        
    except Exception as e:
        raise ValueError(f"Failed to load environment configuration: {e}")


def _validate_config(config: EnvironmentConfig) -> None:
    """
    Validate environment configuration
    
    Args:
        config: Configuration to validate
    
    Raises:
        ValueError: If configuration is invalid
    """
    # Validate environment
    valid_environments = ['development', 'staging', 'production']
    if config.environment not in valid_environments:
        raise ValueError(f"Invalid environment '{config.environment}'. Must be one of: {valid_environments}")
    
    # Validate log level
    valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if config.log_level.upper() not in valid_log_levels:
        raise ValueError(f"Invalid log level '{config.log_level}'. Must be one of: {valid_log_levels}")
    
    # Validate Redis port
    if not (1 <= config.redis_port <= 65535):
        raise ValueError(f"Invalid Redis port '{config.redis_port}'. Must be between 1 and 65535")
    
    # Validate performance settings
    if config.cache_ttl_seconds < 0:
        raise ValueError("Cache TTL must be non-negative")
    
    if config.max_concurrent_requests < 1:
        raise ValueError("Max concurrent requests must be at least 1")
    
    if config.request_timeout_seconds < 1:
        raise ValueError("Request timeout must be at least 1 second")
    
    if config.max_message_length < 1:
        raise ValueError("Max message length must be at least 1")
    
    # Warn about missing API keys in production
    if config.environment == 'production':
        if not config.openai_api_key and not config.gemini_api_key:
            print("WARNING: No AI API keys configured in production environment")
        
        if not config.telegram_bot_token and not config.instagram_access_token:
            print("WARNING: No platform tokens configured in production environment")


def get_config_summary() -> Dict[str, Any]:
    """
    Get configuration summary for logging/debugging
    
    Returns:
        Dictionary with non-sensitive configuration values
    """
    config = load_environment_config()
    
    return {
        'environment': config.environment,
        'log_level': config.log_level,
        'debug': config.debug,
        'redis_host': config.redis_host,
        'redis_port': config.redis_port,
        'chromadb_path': config.chromadb_path,
        'security_enabled': config.security_enabled,
        'health_check_enabled': config.health_check_enabled,
        'metrics_enabled': config.metrics_enabled,
        'performance_monitoring': config.performance_monitoring,
        'business_name': config.business_name,
        'has_openai_key': bool(config.openai_api_key),
        'has_gemini_key': bool(config.gemini_api_key),
        'has_telegram_token': bool(config.telegram_bot_token),
        'has_instagram_token': bool(config.instagram_access_token)
    }


# Global configuration instance
_config = None

def get_environment_config() -> EnvironmentConfig:
    """
    Get global environment configuration instance
    
    Returns:
        EnvironmentConfig instance
    """
    global _config
    if _config is None:
        _config = load_environment_config()
    return _config


def reload_config() -> EnvironmentConfig:
    """
    Reload configuration from environment variables
    
    Returns:
        New EnvironmentConfig instance
    """
    global _config
    _config = load_environment_config()
    return _config


# Convenience functions for common configuration access
def is_production() -> bool:
    """Check if running in production environment"""
    return get_environment_config().environment == 'production'

def is_development() -> bool:
    """Check if running in development environment"""
    return get_environment_config().environment == 'development'

def get_log_level() -> str:
    """Get configured log level"""
    return get_environment_config().log_level

def is_debug_enabled() -> bool:
    """Check if debug mode is enabled"""
    return get_environment_config().debug


# Container deployment helpers
def get_container_config() -> Dict[str, Any]:
    """Get configuration optimized for container deployment"""
    config = get_environment_config()
    
    return {
        'app': {
            'host': '0.0.0.0',  # Bind to all interfaces in container
            'port': 8000,
            'workers': 1,  # Single worker for simplicity
            'log_level': config.log_level.lower(),
            'access_log': True,
            'reload': False  # Never reload in container
        },
        'redis': {
            'host': config.redis_host,
            'port': config.redis_port,
            'db': config.redis_db,
            'password': config.redis_password,
            'socket_timeout': 5,
            'socket_connect_timeout': 5,
            'retry_on_timeout': True,
            'health_check_interval': 30
        },
        'chromadb': {
            'path': config.chromadb_path,
            'collection': config.chromadb_collection,
            'persist_directory': config.chromadb_path
        },
        'monitoring': {
            'health_check_enabled': config.health_check_enabled,
            'metrics_enabled': config.metrics_enabled,
            'performance_monitoring': config.performance_monitoring
        }
    }


def validate_deployment_config() -> Dict[str, Any]:
    """Validate configuration for deployment and return status"""
    config = get_environment_config()
    issues = []
    warnings = []
    
    # Check required API keys for production
    if config.environment == 'production':
        if not config.openai_api_key and not config.gemini_api_key:
            issues.append("No AI API keys configured - at least one is required")
        
        if not config.telegram_bot_token and not config.instagram_access_token:
            warnings.append("No platform tokens configured - limited functionality")
    
    # Check Redis configuration
    try:
        import redis
        r = redis.Redis(
            host=config.redis_host,
            port=config.redis_port,
            db=config.redis_db,
            password=config.redis_password,
            socket_timeout=5,
            socket_connect_timeout=5
        )
        r.ping()
    except Exception as e:
        warnings.append(f"Redis connection failed: {e}")
    
    # Check ChromaDB path
    from pathlib import Path
    chromadb_path = Path(config.chromadb_path)
    if not chromadb_path.exists():
        warnings.append(f"ChromaDB path does not exist: {config.chromadb_path}")
    
    # Check performance settings
    if config.request_timeout_seconds < 10:
        warnings.append("Request timeout is very low - may cause issues")
    
    if config.max_concurrent_requests > 50:
        warnings.append("Max concurrent requests is very high - may cause resource issues")
    
    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'warnings': warnings,
        'config_summary': get_config_summary()
    }


def get_deployment_environment_vars() -> Dict[str, str]:
    """Get environment variables formatted for container deployment"""
    config = get_environment_config()
    
    env_vars = {
        # Application
        'ENVIRONMENT': config.environment,
        'LOG_LEVEL': config.log_level,
        'DEBUG': str(config.debug).lower(),
        
        # Redis
        'REDIS_HOST': config.redis_host,
        'REDIS_PORT': str(config.redis_port),
        'REDIS_DB': str(config.redis_db),
        
        # ChromaDB
        'CHROMADB_PATH': config.chromadb_path,
        'CHROMADB_COLLECTION': config.chromadb_collection,
        
        # Security
        'MAX_MESSAGE_LENGTH': str(config.max_message_length),
        'SECURITY_ENABLED': str(config.security_enabled).lower(),
        
        # Performance
        'CACHE_TTL_SECONDS': str(config.cache_ttl_seconds),
        'MAX_CONCURRENT_REQUESTS': str(config.max_concurrent_requests),
        'REQUEST_TIMEOUT_SECONDS': str(config.request_timeout_seconds),
        
        # Monitoring
        'HEALTH_CHECK_ENABLED': str(config.health_check_enabled).lower(),
        'METRICS_ENABLED': str(config.metrics_enabled).lower(),
        'PERFORMANCE_MONITORING': str(config.performance_monitoring).lower(),
        
        # Business
        'BUSINESS_NAME': config.business_name,
        'BUSINESS_PHONE': config.business_phone,
        'BUSINESS_EMAIL': config.business_email,
        'BUSINESS_WEBSITE': config.business_website,
        'BUSINESS_LOCATION': config.business_location,
        
        # Container specific
        'PYTHONUNBUFFERED': '1',
        'PYTHONDONTWRITEBYTECODE': '1'
    }
    
    # Add optional values only if they exist
    if config.redis_password:
        env_vars['REDIS_PASSWORD'] = config.redis_password
    
    if config.openai_api_key:
        env_vars['OPENAI_API_KEY'] = config.openai_api_key
    
    if config.gemini_api_key:
        env_vars['GEMINI_API_KEY'] = config.gemini_api_key
    
    if config.telegram_bot_token:
        env_vars['TELEGRAM_BOT_TOKEN'] = config.telegram_bot_token
    
    if config.telegram_webhook_url:
        env_vars['TELEGRAM_WEBHOOK_URL'] = config.telegram_webhook_url
    
    if config.instagram_verify_token:
        env_vars['INSTAGRAM_VERIFY_TOKEN'] = config.instagram_verify_token
    
    if config.instagram_access_token:
        env_vars['INSTAGRAM_ACCESS_TOKEN'] = config.instagram_access_token
    
    if config.instagram_webhook_url:
        env_vars['INSTAGRAM_WEBHOOK_URL'] = config.instagram_webhook_url
    
    return env_vars