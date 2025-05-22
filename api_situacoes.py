from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from ..models.situacao import db, SituacaoManutencao
import uuid # Para nomes de arquivo únicos

bp = Blueprint("api_situacoes", __name__, url_prefix="/api/situacoes")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route("/", methods=["POST"])
def create_situacao():
    if "nome_tarefa" not in request.form or not request.form["nome_tarefa"]:
        return jsonify({"error": "O campo nome_tarefa é obrigatório"}), 400
    
    nome_tarefa = request.form["nome_tarefa"]
    status = request.form.get("status", "pendente")
    observacoes = request.form.get("observacoes", "")
    imagem_path_relativo = None

    if "imagem" in request.files:
        file = request.files["imagem"]
        if file and file.filename != "" and allowed_file(file.filename):
            filename_seguro = secure_filename(file.filename)
            # Criar um nome de arquivo único para evitar sobrescrever
            extensao = filename_seguro.rsplit(".", 1)[1].lower()
            nome_arquivo_unico = f"{uuid.uuid4()}.{extensao}"
            
            upload_folder = current_app.config["UPLOAD_FOLDER"]
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            caminho_completo_imagem = os.path.join(upload_folder, nome_arquivo_unico)
            file.save(caminho_completo_imagem)
            # Salvar apenas o nome do arquivo ou caminho relativo para o banco
            imagem_path_relativo = nome_arquivo_unico 
        elif file and file.filename != "":
            return jsonify({"error": "Tipo de arquivo de imagem não permitido."}), 400

    nova_situacao = SituacaoManutencao(
        nome_tarefa=nome_tarefa,
        status=status,
        observacoes=observacoes,
        imagem_path=imagem_path_relativo
    )
    db.session.add(nova_situacao)
    db.session.commit()
    return jsonify(nova_situacao.to_dict()), 201

@bp.route("/", methods=["GET"])
def get_situacoes():
    situacoes = SituacaoManutencao.query.order_by(SituacaoManutencao.data_criacao.desc()).all()
    return jsonify([s.to_dict() for s in situacoes]), 200

@bp.route("/<int:id>", methods=["PUT"])
def update_situacao(id):
    situacao = SituacaoManutencao.query.get_or_404(id)
    data = request.form

    if "nome_tarefa" in data:
        situacao.nome_tarefa = data["nome_tarefa"]
    if "status" in data:
        situacao.status = data["status"]
    if "observacoes" in data:
        situacao.observacoes = data["observacoes"]

    # Lógica para atualizar/remover imagem se necessário (pode ser mais complexa)
    # Por simplicidade, este exemplo não lida com a substituição de imagem no PUT.
    # Se uma nova imagem for enviada, ela pode substituir a antiga ou adicionar uma nova.
    # Se um campo especial indicar remoção de imagem, o imagem_path pode ser setado para None.

    db.session.commit()
    return jsonify(situacao.to_dict()), 200

@bp.route("/<int:id>", methods=["DELETE"])
def delete_situacao(id):
    situacao = SituacaoManutencao.query.get_or_404(id)
    
    # Opcional: remover o arquivo de imagem do sistema de arquivos
    if situacao.imagem_path:
        try:
            caminho_imagem_abs = os.path.join(current_app.config["UPLOAD_FOLDER"], situacao.imagem_path)
            if os.path.exists(caminho_imagem_abs):
                os.remove(caminho_imagem_abs)
        except Exception as e:
            current_app.logger.error(f"Erro ao remover arquivo de imagem {situacao.imagem_path}: {e}")
    
    db.session.delete(situacao)
    db.session.commit()
    return jsonify({"message": "Situação removida com sucesso"}), 200
