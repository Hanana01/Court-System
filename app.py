from flask import Flask
from routes import routes_bp


app = Flask(__name__, template_folder="frontend/templates", static_folder="frontend/static")

# Set the secret key for the flashmessage
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Register blueprints
app.register_blueprint(routes_bp)


if __name__ == '__main__':
    app.run(debug=True)

