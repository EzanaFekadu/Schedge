# tests/test_api.py
import pytest
from app import app, db
from app.models import Employee

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Set up and tear down test data"""
    db.create_all()
    yield
    db.session.remove()
    db.drop_all()


def test_create_employee(client):
    """Test creating an employee via API"""
    data = {'name': 'John Doe', 'position': 'Developer', 'department': 'Engineering'}
    rv = client.post('/api/employees', json=data)
    assert rv.status_code == 201
    assert b'John Doe' in rv.data


def test_get_employee(client):
    """Test retrieving an employee's details"""
    employee = Employee(name='Jane Doe', position='Manager', department='Sales')
    db.session.add(employee)
    db.session.commit()

    rv = client.get(f'/api/employees/{employee.id}')
    assert rv.status_code == 200
    assert b'Jane Doe' in rv.data


def test_update_employee(client):
    """Test updating an employee's details"""
    employee = Employee(name='John Smith', position='Developer', department='Engineering')
    db.session.add(employee)
    db.session.commit()

    data = {'name': 'John Doe', 'position': 'Senior Developer', 'department': 'Engineering'}
    rv = client.put(f'/api/employees/{employee.id}', json=data)
    assert rv.status_code == 200
    assert b'Senior Developer' in rv.data


def test_delete_employee(client):
    """Test deleting an employee"""
    employee = Employee(name='Jane Smith', position='Manager', department='HR')
    db.session.add(employee)
    db.session.commit()

    rv = client.delete(f'/api/employees/{employee.id}')
    assert rv.status_code == 204  # No content
