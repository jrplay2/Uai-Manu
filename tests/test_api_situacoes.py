import os
import pytest
import tempfile
from src import create_app, db
from src.models.situacao import SituacaoManutencao
from io import BytesIO

# Pytest fixture for the Flask application
@pytest.fixture(scope='module')
def app():
    """Create and configure a new app instance for each test module."""
    # Create a temporary file for the SQLite database
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    
    # Configure the app for testing
    # Use a temporary database for testing
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
        "WTF_CSRF_ENABLED": False,  # Disable CSRF for testing forms if you have them
        "SECRET_KEY": "test_secret_key", # Test specific secret key
        "UPLOAD_FOLDER": tempfile.mkdtemp() # Test specific upload folder
    }
    
    _app = create_app(config_object=test_config)

    with _app.app_context():
        db.create_all() # Create all tables

    yield _app # Provides the app instance to the tests

    # Teardown: close and remove the temporary database file
    os.close(db_fd)
    os.unlink(db_path)
    # Clean up upload folder (though tempfile might handle parts of this)
    # For more complex scenarios, shutil.rmtree might be needed for the UPLOAD_FOLDER

# Pytest fixture for the Flask test client
@pytest.fixture(scope='module')
def client(app):
    """A test client for the app."""
    return app.test_client()

# Pytest fixture to clean up database tables after each test
@pytest.fixture(autouse=True)
def cleanup_db(app):
    """Cleans up the database after each test function if needed,
       or simply provides a fresh context. For this setup, 
       create_all is run once per module. If tests modify db and need isolation,
       this fixture would handle session rollbacks or recreating tables per test.
       For now, we rely on module-level setup and specific test actions for cleanup if needed.
    """
    yield
    # If tests add data and don't clean up, you might need to clear tables here.
    # For example, with app.app_context():
    #     meta = db.metadata
    #     for table in reversed(meta.sorted_tables):
    #         db.session.execute(table.delete())
    #     db.session.commit()


def test_get_no_situacoes(client):
    """Test GET /api/situacoes when no situations exist."""
    response = client.get('/api/situacoes')
    assert response.status_code == 200
    assert response.json == []

def test_create_situacao_no_image(client, app):
    """Test POST /api/situacoes without an image."""
    data = {
        'nome_tarefa': 'Test Task 1',
        'observacoes': 'This is a test observation.'
    }
    response = client.post('/api/situacoes', data=data)
    assert response.status_code == 201
    assert response.json['nome_tarefa'] == 'Test Task 1'
    assert response.json['observacoes'] == 'This is a test observation.'
    assert response.json['imagem_path'] is None
    
    with app.app_context():
        assert SituacaoManutencao.query.count() == 1
        # Clean up
        SituacaoManutencao.query.delete()
        db.session.commit()


def test_create_situacao_with_image(client, app):
    """Test POST /api/situacoes with an image."""
    image_content = b"fake_image_content_for_test"
    data = {
        'nome_tarefa': 'Test Task with Image',
        'observacoes': 'Observation for image task.',
        'imagem': (BytesIO(image_content), 'test_image.jpg')
    }
    response = client.post('/api/situacoes', data=data, content_type='multipart/form-data')
    
    assert response.status_code == 201
    assert response.json['nome_tarefa'] == 'Test Task with Image'
    assert response.json['imagem_path'] is not None
    assert 'test_image.jpg' in response.json['imagem_path']

    # Verify the file was "uploaded" (exists in the test upload folder)
    uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'test_image.jpg')
    assert os.path.exists(uploaded_file_path)
    
    # Clean up the created file and database entry
    if os.path.exists(uploaded_file_path):
        os.remove(uploaded_file_path)
    
    with app.app_context():
        situacao = SituacaoManutencao.query.filter_by(nome_tarefa='Test Task with Image').first()
        if situacao:
            db.session.delete(situacao)
            db.session.commit()

def test_get_situacao_by_id(client, app):
    """Test GET /api/situacoes/<id>."""
    with app.app_context():
        new_situacao = SituacaoManutencao(nome_tarefa='Specific Task', status='em_analise')
        db.session.add(new_situacao)
        db.session.commit()
        task_id = new_situacao.id

    response = client.get(f'/api/situacoes/{task_id}')
    assert response.status_code == 200
    assert response.json['nome_tarefa'] == 'Specific Task'
    assert response.json['id'] == task_id

    with app.app_context(): # Cleanup
        SituacaoManutencao.query.filter_by(id=task_id).delete()
        db.session.commit()


