# Arquitetura do Backend e Banco de Dados

## 1. Visão Geral
Para atender à solicitação de persistência de dados para as "Situações de Manutenção", o site estático será transformado em uma aplicação web dinâmica utilizando Flask para o backend e SQLite como banco de dados inicial.

## 2. Modelo de Dados (SQLAlchemy)
Será criada uma tabela `situacao_manutencao` com os seguintes campos:
- `id`: Integer, Chave Primária, Autoincremento
- `nome_tarefa`: String(300), Não Nulo
- `status`: String(50), Não Nulo, Valor Padrão 'pendente' (valores possíveis: 'pendente', 'em_analise', 'aguardando_confirmacao', 'cancelado', 'concluido')
- `observacoes`: Text, Nulo
- `imagem_path`: String(300), Nulo (caminho para a imagem no servidor)
- `data_criacao`: DateTime, Padrão: data e hora atuais
- `data_atualizacao`: DateTime, Padrão: data e hora atuais, Atualizado em cada modificação

## 3. API Endpoints (Rotas Flask)
Serão criados os seguintes endpoints para gerenciar as situações de manutenção:
- `POST /api/situacoes`: Cria uma nova situação de manutenção. Recebe dados em JSON e o arquivo de imagem (multipart/form-data).
- `GET /api/situacoes`: Retorna uma lista de todas as situações de manutenção em JSON.
- `PUT /api/situacoes/<int:id>`: Atualiza uma situação de manutenção existente (ex: status, observações). Recebe dados em JSON.
- `DELETE /api/situacoes/<int:id>`: Remove uma situação de manutenção.

## 4. Tecnologias
- **Backend:** Flask
- **Banco de Dados:** SQLite (inicialmente, com possibilidade de migração futura)
- **ORM:** SQLAlchemy
- **Servidor WSGI:** Gunicorn (para implantação)

## 5. Estrutura de Arquivos (já iniciada)
```
/home/ubuntu/uai_manutencao_flask/
├── src/
│   ├── __init__.py       # Configuração da aplicação Flask
│   ├── main.py           # Ponto de entrada da aplicação, rotas principais (HTML)
│   ├── models/
│   │   ├── __init__.py
│   │   └── situacao.py   # Modelo SQLAlchemy para SituacaoManutencao
│   ├── routes/
│   │   ├── __init__.py
│   │   └── api_situacoes.py # Rotas da API para situações
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   └── templates/
│       └── desnatadeira_inversor_atv630.html # Template principal
├── uploads/                # Diretório para armazenar imagens enviadas
├── requirements.txt        # Dependências Python
└── venv/                   # Ambiente virtual (a ser criado)
```

## 6. Próximos Passos Imediatos (Plano)
1.  Criar o ambiente virtual e instalar dependências (Flask, SQLAlchemy, Flask-SQLAlchemy).
2.  Definir o modelo `SituacaoManutencao` em `src/models/situacao.py`.
3.  Configurar a aplicação Flask e o banco de dados em `src/__init__.py`.

