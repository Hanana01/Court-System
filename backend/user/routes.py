
from flask import Blueprint, render_template

user_bp = Blueprint('user', __name__, template_folder="../../frontend/templates/user")

@user_bp.route('/')
def user_index():
    return render_template('index_user.html')
