# tests/test_routes.py
import pytest
from app import app  # import your Flask app
from flask import url_for


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_home(client):
    """Test the home page"""
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'Welcome to Schedge' in rv.data  # Check if the text exists on the page


def test_login_page(client):
    """Test the login page"""
    rv = client.get('/login')
    assert rv.status_code == 200
    assert b'Login' in rv.data


def test_signup_page(client):
    """Test the signup page"""
    rv = client.get('/signup')
    assert rv.status_code == 200
    assert b'Signup' in rv.data


def test_admin_dashboard(client):
    """Test the admin dashboard page"""
    rv = client.get('/admin_dashboard')
    assert rv.status_code == 200
    assert b'Admin Dashboard' in rv.data


def test_employee_dashboard(client):
    """Test the employee dashboard page"""
    rv = client.get('/employee_dashboard')
    assert rv.status_code == 200
    assert b'Employee Dashboard' in rv.data


def test_logout(client):
    """Test the logout functionality"""
    rv = client.get('/logout')
    assert rv.status_code == 302  # redirect status code after logout
    assert rv.location == url_for('login', _external=True)  # check if redirected to login
