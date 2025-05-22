from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# Este db será inicializado na factory da aplicação em src/__init__.py
# Para evitar importação circular, apenas declaramos aqui.
db = SQLAlchemy()

class SituacaoManutencao(db.Model):
    __tablename__ = 'situacao_manutencao'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome_tarefa = db.Column(db.String(300), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pendente')
    observacoes = db.Column(db.Text, nullable=True)
    imagem_path = db.Column(db.String(300), nullable=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'nome_tarefa': self.nome_tarefa,
            'status': self.status,
            'observacoes': self.observacoes,
            'imagem_path': self.imagem_path if self.imagem_path else None, # Retorna None se não houver imagem
            'data_criacao': self.data_criacao.isoformat(),
            'data_atualizacao': self.data_atualizacao.isoformat()
        }

    def __repr__(self):
        return f'<SituacaoManutencao {self.id}: {self.nome_tarefa}>'

