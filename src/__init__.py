import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import click
from flask.cli import with_appcontext

# Initialize SQLAlchemy instance
db = SQLAlchemy()

def create_app(config_object=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    # Load default configuration
    # Ensure this path is correct based on your project structure
    # For example, if you have a config.py in the instance folder or root
    # app.config.from_object('config.DefaultConfig')

    # Or use environment variables for configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_secret_key'), # It's important to set a proper secret key
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///uai_manutencao.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=os.path.join(app.instance_path, 'uploads') # Folder for image uploads
    )

    if config_object:
        # Load configuration from a passed object, if any
        app.config.from_object(config_object)
    else:
        # Load the instance config, if it exists, when not testing
        # For example, config.py in the instance folder
        app.config.from_pyfile('config.py', silent=True)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Ensure the upload folder exists
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'])
    except OSError:
        pass

    # Initialize extensions
    db.init_app(app)

    # Import and register blueprints
    from .routes.api_situacoes import situacoes_bp
    app.register_blueprint(situacoes_bp, url_prefix='/api')

    # You might want to add a simple route for testing
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # Create database tables if they don't exist
    # This is often handled by Flask migrations (e.g., Flask-Migrate) in larger apps,
    # but for simplicity, we can include it here or in a separate script.
    # with app.app_context():
    #     db.create_all() # Creates tables based on SQLAlchemy models
    
    # Register CLI commands
    app.cli.add_command(init_db_command)

    return app

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    db.create_all()
    click.echo('Initialized the database.')
