from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import check_password_hash
from backend.user.routes import user_bp
from backend.admin.routes import admin_bp
from backend.lawyer.routes import lawyer_bp
from backend.judge.routes import judge_bp
from extensions import mysql
import MySQLdb
from datetime import datetime

app = Flask(__name__, template_folder="frontend/templates", static_folder="frontend/static")

# secret key for the flash message
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'nihla'
app.config['MYSQL_PASSWORD'] = 'EX6826679#'
app.config['MYSQL_DB'] = 'districtcourt'

# Initialize MySQL
mysql.init_app(app)

def create_database_and_tables():
    db = None
    try:
        db = MySQLdb.connect(host=app.config['MYSQL_HOST'], user=app.config['MYSQL_USER'],
                             passwd=app.config['MYSQL_PASSWORD'])
        cursor = db.cursor()
        
        # Create database if not exists
        cursor.execute("CREATE DATABASE IF NOT EXISTS districtcourt")
        cursor.execute("USE districtcourt")

        # Create events table with created_at and updated_at columns
        cursor.execute('''CREATE TABLE IF NOT EXISTS events (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            event_date DATE NOT NULL,
            event_time TIME NOT NULL,
            status VARCHAR(50) DEFAULT 'scheduled',
            judge_id INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )''')
        
        
        cursor.execute(''' CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            fullname VARCHAR(255) NOT NULL,
            username VARCHAR(100) NOT NULL UNIQUE,
            role ENUM('Admin', 'Judge', 'Lawyer', 'Public') NOT NULL,
            password VARCHAR(255) NOT NULL,
            address VARCHAR(255),
            contact VARCHAR(20),
            email VARCHAR(100),
            nic VARCHAR(20),
            gender ENUM('male', 'female', 'other'),
            description VARCHAR(255)    
        )''');
        
        
         # Create cases table
        cursor.execute('''CREATE TABLE IF NOT EXISTS cases (
            id INT AUTO_INCREMENT PRIMARY KEY,
            case_title VARCHAR(255) NOT NULL,
            case_number VARCHAR(100) NOT NULL UNIQUE,
            date DATE NOT NULL,
            case_type ENUM('Criminal', 'Civil', 'Family', 'Labor') NOT NULL,
            plaintiff_name VARCHAR(255) NOT NULL,
            defendant_name VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )''')
        
        # Create notification table
        cursor.execute(''' CREATE TABLE IF NOT EXISTS notifications (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            message TEXT NOT NULL,
            is_read BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
    )
''')
        
        # Create lawyer_notification table
        cursor.execute(''' CREATE TABLE IF NOT EXISTS lawyer_notification (
            id INT AUTO_INCREMENT PRIMARY KEY,
            lawyer_id INT,
            case_id INT,
            client_id INT,  -- New column to indicate the client (plaintiff or defendant)
            message TEXT,
            status ENUM('pending', 'accepted', 'rejected') DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lawyer_id) REFERENCES users(id),
            FOREIGN KEY (case_id) REFERENCES cases(id),
            FOREIGN KEY (client_id) REFERENCES users(id)
    )
''');



        db.commit()

    except MySQLdb.Error as err:
        print(f"Error: {err}")
    finally:
        if db:
            db.close()

@app.route('/')
def landing_page():
    return render_template('pre_index.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     session.clear()

#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']

#         # Connect to the database
#         conn = mysql.connection
#         cursor = conn.cursor(MySQLdb.cursors.DictCursor)

#         # Query to fetch user details by username
#         cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
#         user = cursor.fetchone()

#         if user and check_password_hash(user['password'], password):
#             # Set session variables
#             session['loggedin'] = True
#             session['user_id'] = user['id']  
#             session['username'] = user['username']
#             session['role'] = user['role']


#             # Redirect based on user role
#             if user['role'] == 'Admin':
#                 return redirect(url_for('admin.admin_index'))
#             elif user['role'] == 'Judge':
#                 return redirect(url_for('judge.judge_index'))
#             elif user['role'] == 'Lawyer':
#                 return redirect(url_for('lawyer.lawyer_index'))
#             elif user['role'] == 'Public':
#                 return redirect(url_for('user.user_index'))
#         else:
#             # Flash error message
#             flash('Invalid username or password', 'error')
#             return redirect(url_for('login'))
#     return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Connect to the database
        conn = mysql.connection
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)

        # Query to fetch user details by username
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            # Set session variables
            session['loggedin'] = True
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']

            # Redirect based on user role
            if user['role'] == 'Admin':
                return jsonify({'status': 'success', 'message': 'Login successful! Redirecting...', 'redirect_url': url_for('admin.admin_index')})
            elif user['role'] == 'Judge':
                return jsonify({'status': 'success', 'message': 'Login successful! Redirecting...', 'redirect_url': url_for('judge.judge_index')})
            elif user['role'] == 'Lawyer':
                return jsonify({'status': 'success', 'message': 'Login successful! Redirecting...', 'redirect_url': url_for('lawyer.lawyer_index')})
            elif user['role'] == 'Public':
                return jsonify({'status': 'success', 'message': 'Login successful! Redirecting...', 'redirect_url': url_for('user.user_index')})
        else:
            # Flash error message for invalid login
            return jsonify({'status': 'error', 'message': 'Invalid username or password'})

    return render_template('login.html')



@app.route('/profile')
def profile():
    if 'loggedin' in session:
        username = session['username']
        
        conn = mysql.connection
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT fullname, username, role, address, contact, email, nic, gender FROM users WHERE username = %s", (username,))
        profile_info = cursor.fetchone()

        if profile_info:
            return {
                'status': 'success',
                'data': profile_info
            }
        else:
            return {
                'status': 'error',
                'message': 'Profile not found'
            }
    return {
        'status': 'error',
        'message': 'User not logged in'
    }

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()  # Clear session data
    return jsonify({'status': 'success', 'message': 'Logged out successfully'})

# Register the blueprints
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(lawyer_bp, url_prefix='/lawyer')
app.register_blueprint(judge_bp, url_prefix='/judge')

if __name__ == '__main__':
    # Initialize the database before running the app
    create_database_and_tables()
    app.run(debug=True)
    