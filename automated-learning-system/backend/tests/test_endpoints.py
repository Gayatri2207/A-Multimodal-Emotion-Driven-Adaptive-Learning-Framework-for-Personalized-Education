"""Integration tests for auth and analytics endpoints."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

# Use in-memory SQLite for tests
TEST_DB_URL = "sqlite:///./test_integration.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    try:
        os.remove("./test_integration.db")
    except OSError:
        pass


client = TestClient(app)


class TestHealth:
    def test_health(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"


class TestAuth:
    def test_register(self):
        resp = client.post("/auth/register", json={"email": "test@example.com", "password": "password123"})
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert "access_token" in data

    def test_register_duplicate(self):
        client.post("/auth/register", json={"email": "dup@example.com", "password": "password123"})
        resp = client.post("/auth/register", json={"email": "dup@example.com", "password": "password123"})
        assert resp.status_code == 400

    def test_login_success(self):
        client.post("/auth/register", json={"email": "login@example.com", "password": "password123"})
        resp = client.post("/auth/login", json={"email": "login@example.com", "password": "password123"})
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_login_wrong_password(self):
        client.post("/auth/register", json={"email": "wp@example.com", "password": "password123"})
        resp = client.post("/auth/login", json={"email": "wp@example.com", "password": "wrongpass"})
        assert resp.status_code == 401


class TestAnalytics:
    def test_summary_empty(self):
        resp = client.get("/analytics/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert "average_emotion" in data
        assert "engagement_score" in data

    def test_dashboard_empty(self):
        resp = client.get("/analytics/dashboard")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestCodingProblems:
    def test_list_problems(self):
        resp = client.get("/coding/problems")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_create_and_get_problem(self):
        payload = {
            "title": "Test Problem",
            "description": "Print hello",
            "difficulty": "easy",
            "starter_code": "# starter\n",
        }
        create_resp = client.post("/coding/problems", json=payload)
        assert create_resp.status_code == 201
        pid = create_resp.json()["id"]

        get_resp = client.get(f"/coding/problems/{pid}")
        assert get_resp.status_code == 200
        assert get_resp.json()["title"] == "Test Problem"

    def test_submit_code(self):
        # Create problem with a test case
        prob = client.post("/coding/problems", json={
            "title": "Print 42",
            "description": "Print 42",
            "difficulty": "easy",
        }).json()
        pid = prob["id"]
        client.post(f"/coding/problems/{pid}/test-cases", json={
            "stdin": "",
            "expected_stdout": "42",
        })

        result = client.post("/coding/submit", json={
            "problem_id": pid,
            "code": "print(42)",
        })
        assert result.status_code == 200
        data = result.json()
        assert data["passed"] == 1
        assert data["score"] == 1.0

    def test_missing_problem(self):
        resp = client.get("/coding/problems/99999")
        assert resp.status_code == 404
