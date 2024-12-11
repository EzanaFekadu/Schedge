import pytest
from app import app  # Assuming your Flask app is in app.py
from flask import jsonify

@pytest.fixture
def client():
    """Create a test client for Flask."""
    with app.test_client() as client:
        yield client

def test_get_schedule(client):
    """Test fetching the schedule from the API."""
    response = client.get('/api/schedule')  # Adjust with the correct API route
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)  # Expecting a list of schedules
    assert 'task' in data[0]  # Verify the task field exists in the response

def test_create_schedule(client):
    """Test creating a new schedule."""
    new_schedule = {
        'employee_id': 1,
        'date': '2024-12-15',
        'start_time': '09:00',
        'end_time': '17:00',
        'task': 'Team Meeting'
    }
    response = client.post('/api/schedule', json=new_schedule)
    assert response.status_code == 201
    data = response.get_json()
    assert data['task'] == new_schedule['task']  # Verify the task is correct

def test_delete_schedule(client):
    """Test deleting a schedule."""
    # Assuming schedule ID 1 exists
    response = client.delete('/api/schedule/1')
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Schedule deleted successfully'

def test_update_schedule(client):
    """Test updating a schedule."""
    updated_schedule = {
        'employee_id': 1,
        'date': '2024-12-16',
        'start_time': '10:00',
        'end_time': '18:00',
        'task': 'Project Update'
    }
    response = client.put('/api/schedule/1', json=updated_schedule)
    assert response.status_code == 200
    data = response.get_json()
    assert data['task'] == updated_schedule['task']  # Verify the task was updated
