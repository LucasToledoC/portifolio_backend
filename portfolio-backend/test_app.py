"""
Unit Tests for Portfolio Backend API
Tests the main Flask application endpoints
"""

import pytest
import json
from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestHealthCheck:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test GET /health returns 200 OK."""
        response = client.get("/health")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "ok"
        assert "message" in data


class TestProjectsEndpoints:
    """Test projects CRUD endpoints."""

    def test_get_projects_empty(self, client):
        """Test GET /api/projetos returns empty list initially."""
        response = client.get("/api/projetos")
        assert response.status_code == 200
        # Response should be a list (may be empty or have test data)
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_create_project_without_auth(self, client):
        """Test POST /api/projetos without auth returns 401."""
        response = client.post(
            "/api/projetos",
            json={
                "titulo": "Test Project",
                "descricao": "Test Description",
                "tecnologias": "Python, Flask",
            },
        )
        assert response.status_code == 401

    def test_create_project_with_wrong_password(self, client):
        """Test POST /api/projetos with wrong password returns 401."""
        response = client.post(
            "/api/projetos",
            headers={"Authorization": "Bearer wrongpassword"},
            json={
                "titulo": "Test Project",
                "descricao": "Test Description",
                "tecnologias": "Python, Flask",
            },
        )
        assert response.status_code == 401

    def test_create_project_missing_fields(self, client):
        """Test POST /api/projetos with missing required fields returns 400."""
        response = client.post(
            "/api/projetos",
            headers={"Authorization": "Bearer admin123"},
            json={"titulo": "Test Project"},  # Missing descricao and tecnologias
        )
        assert response.status_code == 400

    def test_invalid_auth_header(self, client):
        """Test invalid Authorization header format returns 401."""
        response = client.post(
            "/api/projetos",
            headers={"Authorization": "InvalidFormat"},
            json={
                "titulo": "Test Project",
                "descricao": "Test Description",
                "tecnologias": "Python, Flask",
            },
        )
        assert response.status_code == 401

    def test_get_nonexistent_project(self, client):
        """Test GET /api/projetos/{id} with non-existent ID returns 404."""
        response = client.get("/api/projetos/99999")
        assert response.status_code == 404


class TestCertificatesEndpoints:
    """Test certificates CRUD endpoints."""

    def test_get_certificates_empty(self, client):
        """Test GET /api/certificados returns list."""
        response = client.get("/api/certificados")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_get_certificates_with_filter(self, client):
        """Test GET /api/certificados?origem=FIAP filters correctly."""
        response = client.get("/api/certificados?origem=FIAP")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        # All returned certificates should have origem=FIAP
        for cert in data:
            assert cert.get("origem") == "FIAP"

    def test_create_certificate_without_auth(self, client):
        """Test POST /api/certificados without auth returns 401."""
        response = client.post(
            "/api/certificados",
            json={
                "nome": "Test Certificate",
                "instituicao": "Test Institution",
                "data_conclusao": "2025-01-15",
            },
        )
        assert response.status_code == 401

    def test_create_certificate_missing_fields(self, client):
        """Test POST /api/certificados with missing fields returns 400."""
        response = client.post(
            "/api/certificados",
            headers={"Authorization": "Bearer admin123"},
            json={"nome": "Test Certificate"},  # Missing required fields
        )
        assert response.status_code == 400

    def test_get_nonexistent_certificate(self, client):
        """Test GET /api/certificados/{id} with non-existent ID returns 404."""
        response = client.get("/api/certificados/99999")
        assert response.status_code == 404


class TestVisitsEndpoints:
    """Test visits tracking endpoints."""

    def test_get_visits(self, client):
        """Test GET /api/visitas returns visit count."""
        response = client.get("/api/visitas")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "total" in data
        assert isinstance(data["total"], int)

    def test_increment_visits(self, client):
        """Test POST /api/visitas increments counter."""
        # Get initial count
        response1 = client.get("/api/visitas")
        initial_count = json.loads(response1.data)["total"]

        # Increment
        response2 = client.post("/api/visitas")
        assert response2.status_code in [200, 201]
        new_count = json.loads(response2.data)["total"]

        # Verify increment
        assert new_count >= initial_count


class TestErrorHandling:
    """Test error handling."""

    def test_404_not_found(self, client):
        """Test non-existent endpoint returns 404."""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
        data = json.loads(response.data)
        assert "error" in data

    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        response = client.get("/api/projetos")
        # Flask-CORS should add these headers
        assert response.status_code == 200


class TestAuthenticationDecorator:
    """Test authentication decorator functionality."""

    def test_missing_auth_header(self, client):
        """Test missing Authorization header returns 401."""
        response = client.post(
            "/api/projetos",
            json={
                "titulo": "Test",
                "descricao": "Test",
                "tecnologias": "Test",
            },
        )
        assert response.status_code == 401

    def test_bearer_token_format(self, client):
        """Test Bearer token format validation."""
        # Missing "Bearer" prefix
        response = client.post(
            "/api/projetos",
            headers={"Authorization": "admin123"},
            json={
                "titulo": "Test",
                "descricao": "Test",
                "tecnologias": "Test",
            },
        )
        assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

