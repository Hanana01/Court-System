from flask import Flask, render_template
from backend.user.routes import user_bp
from backend.admin.routes import admin_bp
from backend.lawyer.routes import lawyer_bp
from backend.judge.routes import judge_bp
from extensions import mysql
import MySQLdb
from datetime import datetime

app = Flask(__name__, template_folder="frontend/templates", static_folder="frontend/static")

# Set the secret key for the flash message
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

        # Create `events` table with created_at and updated_at columns
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

        # Add other table creation logic here as needed
        db.commit()

    except MySQLdb.Error as err:
        print(f"Error: {err}")
    finally:
        if db:
            db.close()

@app.route('/')
def landing_page():
    return render_template('landingPage.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('registration.html')

# Register the blueprints
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(lawyer_bp, url_prefix='/lawyer')
app.register_blueprint(judge_bp, url_prefix='/judge')

if __name__ == '__main__':
    # Initialize the database before running the app
    create_database_and_tables()
    app.run(debug=True)
