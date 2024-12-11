import pytest
from app import app, db
from models import Employee, Schedule
from flask import jsonify


@pytest.fixture
def client():
    """Fixture to setup Flask test client"""
    with app.test_client() as client:
        yield client


@pytest.fixture
def init_db():
    """Fixture to initialize the database with sample data"""
    db.create_all()

    # Add sample employees
    employee_1 = Employee(name="John Doe", position="Developer", department="Engineering")
    employee_2 = Employee(name="Jane Smith", position="Manager", department="Sales")
    db.session.add(employee_1)
    db.session.add(employee_2)
    db.session.commit()

    # Add sample schedules
    schedule_1 = Schedule(employee_id=1, date="2024-12-15", start_time="09:00", end_time="17:00", task="Development Work")
    schedule_2 = Schedule(employee_id=2, date="2024-12-16", start_time="10:00", end_time="16:00", task="Client Meeting")
    db.session.add(schedule_1)
    db.session.add(schedule_2)
    db.session.commit()

    yield db
    db.drop_all()


def test_login(client, init_db):
    """Test login functionality"""
    response = client.post('/login', data={'username': 'John Doe', 'password': 'password'})
    assert response.status_code == 200
    assert b"Welcome" in response.data


def test_get_employee(client, init_db):
    """Test retrieving employee data"""
    response = client.get('/employee/1')
    assert response.status_code == 200
    assert b"John Doe" in response.data


def test_create_schedule(client, init_db):
    """Test creating a schedule"""
    response = client.post('/create_schedule', data={
        'employee_id': 1,
        'date': '2024-12-18',
        'start_time': '08:00',
        'end_time': '16:00',
        'task': 'Team Meeting'
    })
    assert response.status_code == 200
    assert b"Team Meeting" in response.data


def test_get_schedules(client, init_db):
    """Test getting the schedule list for an employee"""
    response = client.get('/schedules/1')  # Get schedules for employee with ID 1
    assert response.status_code == 200
    assert b"Development Work" in response.data
    assert b"2024-12-15" in response.data


def test_update_schedule(client, init_db):
    """Test updating an existing schedule"""
    response = client.post('/edit_schedule/1', data={
        'employee_id': 1,
        'date': '2024-12-18',
        'start_time': '10:00',
        'end_time': '18:00',
        'task': 'Code Review'
    })
    assert response.status_code == 200
    assert b"Code Review" in response.data


def test_delete_schedule(client, init_db):
    """Test deleting a schedule"""
    response = client.delete('/delete_schedule/1')
    assert response.status_code == 200
    assert b"Schedule Deleted" in response.data


def test_invalid_schedule_date(client, init_db):
    """Test creating a schedule with an invalid date"""
    response = client.post('/create_schedule', data={
        'employee_id': 1,
        'date': '2024-02-30',  # Invalid date
        'start_time': '09:00',
        'end_time': '17:00',
        'task': 'Bug Fixing'
    })
    assert response.status_code == 400  # Expecting a Bad Request for invalid date


def test_invalid_login(client):
    """Test logging in with invalid credentials"""
    response = client.post('/login', data={'username': 'Invalid User', 'password': 'wrongpassword'})
    assert response.status_code == 401  # Unauthorized


def test_logout(client):
    """Test logging out of the session"""
    response = client.get('/logout')
    assert response.status_code == 200
    assert b"You have been logged out" in response.data
