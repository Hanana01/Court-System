
from flask import Blueprint, render_template, request, flash, jsonify
from extensions import mysql
from werkzeug.security import generate_password_hash

admin_bp = Blueprint('admin', __name__, template_folder="../../frontend/templates/admin")

@admin_bp.route('/')
def admin_index():
    return render_template('index_admin.html')


@admin_bp.route('/add_case', methods=['GET', 'POST'])
def admin_addCase():
    if request.method == 'POST':
        case_title = request.form.get('caseTitle')
        case_number = request.form.get('caseNumber')
        date = request.form.get('date')
        case_type = request.form.get('caseType')
        plaintiff_name = request.form.get('plaintiffName')
        defendant_name = request.form.get('defendantName')
        description = request.form.get('description')

        try:
            cursor = mysql.connection.cursor()
            cursor.execute('''
                INSERT INTO cases (case_title, case_number, date, case_type, plaintiff_name, defendant_name, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (case_title, case_number, date, case_type, plaintiff_name, defendant_name, description))
            mysql.connection.commit()
            cursor.close()
            return jsonify({'status': 'success', 'message': 'Case added successfully!'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})

    return render_template('add_case.html')


@admin_bp.route('/add_user', methods=['GET', 'POST'])
def admin_addUser():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        username = request.form.get('username')
        role = request.form.get('role')
        password = request.form.get('password')
        address = request.form.get('address')
        contact = request.form.get('contact')
        email = request.form.get('email')
        nic = request.form.get('nic')
        gender = request.form.get('gender')

        try:
            
            password_hash = generate_password_hash(password)
            
            cursor = mysql.connection.cursor()
            cursor.execute('''
                INSERT INTO users (fullname, username, role, password, address, contact, email, nic, gender)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (fullname, username, role, password_hash, address, contact, email, nic, gender))
            mysql.connection.commit()
            cursor.close()
            return jsonify({'status': 'success', 'message': 'User added successfully!'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})

    return render_template('add_user.html')



@admin_bp.route('/users_list')
def admin_users_list():
    role = request.args.get('role', '')  # Get role from query parameters
    try:
        cursor = mysql.connection.cursor()
        if role:
            cursor.execute('SELECT id, fullname, username, role, address, contact, email, nic, gender FROM users WHERE role = %s', (role,))
        else:
            cursor.execute('SELECT id, fullname, username, role, address, contact, email, nic, gender FROM users')
        users = cursor.fetchall()
        cursor.close()
        return render_template('users_list.html', users=users)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@admin_bp.route('/users', methods=['GET'])
def admin_users():
    role = request.args.get('role', '')  # Get role from query parameters
    try:
        cursor = mysql.connection.cursor()
        if role:
            cursor.execute('SELECT id, fullname, username, role, address, contact, email, nic, gender FROM users WHERE role = %s', (role,))
        else:
            cursor.execute('SELECT id, fullname, username, role, address, contact, email, nic, gender FROM users')
        users = cursor.fetchall()
        cursor.close()

        # Convert users to a list of dictionaries
        user_list = [{'id': user[0], 'fullname': user[1], 'username': user[2], 'role': user[3]} for user in users]

        return jsonify({'status': 'success', 'users': user_list})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


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
