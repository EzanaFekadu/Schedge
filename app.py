from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

DATABASE = 'schedules.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def setup_database():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY,
                date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                task TEXT NOT NULL
            )
        ''')
        # Add some example data if it's not already in the table
        conn.execute('INSERT OR IGNORE INTO schedules (id, date, start_time, end_time, task) VALUES (1, "2024-11-21", "10:00 AM", "11:00 AM", "Team Meeting")')
        conn.execute('INSERT OR IGNORE INTO schedules (id, date, start_time, end_time, task) VALUES (2, "2024-11-22", "2:00 PM", "3:00 PM", "Project Review")')
        conn.commit()

# Run this once when the app starts
setup_database()

@app.route('/')
def hello_world():
    return "Hello, World!"

# Fetch schedules for a given date range
@app.route('/schedules', methods=['GET'])
def get_schedules():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    with get_db_connection() as conn:
        schedules = conn.execute('''
            SELECT date, start_time, end_time, task FROM schedules
            WHERE date BETWEEN ? AND ?
            ORDER BY date, start_time
        ''', (start_date, end_date)).fetchall()

    return jsonify([dict(row) for row in schedules])

# Add a new schedule
@app.route('/schedules', methods=['POST'])
def add_schedule():
    new_schedule = request.get_json()
    date = new_schedule['date']
    start_time = new_schedule['start_time']
    end_time = new_schedule['end_time']
    task = new_schedule['task']

    with get_db_connection() as conn:
        conn.execute('''
            INSERT INTO schedules (date, start_time, end_time, task)
            VALUES (?, ?, ?, ?)
        ''', (date, start_time, end_time, task))
        conn.commit()

    return jsonify({'status': 'success', 'message': 'Schedule added!'})

if __name__ == '__main__':
    app.run(debug=True)
