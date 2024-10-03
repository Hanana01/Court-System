
from flask import Blueprint, render_template

lawyer_bp = Blueprint('lawyer', __name__, template_folder="../../frontend/templates/lawyer")

@lawyer_bp.route('/')
def lawyer_index():
    return render_template('index_lawyer.html')
