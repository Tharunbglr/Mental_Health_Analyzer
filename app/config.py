import os


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production")
    ENV = os.getenv("FLASK_ENV", "production")
    DEBUG = ENV == "development"
    TESTING = False

    # Rate limiting
    RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "20 per minute")
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_RETENTION = int(os.getenv("LOG_RETENTION_DAYS", "7"))


class DevelopmentConfig(BaseConfig):
    ENV = "development"
    DEBUG = True


class ProductionConfig(BaseConfig):
    ENV = "production"
    DEBUG = False
    
    # Enhanced security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes
    
    # Rate limiting - use memory storage by default for Railway
    RATELIMIT_DEFAULT = "100/day"
    RATELIMIT_STORAGE_URI = os.getenv("REDIS_URL", "memory://")
    
    # AI rate limits
    AI_RATELIMIT = "50/day"
    AI_TIMEOUT = 10
    AI_MAX_RETRIES = 2
    
    # Health check
    HEALTH_CHECK_ENABLED = True
    HEALTH_CHECK_REDIS = False  # Disable Redis health check by default


def get_config_class():
    env = os.getenv("FLASK_ENV", "production").lower()
    if env.startswith("dev"):
        return DevelopmentConfig
    return ProductionConfig
