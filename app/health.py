from flask import Blueprint, jsonify, render_template
from flask import current_app as app


health_bp = Blueprint("health", __name__)


@health_bp.get("/healthz")
def healthz():
    return jsonify({"status": "ok"}), 200


def register_error_handlers(flask_app):
    @flask_app.errorhandler(404)
    def not_found(_):
        return render_template("404.html"), 404

    @flask_app.errorhandler(500)
    def server_error(_):
        app.logger.exception("Unhandled exception")
        return render_template("500.html"), 500


