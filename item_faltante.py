from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from ..models.situacao import db

class ItemFaltante(db.Model):
    __tablename__ = 'item_faltante'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    categoria = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.String(300), nullable=False)
    adquirido = db.Column(db.Boolean, default=False)
    maquina = db.Column(db.String(50), nullable=False)  # Identificador da máquina (ex: "wse250")
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'categoria': self.categoria,
            'descricao': self.descricao,
            'adquirido': self.adquirido,
            'maquina': self.maquina,
            'data_criacao': self.data_criacao.isoformat(),
            'data_atualizacao': self.data_atualizacao.isoformat()
        }

    def __repr__(self):
        return f'<ItemFaltante {self.id}: {self.descricao}>'
