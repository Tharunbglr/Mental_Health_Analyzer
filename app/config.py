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


def get_config_class():
    env = os.getenv("FLASK_ENV", "production").lower()
    if env.startswith("dev"):
        return DevelopmentConfig
    return ProductionConfig
