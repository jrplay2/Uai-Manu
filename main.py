import os
from src import create_app

app = create_app()

if __name__ == "__main__":
    # For production, Gunicorn will be used as specified in Procfile.
    # This app.run() is mainly for local development if not using 'flask run' or run.py.
    # Consider adding an environment variable to control debug mode and port,
    # or rely on run.py for local execution.
    app.run(host=os.environ.get("FLASK_RUN_HOST", "0.0.0.0"), 
            port=int(os.environ.get("FLASK_RUN_PORT", 5000)))
