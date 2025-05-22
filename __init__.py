import os
from flask import Flask
from .models.situacao import db # Import db de models.situacao

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    # Configurações da aplicação
    app.config.from_mapping(
        SECRET_KEY='dev', # Mudar para um valor aleatório em produção
        SQLALCHEMY_DATABASE_URI='sqlite:///{}'.format(os.path.join(app.instance_path, 'uai_manutencao.sqlite')),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=os.path.join(app.root_path, '..', 'uploads') # Caminho para a pasta de uploads
    )

    if test_config is None:
        # Carrega a configuração da instância, se existir, quando não estiver testando
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Carrega a configuração de teste se passada
        app.config.from_mapping(test_config)

    # Garante que a pasta da instância exista
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Garante que a pasta de uploads exista
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'])
    except OSError:
        pass

    # Inicializa o SQLAlchemy com a app
    db.init_app(app)

    # Cria as tabelas do banco de dados se não existirem
    with app.app_context():
        db.create_all()

    # Importa e registra Blueprints
    from .routes import api_situacoes
    app.register_blueprint(api_situacoes.bp)
    
    from .routes import main_routes
    app.register_blueprint(main_routes.bp)
    
    # Registra o blueprint do Google Drive
    try:
        from . import gdrive_manager
        app.register_blueprint(gdrive_manager.bp)
    except ImportError:
        print("Módulo do Google Drive não encontrado. Funcionalidade de armazenamento em nuvem desativada.")
        pass

    return app
