from flask import Blueprint, request, jsonify, current_app
from ..models.item_faltante import db, ItemFaltante
import os

bp = Blueprint("api_itens_faltantes", __name__, url_prefix="/api/itens-faltantes")

# Rota para listar todos os itens faltantes de uma máquina específica
@bp.route("/<string:maquina>", methods=["GET"])
def get_itens_faltantes(maquina):
    itens = ItemFaltante.query.filter_by(maquina=maquina).order_by(ItemFaltante.categoria, ItemFaltante.id).all()
    return jsonify([item.to_dict() for item in itens]), 200

# Rota para atualizar o status de um item faltante (adquirido/não adquirido)
@bp.route("/<int:id>", methods=["PUT"])
def update_item_faltante(id):
    item = ItemFaltante.query.get_or_404(id)
    data = request.json
    
    if "adquirido" in data:
        item.adquirido = data["adquirido"]
    
    db.session.commit()
    return jsonify(item.to_dict()), 200

# Rota para inicializar os itens faltantes da WSE250 (apenas se não existirem)
@bp.route("/inicializar-wse250", methods=["POST"])
def inicializar_itens_wse250():
    # Verifica se já existem itens para a WSE250
    itens_existentes = ItemFaltante.query.filter_by(maquina="wse250").first()
    if itens_existentes:
        return jsonify({"message": "Itens da WSE250 já foram inicializados"}), 200
    
    # Lista de itens faltantes da WSE250 conforme o PDF
    itens_wse250 = [
        # GÁS
        {"categoria": "GÁS", "descricao": "Válvula reguladora com manômetro duplo para argônio", "maquina": "wse250"},
        {"categoria": "GÁS", "descricao": "Fluxômetro com bico de 6 mm (pode vir junto com o regulador)", "maquina": "wse250"},
        {"categoria": "GÁS", "descricao": "Mangueira de gás (PVC/PU) com engate ou braçadeiras", "maquina": "wse250"},
        {"categoria": "GÁS", "descricao": "Adaptador 1/4\" NPT (se necessário)", "maquina": "wse250"},
        
        # TOCHA TIG
        {"categoria": "TOCHA TIG", "descricao": "Tocha TIG tipo SR-26 ou WP-26 (com conector e acionamento)", "maquina": "wse250"},
        {"categoria": "TOCHA TIG", "descricao": "Tungstênios: vermelho (aço), verde/roxo (alumínio)", "maquina": "wse250"},
        {"categoria": "TOCHA TIG", "descricao": "Bicos cerâmicos: tamanhos #5, #6, #7", "maquina": "wse250"},
        {"categoria": "TOCHA TIG", "descricao": "Collets e porta-collets: 1,6 mm, 2,4 mm, 3,2 mm", "maquina": "wse250"},
        {"categoria": "TOCHA TIG", "descricao": "Tampa traseira da tocha", "maquina": "wse250"},
        
        # MMA (ELETRODO)
        {"categoria": "MMA (ELETRODO)", "descricao": "Porta eletrodo com cabo (mínimo 10 mm², 3 m)", "maquina": "wse250"},
        {"categoria": "MMA (ELETRODO)", "descricao": "Garra negativa/terra com cabo (mínimo 10 mm², 3 m)", "maquina": "wse250"},
        {"categoria": "MMA (ELETRODO)", "descricao": "Eletrodos (E6013, E7018, etc.)", "maquina": "wse250"},
        
        # EPIs
        {"categoria": "EPIs", "descricao": "Máscara de solda automática (escurecimento DIN 9-13)", "maquina": "wse250"},
        {"categoria": "EPIs", "descricao": "Luvas de raspa", "maquina": "wse250"},
        {"categoria": "EPIs", "descricao": "Avental de raspa", "maquina": "wse250"}
    ]
    
    # Adiciona os itens ao banco de dados
    for item_data in itens_wse250:
        item = ItemFaltante(
            categoria=item_data["categoria"],
            descricao=item_data["descricao"],
            adquirido=False,
            maquina=item_data["maquina"]
        )
        db.session.add(item)
    
    db.session.commit()
    return jsonify({"message": "Itens da WSE250 inicializados com sucesso"}), 201
