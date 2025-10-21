import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect

from .config import get_config_class


def create_app() -> Flask:
    app = Flask(__name__)
    
    # Load configuration
    load_dotenv()  # .env in project root
    try:
        load_dotenv(os.path.join(app.instance_path, ".env"))
    except Exception:
        pass
    
    # Apply configuration
    app.config.from_object(get_config_class())
    
    # Railway specific configuration
    if os.getenv("RAILWAY_ENVIRONMENT"):
        app.config["PREFERRED_URL_SCHEME"] = "https"
        app.config["SERVER_NAME"] = None
        # Ensure we have a secret key
        if not app.config["SECRET_KEY"] or app.config["SECRET_KEY"] == "change-this-in-production":
            app.config["SECRET_KEY"] = os.urandom(32).hex()

    # Ensure instance and data dirs exist
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    from .routes import bp as main_bp

    app.register_blueprint(main_bp)

    # Register error handlers and health
    from .health import health_bp, register_error_handlers

    app.register_blueprint(health_bp)
    register_error_handlers(app)

    _configure_security(app)
    _configure_rate_limiting(app)
    _configure_csrf(app)
    _configure_logging(app)

    return app


def _configure_logging(app: Flask) -> None:
    log_dir = os.path.join(app.instance_path, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "app.log")

    handler = RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=10)
    handler.setLevel(getattr(logging, app.config.get("LOG_LEVEL", "INFO")))
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(remote_addr)s %(method)s %(path)s - %(message)s"
    )
    handler.setFormatter(formatter)

    # Add request context fields via middleware
    @app.before_request
    def _inject_request_logging_fields():
        from flask import g, request

        g.log_fields = {
            "remote_addr": request.remote_addr,
            "method": request.method,
            "path": request.path,
        }

    class RequestContextFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            try:
                from flask import g

                for k, v in getattr(g, "log_fields", {}).items():
                    setattr(record, k, v)
            except Exception:
                record.remote_addr = "-"
                record.method = "-"
                record.path = "-"
            return True

    handler.addFilter(RequestContextFilter())
    app.logger.addHandler(handler)
    app.logger.setLevel(getattr(logging, app.config.get("LOG_LEVEL", "INFO")))


def _configure_security(app: Flask) -> None:
    # Disable Talisman on Railway to prevent redirect issues
    if app.config.get("ENV") == "production" and "railway" in os.getenv("RAILWAY_ENVIRONMENT", ""):
        return

    csp = {
        "default-src": ["'self'"],
        "script-src": ["'self'"],
        "style-src": ["'self'", "'unsafe-inline'"],
        "img-src": ["'self'", "data:"],
        "connect-src": ["'self'"],
        "object-src": ["'none'"],
        "base-uri": ["'self'"],
        "frame-ancestors": ["'none'"],
    }
    Talisman(app, content_security_policy=csp, strict_transport_security=True)


def _configure_rate_limiting(app: Flask) -> Limiter:
    limiter = Limiter(get_remote_address, storage_uri=app.config["RATELIMIT_STORAGE_URI"])
    limiter.init_app(app)
    return limiter


def _configure_csrf(app: Flask) -> CSRFProtect:
    csrf = CSRFProtect()
    csrf.init_app(app)
    return csrf
