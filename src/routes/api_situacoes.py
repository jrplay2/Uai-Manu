import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from src import db # Assuming db is initialized in src/__init__.py and imported here
from src.models.situacao import SituacaoManutencao # Assuming model is in src/models/situacao.py

situacoes_bp = Blueprint('situacoes_bp', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@situacoes_bp.route('/situacoes', methods=['POST'])
def create_situacao():
    if 'nome_tarefa' not in request.form:
        current_app.logger.warn("Create situacao failed: Missing nome_tarefa")
        return jsonify({'error': 'Missing nome_tarefa in form data'}), 400

    nome_tarefa = request.form['nome_tarefa']
    status = request.form.get('status', 'pendente')
    observacoes = request.form.get('observacoes')
    
    imagem_path_to_store_in_db = None 
    
    if 'imagem' in request.files:
        file = request.files['imagem']
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            
            # app.config['UPLOAD_FOLDER'] is absolute path to instance_path/uploads
            absolute_upload_folder = current_app.config['UPLOAD_FOLDER'] 
            
            if not os.path.exists(absolute_upload_folder):
                try:
                    os.makedirs(absolute_upload_folder)
                    current_app.logger.info(f"Created upload folder: {absolute_upload_folder}")
                except OSError as e:
                    current_app.logger.error(f"Could not create upload folder {absolute_upload_folder}: {e}")
                    return jsonify({'error': f'Server error: Could not create upload directory'}), 500
            
            absolute_image_save_path = os.path.join(absolute_upload_folder, filename)
            
            try:
                file.save(absolute_image_save_path)
                current_app.logger.info(f"Saved image to: {absolute_image_save_path}")
                # Path stored in DB is relative to the 'instance' folder, e.g., 'uploads/filename.jpg'
                imagem_path_to_store_in_db = os.path.join('uploads', filename) 
            except Exception as e:
                current_app.logger.error(f"Could not save image {filename} to {absolute_image_save_path}: {e}")
                return jsonify({'error': f'Server error: Could not save image'}), 500
        elif file and file.filename: # File is present but type not allowed
             current_app.logger.warn(f"Create situacao failed: Invalid image file type for {file.filename}")
             return jsonify({'error': 'Invalid image file type'}), 400

    try:
        nova_situacao = SituacaoManutencao(
            nome_tarefa=nome_tarefa,
            status=status,
            observacoes=observacoes,
            imagem_path=imagem_path_to_store_in_db
        )
        db.session.add(nova_situacao)
        db.session.commit()
        current_app.logger.info(f"Created new situacao: ID {nova_situacao.id}, Tarefa: {nova_situacao.nome_tarefa}")
        return jsonify(nova_situacao.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Database error on create_situacao: {e}")
        return jsonify({'error': f'Database error occurred'}), 500

@situacoes_bp.route('/situacoes', methods=['GET'])
def get_situacoes():
    try:
        situacoes = SituacaoManutencao.query.order_by(SituacaoManutencao.data_criacao.desc()).all()
        return jsonify([s.to_dict() for s in situacoes]), 200
    except Exception as e:
        current_app.logger.error(f"Database error on get_situacoes: {e}")
        return jsonify({'error': f'Database error occurred'}), 500

@situacoes_bp.route('/situacoes/<int:id>', methods=['GET'])
def get_situacao(id):
    try:
        situacao = SituacaoManutencao.query.get(id)
        if situacao is None:
            current_app.logger.warn(f"Get situacao failed: ID {id} not found")
            return jsonify({'error': 'Situacao not found'}), 404
        return jsonify(situacao.to_dict()), 200
    except Exception as e:
        current_app.logger.error(f"Database error on get_situacao ID {id}: {e}")
        return jsonify({'error': f'Database error occurred'}), 500

@situacoes_bp.route('/situacoes/<int:id>', methods=['PUT'])
def update_situacao(id):
    try:
        situacao = SituacaoManutencao.query.get(id)
        if situacao is None:
            current_app.logger.warn(f"Update situacao failed: ID {id} not found")
            return jsonify({'error': 'Situacao not found'}), 404

        data = request.json
        if not data:
            current_app.logger.warn(f"Update situacao failed for ID {id}: Missing JSON data")
            return jsonify({'error': 'Missing JSON data'}), 400

        situacao.nome_tarefa = data.get('nome_tarefa', situacao.nome_tarefa)
        situacao.status = data.get('status', situacao.status)
        situacao.observacoes = data.get('observacoes', situacao.observacoes)
        # Note: Image update is not handled in this PUT request.
        # This would typically involve a separate endpoint or using multipart/form-data for PUT.

        db.session.commit()
        current_app.logger.info(f"Updated situacao: ID {id}")
        return jsonify(situacao.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Database error or invalid data on update_situacao ID {id}: {e}")
        return jsonify({'error': f'Database error or invalid data'}), 500

@situacoes_bp.route('/situacoes/<int:id>', methods=['DELETE'])
def delete_situacao(id):
    try:
        situacao = SituacaoManutencao.query.get(id)
        if situacao is None:
            current_app.logger.warn(f"Delete situacao failed: ID {id} not found")
            return jsonify({'error': 'Situacao not found'}), 404

        if situacao.imagem_path:
            # situacao.imagem_path is 'uploads/filename.jpg'
            # current_app.instance_path is the absolute path to the 'instance' folder
            image_full_path = os.path.join(current_app.instance_path, situacao.imagem_path)
            try:
                if os.path.exists(image_full_path):
                    os.remove(image_full_path)
                    current_app.logger.info(f"Deleted image file: {image_full_path} for situacao ID {id}")
            except Exception as e:
                current_app.logger.error(f"Error deleting image file {image_full_path} for situacao ID {id}: {e}")
                # Log error but continue with DB record deletion

        db.session.delete(situacao)
        db.session.commit()
        current_app.logger.info(f"Deleted situacao: ID {id}")
        return jsonify({'message': 'Situacao deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Database error on delete_situacao ID {id}: {e}")
        return jsonify({'error': f'Database error occurred'}), 500
