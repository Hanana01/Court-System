from flask import Flask, render_template, Blueprint

# Create a blueprint for the routes
routes_bp = Blueprint('routes', __name__, template_folder="frontend/templates", static_folder="frontend/static")

@routes_bp.route('/index')
def dashboard():
    return render_template('index.html')

@routes_bp.route('/index_public')
def dashboard_public():
    return render_template('index_public.html')

@routes_bp.route('/index_lawyer')
def dashboard_lawyer():
    return render_template('index_lawyer.html')

@routes_bp.route('/index_judge')
def dashboard_judge():
    return render_template('index_judge.html')

# Initialize the Flask app
app = Flask(__name__, template_folder="frontend/templates", static_folder="frontend/static")

# Set the secret key for the flash message
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Register the blueprint
app.register_blueprint(routes_bp)

@app.route('/login')
def login():
    return render_template('login.html')

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

@app.route('/cases')
def cases():
    return render_template('cases.html')

@app.route('/user')
def user():
    return render_template('user.html')

@app.route('/add_lawyer')
def addLawyer():
    return render_template('addLawyer.html')

@app.route('/add_judge')
def addJudge():
    return render_template('addJudge.html')

@app.route('/')
def landpage():
    return render_template('landingPage.html')

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
