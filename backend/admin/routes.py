from flask import Blueprint, render_template
from extensions import mysql

admin_bp = Blueprint('admin', __name__, template_folder="../../frontend/templates/admin")

@admin_bp.route('/')
def admin_index():
    return render_template('index_admin.html')

@admin_bp.route('/add_case')
def admin_addCase():
    return render_template('add_case.html')

@admin_bp.route('/add_user')
def admin_addUser():
    return render_template('add_user.html')

@admin_bp.route('/add_lawyer')
def admin_addLawyer():
    return render_template('add_lawyer.html')

@admin_bp.route('/add_judge')
def admin_addJudge():
    return render_template('add_judge.html')

@admin_bp.route('/dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@admin_bp.route('/test-db')
def test_db():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT 1''')
    results = cur.fetchall()
    return f"DB Test Results: Success {results}"