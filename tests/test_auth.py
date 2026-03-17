# tests/test_auth.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json()['status'] == 'MedMatch API is running'

def test_register_user():
    response = client.post('/api/auth/register', json={
        'email': 'test@example.com',
        'password': 'password123',
        'full_name': 'Test User',
        'role': 'mentee'
    })
    assert response.status_code == 201
    assert response.json()['email'] == 'test@example.com'