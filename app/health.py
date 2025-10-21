import datetime
from flask import Blueprint, current_app, jsonify, render_template
from flask import current_app as app

health_bp = Blueprint("health", __name__)


@health_bp.get("/healthz")
def healthz():
    """Enhanced health check endpoint for production monitoring"""
    health_status = {
        "status": "ok",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "components": {
            "app": {"status": "ok"},
            "redis": {"status": "unknown"},
            "ai": {"status": "unknown"}
        }
    }
    
    # Check Redis connection
    if current_app.config.get('HEALTH_CHECK_REDIS'):
        try:
            from flask_limiter import get_limiter
            limiter = get_limiter()
            limiter.storage.ping()
            health_status["components"]["redis"]["status"] = "ok"
        except Exception as e:
            health_status["components"]["redis"]["status"] = "error"
            health_status["components"]["redis"]["error"] = str(e)
            health_status["status"] = "degraded"

    # Check AI service
    if current_app.config.get('OPENAI_API_KEY'):
        try:
            from .ai import check_ai_service
            ai_status = check_ai_service()
            health_status["components"]["ai"]["status"] = "ok"
        except Exception as e:
            health_status["components"]["ai"]["status"] = "error"
            health_status["components"]["ai"]["error"] = str(e)
            health_status["status"] = "degraded"
    
    status_code = 200 if health_status["status"] == "ok" else 500
    return jsonify(health_status), status_code


def register_error_handlers(flask_app):
    @flask_app.errorhandler(404)
    def not_found(_):
        return render_template("404.html"), 404

    @flask_app.errorhandler(500)
    def server_error(_):
        app.logger.exception("Unhandled exception")
        return render_template("500.html"), 500
