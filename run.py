import os # Added to support os.environ.get
from src import create_app

app = create_app()

if __name__ == "__main__":
    # Debug mode should ideally be controlled by an environment variable (e.g., FLASK_DEBUG)
    # For simplicity here, we'll keep debug=True for run.py, assuming it's for development.
    # The host and port can also be from environment variables.
    app.run(
        host=os.environ.get("FLASK_RUN_HOST", "0.0.0.0"),
        port=int(os.environ.get("FLASK_RUN_PORT", 5000)),
        debug=True # Keep debug=True for this development-focused run script
    )
