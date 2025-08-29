import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to HamroAawaz API"}

def test_read_complaints():
    response = client.get("/complaints/")
    assert response.status_code == 401  # Should require authentication

def test_read_municipalities():
    response = client.get("/municipality/")
    assert response.status_code == 401  # Should require authentication
