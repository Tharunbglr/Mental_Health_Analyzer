import os

from app import create_app


# Use the application factory so the app serves the templates and routes
# defined in the `app` package (templates in `app/templates`).
app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
