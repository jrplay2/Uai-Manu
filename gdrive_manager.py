from flask import Blueprint, request, jsonify, current_app, render_template, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
from .gdrive_storage import GoogleDriveStorage
from . import gdrive_config

# Crie um Blueprint para as rotas relacionadas ao Google Drive
bp = Blueprint('gdrive', __name__, url_prefix='/gdrive')

# Inicializa o armazenamento do Google Drive
drive_storage = GoogleDriveStorage()

# Extensões de arquivo permitidas
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf', 'doc', 'docx', 'xls', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/')
def index():
    """Página principal do gerenciador do Google Drive."""
    return render_template('gdrive/index.html')

@bp.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Rota para fazer upload de arquivos para o Google Drive."""
    if request.method == 'POST':
        # Verifica se há arquivo na requisição
        if 'file' not in request.files:
            flash('Nenhum arquivo enviado')
            return redirect(request.url)
            
        file = request.files['file']
        
        # Se o usuário não selecionou um arquivo
        if file.filename == '':
            flash('Nenhum arquivo selecionado')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            # Salva o arquivo temporariamente
            filename = secure_filename(file.filename)
            temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(temp_path)
            
            try:
                # Determina a pasta de destino com base no tipo de arquivo
                folder_id = gdrive_config.IMAGES_FOLDER_ID
                
                # Faz upload para o Google Drive
                file_id = drive_storage.upload_file(temp_path, folder_id)
                file_url = drive_storage.get_file_url(file_id)
                
                # Remove o arquivo temporário
                os.remove(temp_path)
                
                # Retorna JSON se for uma requisição AJAX, ou redireciona se for um formulário normal
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': True,
                        'file_id': file_id,
                        'file_url': file_url
                    })
                else:
                    flash(f'Arquivo enviado com sucesso! URL: {file_url}')
                    return redirect(url_for('gdrive.index'))
                    
            except Exception as e:
                # Remove o arquivo temporário em caso de erro
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'error': str(e)}), 500
                else:
                    flash(f'Erro ao enviar arquivo: {str(e)}')
                    return redirect(request.url)
        else:
            flash('Tipo de arquivo não permitido')
            return redirect(request.url)
            
    return render_template('gdrive/upload.html')

@bp.route('/save_data', methods=['POST'])
def save_data():
    """Rota para salvar dados estruturados no Google Drive."""
    data = request.json
    
    if not data:
        return jsonify({'error': 'Dados vazios'}), 400
        
    try:
        # Obtém o nome do arquivo a partir dos dados ou usa um padrão
        file_name = data.get('nome', 'dados') + '.json'
        
        # Salva os dados no Google Drive
        file_id = drive_storage.save_data(data, file_name, gdrive_config.DATA_FOLDER_ID)
        
        return jsonify({
            'success': True,
            'file_id': file_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/load_data/<file_id>')
def load_data(file_id):
    """Rota para carregar dados estruturados do Google Drive."""
    try:
        # Carrega os dados do Google Drive
        data = drive_storage.load_data(file_id)
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
