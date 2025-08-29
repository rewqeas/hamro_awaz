"""
Test suite for the main FastAPI application.
Tests basic functionality and API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_read_root():
    """Test the root endpoint returns correct welcome message."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Complaint Box API running"}

def test_auth_endpoints():
    """Test authentication endpoints require proper credentials."""
    # Test login endpoint
    response = client.post("/auth/login", json={
        "phone": "test_user",
        "password": "wrong_password"
    })
    assert response.status_code == 401

def test_complaints_endpoints():
    """Test complaints endpoints require authentication."""
    response = client.get("/complaints/")
    assert response.status_code == 401

def test_municipality_endpoints():
    """Test municipality endpoints require authentication."""
    response = client.get("/municipality/")
    assert response.status_code == 401

def test_static_files_configuration():
    """Test static files are properly configured."""
    response = client.get("/uploads/")
    assert response.status_code in [404, 403]  # Should not list directory contents