def test_update_situacao(client, app):
    """Test PUT /api/situacoes/<id>."""
    with app.app_context():
        new_situacao = SituacaoManutencao(nome_tarefa='Task to Update', status='pendente')
        db.session.add(new_situacao)
        db.session.commit()
        task_id = new_situacao.id

    update_data = {'nome_tarefa': 'Updated Task Name', 'status': 'concluido'}
    response = client.put(f'/api/situacoes/{task_id}', json=update_data)
    
    assert response.status_code == 200
    assert response.json['nome_tarefa'] == 'Updated Task Name'
    assert response.json['status'] == 'concluido'

    with app.app_context(): # Cleanup
        SituacaoManutencao.query.filter_by(id=task_id).delete()
        db.session.commit()

def test_delete_situacao(client, app):
    """Test DELETE /api/situacoes/<id>."""
    with app.app_context():
        # Create a task with an image to test image deletion as well
        image_filename = 'delete_test_image.jpg'
        image_content = b"fake_image_for_delete_test"
        
        # Ensure upload folder exists
        upload_folder = app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            
        temp_image_path = os.path.join(upload_folder, image_filename)
        with open(temp_image_path, 'wb') as f:
            f.write(image_content)

        new_situacao = SituacaoManutencao(
            nome_tarefa='Task to Delete', 
            status='pendente',
            imagem_path=os.path.join('uploads', image_filename) # Path as stored in DB
        )
        db.session.add(new_situacao)
        db.session.commit()
        task_id = new_situacao.id
        
        # Verify image exists before deletion
        # The actual image path is instance_path + imagem_path
        # For test, UPLOAD_FOLDER is app.config['UPLOAD_FOLDER'] which is already absolute
        # And the path stored in db is relative 'uploads/filename.jpg'
        # So, the API constructs current_app.instance_path + situacao.imagem_path
        # For tests, current_app.instance_path could be different.
        # The UPLOAD_FOLDER is set to a temp dir, and imagem_path is 'uploads/filename.jpg'
        # The API will try to delete app.instance_path + 'uploads/' + filename
        # We save the test image directly into app.config['UPLOAD_FOLDER'] which is a flat temp dir.
        # The delete API will look for app.instance_path + 'uploads/delete_test_image.jpg'
        # To make this align, the image_path in db should be just 'delete_test_image.jpg' if UPLOAD_FOLDER is flat.
        # Let's adjust:
        # The API saves image to app.config['UPLOAD_FOLDER']/filename
        # And stores 'uploads/filename' in DB.
        # The API deletes os.path.join(app.instance_path, db_image_path)
        # So if db_image_path is 'uploads/file.jpg', it looks in instance_path/uploads/file.jpg
        # In test, app.config['UPLOAD_FOLDER'] is a flat temp dir.
        # And app.instance_path is a different temp dir.
        # So, for the test delete to work as the API works, the image needs to be in:
        # app.instance_path / 'uploads' / image_filename
        
        # Re-adjusting image setup for delete test to match API's expected structure
        # The API stores 'uploads/filename.jpg' and expects it at 'instance_path/uploads/filename.jpg'
        test_instance_upload_dir = os.path.join(app.instance_path, 'uploads')
        if not os.path.exists(test_instance_upload_dir):
            os.makedirs(test_instance_upload_dir)
        
        actual_image_path_for_api_to_delete = os.path.join(test_instance_upload_dir, image_filename)
        with open(actual_image_path_for_api_to_delete, 'wb') as f:
            f.write(image_content)
        
        # Update the situacao's image_path to what the API expects
        new_situacao.imagem_path = os.path.join('uploads', image_filename)
        db.session.commit()

        assert os.path.exists(actual_image_path_for_api_to_delete)


    response = client.delete(f'/api/situacoes/{task_id}')
    assert response.status_code == 200
    assert response.json['message'] == 'Situacao deleted successfully'

    with app.app_context():
        assert SituacaoManutencao.query.get(task_id) is None
    
    # Check if image was deleted by the API endpoint
    assert not os.path.exists(actual_image_path_for_api_to_delete)
