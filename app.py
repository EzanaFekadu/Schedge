from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
bcrypt = Bcrypt(app)
CORS(app)
app.secret_key = 'your_secret_key'

DATABASE = 'schedules.db'

# Database connection setup
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Set up database and tables if they don't exist
def setup_database():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'employee'))
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                position TEXT NOT NULL,
                department TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                task TEXT NOT NULL,
                FOREIGN KEY(employee_id) REFERENCES employees(id)
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS shift_swaps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                requester_id INTEGER NOT NULL,
                requested_shift_id INTEGER NOT NULL,
                target_shift_id INTEGER NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('pending', 'approved', 'declined')),
                FOREIGN KEY(requester_id) REFERENCES users(id),
                FOREIGN KEY(requested_shift_id) REFERENCES schedules(id),
                FOREIGN KEY(target_shift_id) REFERENCES schedules(id)
            )
        ''')
        conn.commit()

setup_database()

@app.route('/')
def landing_page():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if user exists and password is correct
        with get_db_connection() as conn:
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

        if user and bcrypt.check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['role'] = user['role']
            # Redirect to the correct dashboard based on the user's role
            if user['role'] == 'employee':
                return redirect(url_for('employee_dashboard'))  # Updated to 'employee_dashboard'
            else:
                return redirect(url_for('admin_dashboard'))
        else:
            error = "Invalid username or password"
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        try:
            with get_db_connection() as conn:
                # Insert the new user into the database
                conn.execute(
                    'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                    (username, hashed_password, role)
                )
                conn.commit()

            # Redirect to login page upon successful signup
            return redirect(url_for('login'))

        except sqlite3.IntegrityError:
            # Handle duplicate usernames
            return render_template('signup.html', error='Username already exists')

        except Exception as e:
            # Log unexpected errors (optional) and display a generic message
            print(f"Error during signup: {e}")
            return render_template('signup.html', error='An unexpected error occurred. Please try again.')

    # Render signup page for GET requests
    return render_template('signup.html')

@app.route('/admin')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    with get_db_connection() as conn:
        employees = conn.execute('SELECT * FROM employees').fetchall()  # Get employees from the database
        schedules = conn.execute(''' 
            SELECT schedules.id, employees.name, schedules.date, schedules.start_time, schedules.end_time, schedules.task
            FROM schedules
            JOIN employees ON schedules.employee_id = employees.id
        ''').fetchall()  # Get schedules with employee names
    
    return render_template('admin_dashboard.html', employees=employees, schedules=schedules)

@app.route('/api/get_employees', methods=['GET'])
def api_get_employees():
    with get_db_connection() as conn:
        employees = conn.execute('SELECT * FROM employees').fetchall()  # Query the database to get employees
        employees_list = [{'id': emp['id'], 'name': emp['name'], 'position': emp['position'], 'department': emp['department']} for emp in employees]
    
    return jsonify({'employees': employees_list})

@app.route('/employee')
def employee_dashboard():
    if session.get('role') != 'employee':
        return redirect(url_for('login'))

    user_id = session.get('user_id')  # Fetch logged-in user's ID
    with get_db_connection() as conn:
        # Query schedules for the logged-in user
        schedules = conn.execute('''
            SELECT schedules.id, schedules.date, schedules.start_time, schedules.end_time, schedules.task, 
                employees.name AS employee_name, employees.position AS employee_position, employees.department AS employee_department
            FROM schedules
            JOIN employees ON schedules.employee_id = employees.id
            JOIN users ON employees.id = users.id
            WHERE users.id = ?
        ''', (user_id,)).fetchall()

    schedule_list = [dict(row) for row in schedules]  # Convert rows to dictionaries for JSON serialization
    return render_template('employee_dashboard.html', schedules=schedule_list)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landing_page'))

@app.route('/add_employee', methods=['POST'])
def add_employee():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    name = request.form['name']
    position = request.form['position']
    department = request.form['department']
    
    with get_db_connection() as conn:
        conn.execute('INSERT INTO employees (name, position, department) VALUES (?, ?, ?)', 
                    (name, position, department))
        conn.commit()

    return redirect(url_for('admin_dashboard'))

@app.route('/delete_employee/<int:employee_id>', methods=['POST'])
def delete_employee(employee_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    with get_db_connection() as conn:
        conn.execute('DELETE FROM employees WHERE id = ?', (employee_id,))
        conn.commit()

    return redirect(url_for('admin_dashboard'))

@app.route('/add_schedule', methods=['POST'])
def add_schedule():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    employee_id = request.form['employee_id']
    date = request.form['date']
    start_time = request.form['start_time']
    end_time = request.form['end_time']
    task = request.form['task']
    
    with get_db_connection() as conn:
        conn.execute('INSERT INTO schedules (employee_id, date, start_time, end_time, task) VALUES (?, ?, ?, ?, ?)',
                    (employee_id, date, start_time, end_time, task))
        conn.commit()

    return redirect(url_for('admin_dashboard'))

@app.route('/delete_schedule/<int:schedule_id>', methods=['POST'])
def delete_schedule(schedule_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    with get_db_connection() as conn:
        conn.execute('DELETE FROM schedules WHERE id = ?', (schedule_id,))
        conn.commit()

    return redirect(url_for('admin_dashboard'))

@app.route('/edit_employee/<int:employee_id>', methods=['GET', 'POST'])
def edit_employee(employee_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    with get_db_connection() as conn:
        employee = conn.execute('SELECT * FROM employees WHERE id = ?', (employee_id,)).fetchone()
    
    if request.method == 'POST':
        name = request.form['name']
        position = request.form['position']
        department = request.form['department']
        with get_db_connection() as conn:
            conn.execute('UPDATE employees SET name = ?, position = ?, department = ? WHERE id = ?',
                        (name, position, department, employee_id))
            conn.commit()
        return redirect(url_for('admin_dashboard'))
    
    return render_template('edit_employee.html', employee=employee)

@app.route('/edit_schedule/<int:schedule_id>', methods=['GET', 'POST'])
def edit_schedule(schedule_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    with get_db_connection() as conn:
        schedule = conn.execute('SELECT * FROM schedules WHERE id = ?', (schedule_id,)).fetchone()
        employees = conn.execute('SELECT * FROM employees').fetchall()
    
    if request.method == 'POST':
        employee_id = request.form['employee_id']
        date = request.form['date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        task = request.form['task']
        with get_db_connection() as conn:
            conn.execute('UPDATE schedules SET employee_id = ?, date = ?, start_time = ?, end_time = ?, task = ? WHERE id = ?',
                        (employee_id, date, start_time, end_time, task, schedule_id))
            conn.commit()
        return redirect(url_for('admin_dashboard'))
    
    return render_template('edit_schedule.html', schedule=schedule, employees=employees)

@app.route('/swap_shift', methods=['POST'])
def swap_shift():
    if session.get('role') != 'employee':
        return redirect(url_for('login'))

    requester_id = session['user_id']
    requested_shift_id = request.form['requested_shift_id']
    target_shift_id = request.form['target_shift_id']

    with get_db_connection() as conn:
        # Fetch details of both shifts
        requested_shift = conn.execute('SELECT * FROM schedules WHERE id = ?', (requested_shift_id,)).fetchone()
        target_shift = conn.execute('SELECT * FROM schedules WHERE id = ?', (target_shift_id,)).fetchone()

        # Check for overlapping times
        if (requested_shift and target_shift and
                requested_shift['start_time'] < target_shift['end_time'] and
                requested_shift['end_time'] > target_shift['start_time']):
            return jsonify({'error': 'Shifts overlap and cannot be swapped.'}), 400

        # Proceed with inserting the swap request
        conn.execute('''
            INSERT INTO shift_swaps (requester_id, requested_shift_id, target_shift_id, status)
            VALUES (?, ?, ?, 'pending')
        ''', (requester_id, requested_shift_id, target_shift_id))
        conn.commit()

    return redirect(url_for('employee_dashboard'))

@app.route('/view_swap_requests')
def view_swap_requests():
    if session.get('role') != 'employee':
        return redirect(url_for('login'))
    
    user_id = session['user_id']

    with get_db_connection() as conn:
        requests = conn.execute('''
            SELECT ss.id, ss.status, s1.date AS requested_date, s2.date AS target_date
            FROM shift_swaps ss
            JOIN schedules s1 ON ss.requested_shift_id = s1.id
            JOIN schedules s2 ON ss.target_shift_id = s2.id
            WHERE ss.requester_id = ?
        ''', (user_id,)).fetchall()
    
    return render_template('view_swap_requests.html', requests=requests)

@app.route('/manage_shift_swaps')
def manage_shift_swaps():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    with get_db_connection() as conn:
        swap_requests = conn.execute('''
            SELECT ss.id, ss.status, u.username AS requester, 
                s1.date AS requested_date, s2.date AS target_date
            FROM shift_swaps ss
            JOIN users u ON ss.requester_id = u.id
            JOIN schedules s1 ON ss.requested_shift_id = s1.id
            JOIN schedules s2 ON ss.target_shift_id = s2.id
            WHERE ss.status = 'pending'
        ''').fetchall()
    
    return render_template('manage_shift_swaps.html', swap_requests=swap_requests)

@app.route('/update_swap_status/<int:swap_id>', methods=['POST'])
def update_swap_status(swap_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    status = request.form['status']  # 'approved' or 'declined'
    
    with get_db_connection() as conn:
        if status == 'approved':
            # Update the schedules if approved
            swap_request = conn.execute('''
                SELECT requested_shift_id, target_shift_id
                FROM shift_swaps
                WHERE id = ?
            ''', (swap_id,)).fetchone()

            conn.execute('''
                UPDATE schedules
                SET employee_id = (CASE
                    WHEN id = ? THEN (SELECT employee_id FROM schedules WHERE id = ?)
                    WHEN id = ? THEN (SELECT employee_id FROM schedules WHERE id = ?)
                END)
                WHERE id IN (?, ?)
            ''', (swap_request['requested_shift_id'], swap_request['target_shift_id'],
                swap_request['target_shift_id'], swap_request['requested_shift_id'],
                swap_request['requested_shift_id'], swap_request['target_shift_id']))

        conn.execute('UPDATE shift_swaps SET status = ? WHERE id = ?', (status, swap_id))
        conn.commit()

    return redirect(url_for('manage_shift_swaps'))

if __name__ == '__main__':
    app.run(debug=True)
