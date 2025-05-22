from flask import Blueprint, request, jsonify, current_app, url_for, render_template
import os
from werkzeug.utils import secure_filename
from .gdrive_storage import GoogleDriveStorage

# Crie um Blueprint para as rotas relacionadas ao Google Drive
bp = Blueprint('gdrive', __name__, url_prefix='/gdrive')

# Configuração do Google Drive
# Você precisará criar um arquivo de credenciais do Google Cloud
CREDENTIALS_PATH = 'credentials.json'  # Caminho para o arquivo de credenciais
IMAGES_FOLDER_ID = 'SEU_FOLDER_ID_AQUI'  # ID da pasta no Google Drive para imagens
DATA_FOLDER_ID = 'SEU_FOLDER_ID_AQUI'  # ID da pasta no Google Drive para dados

# Inicializa o armazenamento do Google Drive
def get_drive_storage():
    return GoogleDriveStorage(CREDENTIALS_PATH)

# Rota para fazer upload de imagens
@bp.route('/upload_image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'Nome de arquivo vazio'}), 400
        
    if file:
        # Salva o arquivo temporariamente
        filename = secure_filename(file.filename)
        temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_path)
        
        try:
            # Faz upload para o Google Drive
            drive = get_drive_storage()
            file_id = drive.upload_file(temp_path, IMAGES_FOLDER_ID)
            file_url = drive.get_file_url(file_id)
            
            # Remove o arquivo temporário
            os.remove(temp_path)
            
            return jsonify({
                'success': True,
                'file_id': file_id,
                'file_url': file_url
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# Rota para salvar dados de uma máquina
@bp.route('/save_machine_data', methods=['POST'])
def save_machine_data():
    data = request.json
    
    if not data:
        return jsonify({'error': 'Dados vazios'}), 400
        
    try:
        machine_name = data.get('nome', 'maquina')
        
        # Salva os dados no Google Drive
        drive = get_drive_storage()
        file_id = drive.save_data(data, f"{machine_name}_data.json", DATA_FOLDER_ID)
        
        return jsonify({
            'success': True,
            'file_id': file_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rota para carregar dados de uma máquina
@bp.route('/load_machine_data/<file_id>', methods=['GET'])
def load_machine_data(file_id):
    try:
        # Carrega os dados do Google Drive
        drive = get_drive_storage()
        data = drive.load_data(file_id)
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Página de exemplo para gerenciar arquivos no Google Drive
@bp.route('/manager', methods=['GET'])
def manager():
    return render_template('gdrive_manager.html')
