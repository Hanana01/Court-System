from flask import Flask
from routes import routes_bp
from db_operations import db

from registration_tasks import registration_tasks_bp

app = Flask(__name__, template_folder="templates", static_folder="static")

# Set the secret key for the flashmessage
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Register blueprints
app.register_blueprint(routes_bp)
app.register_blueprint(registration_tasks_bp)

if __name__ == '__main__':
    app.run(debug=True)
