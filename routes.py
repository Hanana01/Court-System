from flask import render_template, Blueprint

routes_bp = Blueprint('routes', __name__, template_folder="frontend/templates", static_folder="frontend/static")

@routes_bp.route('/')
def dashboard():
    return render_template('dashboard.html')
