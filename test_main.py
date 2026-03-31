import pytest
from fastapi.testclient import TestClient
from main import app  # Pastikan file utamamu bernama main.py

client = TestClient(app)

# ==========================================
# FIXTURES (Data Awal untuk Testing)
# ==========================================

@pytest.fixture
def test_user():
    return {
        "username": "biasa_user",
        "password": "password123",
        "role": "user"
    }

@pytest.fixture
def test_admin():
    return {
        "username": "super_admin",
        "password": "adminpassword",
        "role": "admin"
    }

# Helper function untuk mendapatkan token
def get_token(user_data):
    # Register dulu jika belum ada, lalu login
    client.post("/register", json=user_data)
    res = client.post("/login", data={"username": user_data["username"], "password": user_data["password"]})
    return res.json().get("access_token")

# ==========================================
# TEST CASES (Urutan persis seperti gambar)
# ==========================================

# 1. test_register_user
def test_register_user(test_user):
    response = client.post("/register", json=test_user)
    assert response.status_code in [200, 201]

# 2. test_login_user
def test_login_user(test_user):
    login_data = {"username": test_user["username"], "password": test_user["password"]}
    response = client.post("/login", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()

# 3. test_register_admin
def test_register_admin(test_admin):
    response = client.post("/register", json=test_admin)
    assert response.status_code in [200, 201]

# 4. test_login_admin
def test_login_admin(test_admin):
    login_data = {"username": test_admin["username"], "password": test_admin["password"]}
    response = client.post("/login", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()

# 5. test_user_cannot_create_item
def test_user_cannot_create_item(test_user):
    token = get_token(test_user)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"name": "Hack Item", "description": "User biasa coba tambah"}
    
    response = client.post("/items/", json=payload, headers=headers)
    assert response.status_code == 403  # Harus ditolak (Access denied)

# 6. test_admin_can_create_item
def test_admin_can_create_item(test_admin):
    token = get_token(test_admin)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"name": "Admin Item", "description": "Ditambahkan oleh Admin"}
    
    response = client.post("/items/", json=payload, headers=headers)
    assert response.status_code == 200  # Harus berhasil

# 7. test_user_can_read_items
def test_user_can_read_items(test_user):
    token = get_token(test_user)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/items/", headers=headers)
    assert response.status_code == 200  # Harus bisa membaca list item
    assert isinstance(response.json(), list)