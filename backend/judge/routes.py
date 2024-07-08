
from flask import Blueprint, render_template

judge_bp = Blueprint('judge', __name__, template_folder="../../frontend/templates/judge")

@judge_bp.route('/')
def judge_index():
    return render_template('index_judge.html')
