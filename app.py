from flask import Flask
from backend.user.routes import user_bp
from backend.admin.routes import admin_bp
from backend.lawyer.routes import lawyer_bp
from backend.judge.routes import judge_bp
from extensions import mysql

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

# Register the blueprints
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(lawyer_bp, url_prefix='/lawyer')
app.register_blueprint(judge_bp, url_prefix='/judge')

if __name__ == '__main__':
    app.run(debug=True)
