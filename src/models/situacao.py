from sqlalchemy import Column, Integer, String, Text, DateTime, func
from src import db  # Import db instance from src/__init__.py

class SituacaoManutencao(db.Model):
    __tablename__ = 'situacao_manutencao'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_tarefa = Column(String(300), nullable=False)
    status = Column(String(50), nullable=False, default='pendente')
    observacoes = Column(Text, nullable=True)
    imagem_path = Column(String(300), nullable=True) # Path to the image on the server
    data_criacao = Column(DateTime, default=func.now())
    data_atualizacao = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f'<SituacaoManutencao {self.id}: {self.nome_tarefa} [{self.status}]>'

    def to_dict(self):
        """Returns a dictionary representation of the model."""
        return {
            'id': self.id,
            'nome_tarefa': self.nome_tarefa,
            'status': self.status,
            'observacoes': self.observacoes,
            'imagem_path': self.imagem_path,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None,
        }
