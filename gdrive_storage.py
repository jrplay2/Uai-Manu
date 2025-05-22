from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import json

class GoogleDriveStorage:
    def __init__(self, credentials_path='jrplay-f1324cfb5a31.json'):
        """Inicializa o armazenamento do Google Drive.
        
        Args:
            credentials_path: Caminho para o arquivo JSON de credenciais
        """
        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=['https://www.googleapis.com/auth/drive']
        )
        self.service = build('drive', 'v3', credentials=self.credentials)
        
    def upload_file(self, file_path, folder_id=None):
        """Faz upload de um arquivo para o Google Drive.
        
        Args:
            file_path: Caminho local do arquivo
            folder_id: ID da pasta no Google Drive (opcional)
            
        Returns:
            ID do arquivo no Google Drive
        """
        file_metadata = {
            'name': os.path.basename(file_path),
        }
        
        if folder_id:
            file_metadata['parents'] = [folder_id]
            
        media = MediaFileUpload(file_path)
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        return file.get('id')
    
    def get_file_url(self, file_id):
        """Obtém a URL de um arquivo no Google Drive.
        
        Args:
            file_id: ID do arquivo no Google Drive
            
        Returns:
            URL do arquivo
        """
        # Configura permissão de leitura para qualquer pessoa com o link
        self.service.permissions().create(
            fileId=file_id,
            body={'type': 'anyone', 'role': 'reader'},
        ).execute()
        
        # Retorna a URL do arquivo
        return f"https://drive.google.com/uc?id={file_id}"
    
    def save_data(self, data, file_name, folder_id=None):
        """Salva dados estruturados como um arquivo JSON no Google Drive.
        
        Args:
            data: Dados a serem salvos (dict ou list)
            file_name: Nome do arquivo
            folder_id: ID da pasta no Google Drive (opcional)
            
        Returns:
            ID do arquivo no Google Drive
        """
        # Cria um arquivo temporário
        temp_path = f"temp_{file_name}.json"
        with open(temp_path, 'w') as f:
            json.dump(data, f)
        
        # Faz upload do arquivo
        file_id = self.upload_file(temp_path, folder_id)
        
        # Remove o arquivo temporário
        os.remove(temp_path)
        
        return file_id
    
    def load_data(self, file_id):
        """Carrega dados estruturados de um arquivo JSON no Google Drive.
        
        Args:
            file_id: ID do arquivo no Google Drive
            
        Returns:
            Dados carregados (dict ou list)
        """
        # Baixa o arquivo
        response = self.service.files().get_media(fileId=file_id).execute()
        
        # Carrega os dados JSON
        return json.loads(response.decode('utf-8'))

# Exemplo de uso:
# drive = GoogleDriveStorage('credentials.json')
# image_id = drive.upload_file('imagem.jpg', 'ID_DA_PASTA')
# image_url = drive.get_file_url(image_id)
# 
# dados = {'nome': 'Desnatadeira', 'status': 'Operacional'}
# data_id = drive.save_data(dados, 'status_maquina', 'ID_DA_PASTA')
