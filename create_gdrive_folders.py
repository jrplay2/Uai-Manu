from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

# Caminho para o arquivo de credenciais
CREDENTIALS_PATH = 'jrplay-f1324cfb5a31.json'

def create_folder(service, folder_name, parent_id=None):
    """Cria uma pasta no Google Drive.
    
    Args:
        service: Serviço do Google Drive
        folder_name: Nome da pasta
        parent_id: ID da pasta pai (opcional)
        
    Returns:
        ID da pasta criada
    """
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    
    if parent_id:
        file_metadata['parents'] = [parent_id]
        
    folder = service.files().create(body=file_metadata, fields='id').execute()
    folder_id = folder.get('id')
    
    # Configura permissão para a pasta ser acessível pelo link
    service.permissions().create(
        fileId=folder_id,
        body={'type': 'anyone', 'role': 'reader'},
    ).execute()
    
    print(f"Pasta '{folder_name}' criada com ID: {folder_id}")
    print(f"Link para a pasta: https://drive.google.com/drive/folders/{folder_id}")
    
    return folder_id

def main():
    # Carrega as credenciais
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_PATH, scopes=['https://www.googleapis.com/auth/drive']
    )
    
    # Cria o serviço do Google Drive
    service = build('drive', 'v3', credentials=credentials)
    
    # Cria a pasta principal do projeto
    main_folder_id = create_folder(service, 'Uai Manutenção - Site')
    
    # Cria subpastas para organizar os arquivos
    images_folder_id = create_folder(service, 'Imagens', main_folder_id)
    data_folder_id = create_folder(service, 'Dados', main_folder_id)
    
    # Salva os IDs das pastas em um arquivo de configuração
    config = f"""# Configuração das pastas do Google Drive
MAIN_FOLDER_ID = '{main_folder_id}'
IMAGES_FOLDER_ID = '{images_folder_id}'
DATA_FOLDER_ID = '{data_folder_id}'
"""
    
    with open('gdrive_config.py', 'w') as f:
        f.write(config)
    
    print("\nConfiguração salva em 'gdrive_config.py'")
    print("Você pode usar esses IDs no seu código para acessar as pastas.")

if __name__ == '__main__':
    main()
