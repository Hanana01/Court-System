from flask import Flask, render_template, Blueprint

# Create a blueprint for the routes
routes_bp = Blueprint('routes', __name__, template_folder="frontend/templates", static_folder="frontend/static")

@routes_bp.route('/index_admin')
def dashboard():
    return render_template('index_admin.html')

# Initialize the Flask app
app = Flask(__name__, template_folder="frontend/templates", static_folder="frontend/static")

# Set the secret key for the flash message
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Register the blueprint
app.register_blueprint(routes_bp)

# Define the other routes
@app.route('/navbar')
def navbar():
    return render_template('navbar.html')

@app.route('/unfiled')
def unfiled():
    return render_template('unfiled.html')

@app.route('/sidebar')
def sidebar():
    return render_template('sidebar.html')

@app.route('/index_admin/add_case')
def cases():
    return render_template('add_case.html')

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
