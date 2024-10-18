from flask import Blueprint, render_template, request, flash, jsonify,session
from extensions import mysql
from werkzeug.security import generate_password_hash

admin_bp = Blueprint('admin', __name__, template_folder="../../frontend/templates/admin")

@admin_bp.route('/')
def admin_index():
    return render_template('index_admin.html')

from flask import session, jsonify, redirect

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

            # Insert the case into the database
            cursor.execute('''
                INSERT INTO cases (case_title, case_number, date, case_type, plaintiff_name, defendant_name, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (case_title, case_number, date, case_type, plaintiff_name, defendant_name, description))

            # Get the ID of the plaintiff and defendant
            cursor.execute('SELECT id FROM users WHERE username = %s', (plaintiff_name,))
            plaintiff = cursor.fetchone()
            

            cursor.execute('SELECT id FROM users WHERE username = %s', (defendant_name,))
            defendant = cursor.fetchone()

            # Create notifications for the plaintiff and defendant
            if plaintiff:
                cursor.execute('''
                    INSERT INTO notifications (user_id, message)
                    VALUES (%s, %s)
                ''', (plaintiff[0], f'A new case has been registered against you: {case_title}'))

            if defendant:
                cursor.execute('''
                    INSERT INTO notifications (user_id, message)
                    VALUES (%s, %s)
                ''', (defendant[0], f'You have been registered as the plaintiff in a new case: {case_title}'))

            mysql.connection.commit()
            cursor.close()
            return jsonify({'status': 'success', 'message': 'Case added and notifications sent successfully!'})
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
        description = request.form.get('description')

        try:
            
            password_hash = generate_password_hash(password)
            
            cursor = mysql.connection.cursor()
            cursor.execute('''
                INSERT INTO users (fullname, username, role, password, address, contact, email, nic, gender, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (fullname, username, role, password_hash, address, contact, email, nic, gender, description))
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

@admin_bp.route('/view_user/<int:id>', methods=['GET'])
def admin_view_user(id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id, fullname, username, role, address, contact, email, nic, gender, description FROM users WHERE id = %s', (id,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            # Convert user data to dictionary
            user_data = {
                'id': user[0],
                'fullname': user[1],
                'username': user[2],
                'role': user[3],
                'address': user[4],
                'contact': user[5],
                'email': user[6],
                'nic': user[7],
                'gender': user[8],
                'description': user[9]
            }
            return jsonify({'status': 'success', 'user': user_data})
        else:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@admin_bp.route('/users', methods=['GET'])
def admin_users():
    role = request.args.get('role', '')  # Get role from query parameters
    try:
        cursor = mysql.connection.cursor()
        if role:
            cursor.execute('SELECT id, fullname, username, role, address, contact, email, nic, gender, description FROM users WHERE role = %s', (role,))
        else:
            cursor.execute('SELECT id, fullname, username, role, address, contact, email, nic, gender, description FROM users')
        users = cursor.fetchall()
        cursor.close()

        # Convert users to a list of dictionaries
        user_list = [{'id': user[0], 'fullname': user[1], 'username': user[2], 'role': user[3]} for user in users]

        return jsonify({'status': 'success', 'users': user_list})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})



@admin_bp.route('/dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@admin_bp.route('/calendar')
def admin_calendar():
    return render_template('admin_calendar.html')




