# from flask import Blueprint, render_template, request, flash, jsonify,session
# from extensions import mysql
# from werkzeug.security import generate_password_hash

# admin_bp = Blueprint('admin', __name__, template_folder="../../frontend/templates/admin")

# @admin_bp.route('/')
# def admin_index():
#     return render_template('index_admin.html')

# from flask import session, jsonify, redirect

# @admin_bp.route('/add_case', methods=['GET', 'POST'])
# def admin_addCase():
#     if request.method == 'POST':
#         case_title = request.form.get('caseTitle')
#         case_number = request.form.get('caseNumber')
#         date = request.form.get('date')
#         case_type = request.form.get('caseType')
#         plaintiff_name = request.form.get('plaintiffName')
#         defendant_name = request.form.get('defendantName')
#         description = request.form.get('description')

#         try:
#             cursor = mysql.connection.cursor()

#             # Insert the case into the database
#             cursor.execute('''
#                 INSERT INTO cases (case_title, case_number, date, case_type, plaintiff_name, defendant_name, description)
#                 VALUES (%s, %s, %s, %s, %s, %s, %s)
#             ''', (case_title, case_number, date, case_type, plaintiff_name, defendant_name, description))

#             # Get the ID of the plaintiff and defendant
#             cursor.execute('SELECT id FROM users WHERE username = %s', (plaintiff_name,))
#             plaintiff = cursor.fetchone()
            

#             cursor.execute('SELECT id FROM users WHERE username = %s', (defendant_name,))
#             defendant = cursor.fetchone()

#             # Create notifications for the plaintiff and defendant
#             if plaintiff:
#                 cursor.execute('''
#                     INSERT INTO notifications (user_id, message)
#                     VALUES (%s, %s)
#                 ''', (plaintiff[0], f'A new case has been registered against you: {case_title}'))

#             if defendant:
#                 cursor.execute('''
#                     INSERT INTO notifications (user_id, message)
#                     VALUES (%s, %s)
#                 ''', (defendant[0], f'You have been registered as the plaintiff in a new case: {case_title}'))

#             mysql.connection.commit()
#             cursor.close()
#             return jsonify({'status': 'success', 'message': 'Case added and notifications sent successfully!'})
#         except Exception as e:
#             return jsonify({'status': 'error', 'message': str(e)})

#     return render_template('add_case.html')



# # @admin_bp.route('/add_case', methods=['GET', 'POST'])
# # def admin_addCase():
# #     if request.method == 'POST':
# #         case_title = request.form.get('caseTitle')
# #         case_number = request.form.get('caseNumber')
# #         date = request.form.get('date')
# #         case_type = request.form.get('caseType')
# #         plaintiff_name = request.form.get('plaintiffName')
# #         defendant_name = request.form.get('defendantName')
# #         description = request.form.get('description')

# #         try:
# #             cursor = mysql.connection.cursor()

# #             # Insert the case into the database
# #             cursor.execute('''
# #                 INSERT INTO cases (case_title, case_number, date, case_type, plaintiff_name, defendant_name, description)
# #                 VALUES (%s, %s, %s, %s, %s, %s, %s)
# #             ''', (case_title, case_number, date, case_type, plaintiff_name, defendant_name, description))

# #             # Get the ID of the plaintiff and defendant, but only if they are users with the role "Public"
# #             cursor.execute('SELECT id FROM users WHERE username = %s AND role = "Public"', (plaintiff_name,))
# #             plaintiff = cursor.fetchone()

# #             cursor.execute('SELECT id FROM users WHERE username = %s AND role = "Public"', (defendant_name,))
# #             defendant = cursor.fetchone()

# #             # Create notifications for the plaintiff and defendant
# #             if plaintiff:
# #                 cursor.execute('''
# #                     INSERT INTO notifications (user_id, message)
# #                     VALUES (%s, %s)
# #                 ''', (plaintiff[0], f'You have been registered as the plaintiff in a new case: {case_title}'))

# #             if defendant:
# #                 cursor.execute('''
# #                     INSERT INTO notifications (user_id, message)
# #                     VALUES (%s, %s)
# #                 ''', (defendant[0], f'A new case has been registered against you: {case_title}'))

# #             mysql.connection.commit()
# #             cursor.close()
# #             return jsonify({'status': 'success', 'message': 'Case added and notifications sent successfully!'})
# #         except Exception as e:
# #             return jsonify({'status': 'error', 'message': str(e)})

# #     # Retrieve users with the role "Public" for display in the form
# #     try:
# #         cursor = mysql.connection.cursor()
# #         cursor.execute('SELECT username FROM users WHERE role = "Public"')
# #         public_users = [row[0] for row in cursor.fetchall()]
# #         cursor.close()
# #     except Exception as e:
# #         public_users = []
# #         print(f"Error fetching public users: {str(e)}")

# #     return render_template('add_case.html', public_users=public_users)


# @admin_bp.route('/add_user', methods=['GET', 'POST'])
# def admin_addUser():
#     if request.method == 'POST':
#         fullname = request.form.get('fullname')
#         username = request.form.get('username')
#         role = request.form.get('role')
#         password = request.form.get('password')
#         address = request.form.get('address')
#         contact = request.form.get('contact')
#         email = request.form.get('email')
#         nic = request.form.get('nic')
#         gender = request.form.get('gender')

#         try:
            
#             password_hash = generate_password_hash(password)
            
#             cursor = mysql.connection.cursor()
#             cursor.execute('''
#                 INSERT INTO users (fullname, username, role, password, address, contact, email, nic, gender)
#                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
#             ''', (fullname, username, role, password_hash, address, contact, email, nic, gender))
#             mysql.connection.commit()
#             cursor.close()
#             return jsonify({'status': 'success', 'message': 'User added successfully!'})
#         except Exception as e:
#             return jsonify({'status': 'error', 'message': str(e)})

#     return render_template('add_user.html')



# @admin_bp.route('/users_list')
# def admin_users_list():
#     role = request.args.get('role', '')  # Get role from query parameters
#     try:
#         cursor = mysql.connection.cursor()
#         if role:
#             cursor.execute('SELECT id, fullname, username, role, address, contact, email, nic, gender FROM users WHERE role = %s', (role,))
#         else:
#             cursor.execute('SELECT id, fullname, username, role, address, contact, email, nic, gender FROM users')
#         users = cursor.fetchall()
#         cursor.close()
#         return render_template('users_list.html', users=users)
#     except Exception as e:
#         return jsonify({'status': 'error', 'message': str(e)})


# @admin_bp.route('/users', methods=['GET'])
# def admin_users():
#     role = request.args.get('role', '')  # Get role from query parameters
#     try:
#         cursor = mysql.connection.cursor()
#         if role:
#             cursor.execute('SELECT id, fullname, username, role, address, contact, email, nic, gender FROM users WHERE role = %s', (role,))
#         else:
#             cursor.execute('SELECT id, fullname, username, role, address, contact, email, nic, gender FROM users')
#         users = cursor.fetchall()
#         cursor.close()

#         # Convert users to a list of dictionaries
#         user_list = [{'id': user[0], 'fullname': user[1], 'username': user[2], 'role': user[3]} for user in users]

#         return jsonify({'status': 'success', 'users': user_list})
#     except Exception as e:
#         return jsonify({'status': 'error', 'message': str(e)})


# @admin_bp.route('/public_users', methods=['GET'])
# def get_public_users():
#     try:
#         cursor = mysql.connection.cursor()
#         # Fetch only users with the role "Public"
#         cursor.execute('SELECT username FROM users WHERE role = "Public"')
#         public_users = cursor.fetchall()
#         cursor.close()

#         users_list = [{'username': user[0]} for user in public_users]
#         return jsonify({'status': 'success', 'users': users_list})
#     except Exception as e:
#         return jsonify({'status': 'error', 'message': str(e)})


# @admin_bp.route('/dashboard')
# def admin_dashboard():
#     return render_template('admin_dashboard.html')

# @admin_bp.route('/test-db')
# def test_db():
#     cur = mysql.connection.cursor()
#     cur.execute('''SELECT 1''')
#     results = cur.fetchall()
#     return f"DB Test Results: Success {results}"
























import os
import re  # email validation
from werkzeug.utils import secure_filename
from extensions import mysql
import MySQLdb
from datetime import timedelta,datetime
from werkzeug.security import generate_password_hash,check_password_hash
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, send_from_directory, session

admin_bp = Blueprint('admin', __name__, template_folder="../../frontend/templates/admin")

@admin_bp.route('/')
def admin_index():
    return render_template('index_admin.html')


# Specify the folder where uploaded files will be stored
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')  # Define upload path
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'png'}  # Adjust the file types as needed

# Make sure the uploads directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_bp.route('/upload_document', methods=['POST'])
def upload_document():
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(request.url)
    
    file = request.files['file']
    case_id = request.form.get('case_id')
    description = request.form.get('description')

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)  # Save the file to UPLOAD_FOLDER
        
        # Store only the relative file path in the database
        conn = mysql.connection
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO case_documents (case_id, document, description) 
            VALUES (%s, %s, %s)
        """, (case_id, file_path, description))
        
        conn.commit()
        cursor.close()
        flash('Document uploaded successfully', 'success')
        return redirect(url_for('admin.admin_index'))
    
    flash('File type not allowed', 'error')
    return redirect(url_for('admin.admin_index'))

@admin_bp.route('/view_document/<int:document_id>')
def view_document(document_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT document FROM case_documents WHERE id = %s", (document_id,))
    result = cursor.fetchone()
    cursor.close()

    if result:
        document_path = result[0]  # Get file path from database
        filename = os.path.basename(document_path)  # Extract the filename from the path
        return send_from_directory(directory=UPLOAD_FOLDER, path=filename, as_attachment=False)
    else:
        flash('Document not found', 'error')
        return redirect(url_for('admin.cases'))

@admin_bp.route('/download_document/<int:document_id>')
def download_document(document_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT document FROM case_documents WHERE id = %s", (document_id,))
    result = cursor.fetchone()
    cursor.close()

    if result:
        document_path = result[0]  # Get file path from database
        filename = os.path.basename(document_path)  # Extract the filename from the path
        return send_from_directory(directory=UPLOAD_FOLDER, path=filename, as_attachment=True, mimetype='application/pdf')
    else:
        flash('Document not found', 'error')
        return redirect(url_for('admin.cases'))



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




@admin_bp.route('/change_password', methods=['GET', 'POST'])
def change_password_admin():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_new_password = request.form['confirm_new_password']

        if not current_password or not new_password or not confirm_new_password:
            flash('All fields are required.', 'error')
            return render_template('change_password_admin.html')

        if new_password != confirm_new_password:
            flash('New passwords do not match.', 'error')
            return render_template('change_password_admin.html')

        user_id = session['user_id']
        conn = mysql.connection
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute("SELECT password FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], current_password):
            hashed_password = generate_password_hash(new_password)
            cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_password, user_id))
            conn.commit()
            flash('Password changed successfully.', 'success')
        else:
            flash('Current password is incorrect.', 'error')

        cursor.close()
        return render_template('change_password_admin.html')

    return render_template('change_password_admin.html')



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

        # Validate email format
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email):
            return jsonify({'status': 'error', 'message': 'Invalid email format. Please enter a valid email address.'})

        # Validate contact number is numeric and 10 digits
        if not contact.isdigit() or len(contact) != 10:
            return jsonify({'status': 'error', 'message': 'Contact number must be exactly 10 digits.'})

        try:
            cursor = mysql.connection.cursor()

            # Validate unique email
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return jsonify({'status': 'error', 'message': 'Email already exists. Please try again with new email'})

            # Validate unique username
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                return jsonify({'status': 'error', 'message': 'Username already exists.'})

            # Validate unique contact number
            cursor.execute("SELECT * FROM users WHERE contact = %s", (contact,))
            if cursor.fetchone():
                return jsonify({'status': 'error', 'message': 'Contact number already exists.'})

            # Validate unique NIC
            cursor.execute("SELECT * FROM users WHERE nic = %s", (nic,))
            if cursor.fetchone():
                return jsonify({'status': 'error', 'message': 'NIC number already exists.'})

            # Hash the password
            password_hash = generate_password_hash(password)

            # Insert new user if all validations pass
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
        
        # Fetch all user data and map column names to the results
        columns = [col[0] for col in cursor.description]
        users = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        cursor.close()
        return render_template('users_list.html', users=users)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@admin_bp.route('/get_user_details/<int:user_id>', methods=['GET'])
def get_user_details(user_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT fullname, username, address, contact, email, nic, gender FROM users WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            return jsonify({
                'status': 'success',
                'fullname': user[0],
                'username': user[1],
                'address': user[2],
                'contact': user[3],
                'email': user[4],
                'nic': user[5],
                'gender': user[6]
            })
        else:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500




@admin_bp.route('/manage_users', methods=['GET'])
def manage_users():
    try:
        cursor = mysql.connection.cursor()
        role_filter = request.args.get('role', None)
        
        # Retrieve users with an optional role filter
        if role_filter:
            cursor.execute("SELECT id, fullname, username, role, address FROM users WHERE role = %s", (role_filter,))
        else:
            cursor.execute("SELECT id, fullname, username, role, address FROM users")
        
        users = cursor.fetchall()
        cursor.close()

        # Convert query result to a list of dictionaries for template use
        users_list = [
            {
                'id': user[0],
                'fullname': user[1],
                'username': user[2],
                'role': user[3],
                'address': user[4]
            }
            for user in users
        ]

        return render_template('manage_user.html', users=users_list)

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})




@admin_bp.route('/edit_user', methods=['GET', 'POST'])
def edit_user():
    user_id = request.args.get('id')
    
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID is required'})
    
    # Fetch user details to prefill the form
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, fullname, username, role, address, contact, email, nic, gender FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            user_data = {
                'id': user[0],
                'fullname': user[1],
                'username': user[2],
                'role': user[3],
                'address': user[4],
                'contact': user[5],
                'email': user[6],
                'nic': user[7],
                'gender': user[8]
            }

            message = None
            status = None
            button_class = 'btn-primary'  # Default button class

            # Handle POST request for updating user data
            if request.method == 'POST':
                fullname = request.form.get('fullname')
                username = request.form.get('username')
                role = request.form.get('role')
                address = request.form.get('address')
                contact = request.form.get('contact')
                email = request.form.get('email')
                nic = request.form.get('nic')
                gender = request.form.get('gender')

                # Validate email format
                email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
                if not re.match(email_regex, email):
                    message = 'Invalid email format'
                    status = 'error'
                    button_class = 'btn-danger'
                # Validate contact number
                elif not contact.isdigit() or len(contact) != 10:
                    message = 'Contact number must be exactly 10 digits'
                    status = 'error'
                    button_class = 'btn-danger'
                else:
                    try:
                        cursor = mysql.connection.cursor()
                        cursor.execute('''UPDATE users
                                          SET fullname = %s, username = %s, role = %s, address = %s, contact = %s, email = %s, nic = %s, gender = %s
                                          WHERE id = %s''', 
                                          (fullname, username, role, address, contact, email, nic, gender, user_id))
                        mysql.connection.commit()
                        cursor.close()
                        message = 'User updated successfully!'
                        status = 'success'
                        button_class = 'btn-success'
                    except Exception as e:
                        message = f'Error: {str(e)}'
                        status = 'error'
                        button_class = 'btn-danger'

            return render_template('edit_user.html', user=user_data, message=message, status=status, button_class=button_class)
        else:
            return jsonify({'status': 'error', 'message': 'User not found'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})





@admin_bp.route('/delete_user', methods=['GET'])
def delete_user():
    user_id = request.args.get('id')
    
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID is required'})
    
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        mysql.connection.commit()
        cursor.close()
        return jsonify({'status': 'success', 'message': 'User deleted successfully!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})




@admin_bp.route('/public_users', methods=['GET'])
def get_public_users():
    try:
        cursor = mysql.connection.cursor()
        # Fetch only users with the role "Public"
        cursor.execute('SELECT username FROM users WHERE role = "Public"')
        public_users = cursor.fetchall()
        cursor.close()

        users_list = [{'username': user[0]} for user in public_users]
        return jsonify({'status': 'success', 'users': users_list})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})



@admin_bp.route('/all_cases', methods=['GET'])
def cases():
    try:
        cursor = mysql.connection.cursor()

        # Retrieve case information
        cursor.execute('''
            SELECT 
                c.id AS case_id,
                c.plaintiff_name,
                c.defendant_name
            FROM cases c
        ''')
        cases = cursor.fetchall()

        enriched_cases = []

        for case in cases:
            case_id, plaintiff_username, defendant_username = case

            # Lookup user IDs for plaintiff and defendant based on usernames
            cursor.execute('SELECT id FROM users WHERE username = %s AND role = "Public"', (plaintiff_username,))
            plaintiff_client_id = cursor.fetchone()
            plaintiff_client_id = plaintiff_client_id[0] if plaintiff_client_id else None

            cursor.execute('SELECT id FROM users WHERE username = %s AND role = "Public"', (defendant_username,))
            defendant_client_id = cursor.fetchone()
            defendant_client_id = defendant_client_id[0] if defendant_client_id else None

            # Print the mapped client IDs to verify
            print(f"Plaintiff Client ID for username {plaintiff_username}: {plaintiff_client_id}")
            print(f"Defendant Client ID for username {defendant_username}: {defendant_client_id}")

            # Fetch Plaintiff's Lawyer
            cursor.execute('''
                SELECT u.fullname 
                FROM lawyer_notification ln 
                JOIN users u ON ln.lawyer_id = u.id 
                WHERE ln.case_id = %s
                AND ln.client_id = %s
                AND ln.status = 'accepted'
                AND u.role = 'Lawyer'
                LIMIT 1
            ''', (case_id, plaintiff_client_id))
            plaintiff_lawyer = cursor.fetchone()
            plaintiff_lawyer = plaintiff_lawyer[0] if plaintiff_lawyer else None

            # Fetch Defendant's Lawyer
            cursor.execute('''
                SELECT u.fullname 
                FROM lawyer_notification ln 
                JOIN users u ON ln.lawyer_id = u.id 
                WHERE ln.case_id = %s
                AND ln.client_id = %s
                AND ln.status = 'accepted'
                AND u.role = 'Lawyer'
                LIMIT 1
            ''', (case_id, defendant_client_id))
            defendant_lawyer = cursor.fetchone()
            defendant_lawyer = defendant_lawyer[0] if defendant_lawyer else None

            # Append enriched case info
            enriched_cases.append((case_id, plaintiff_username, plaintiff_lawyer, defendant_username, defendant_lawyer))

        # Display enriched cases in terminal
        print("Enriched Cases with Lawyers:")
        for case in enriched_cases:
            print(case)

        cursor.close()

        # Render template with enriched cases
        return render_template('all_cases.html', cases=enriched_cases)
    except Exception as e:
        print("Error:", e)  # Print error details in terminal
        return jsonify({'status': 'error', 'message': str(e)})
    
    


@admin_bp.route('/get_cases', methods=['GET'])
def get_cases():
    """
    Fetch all cases from the database and return them as JSON.
    """
    try:
        cursor = mysql.connection.cursor()
        query = '''
        SELECT case_number, case_type, case_title FROM cases
        '''
        cursor.execute(query)
        cases = cursor.fetchall()
        cursor.close()

        # Log the fetched cases to the terminal
        print("Fetched cases from the database:", cases)

        # Format the data as a list of dictionaries
        cases_list = [{'case_number': row[0], 'case_type': row[1], 'case_title': row[2]} for row in cases]
        return jsonify({'status': 'success', 'data': cases_list})
    except Exception as e:
        print("Error fetching cases:", str(e))
        return jsonify({'status': 'error', 'message': str(e)})
    



@admin_bp.route('/add_hearing', methods=['GET', 'POST'])
def add_hearing():
    if request.method == 'POST':
        # Fetch the form data
        case_number = request.form.get('case_number')
        hearing_date = request.form.get('hearing_date')
        hearing_description = request.form.get('hearing_description')
        highlights = request.form.get('highlights')

        if not case_number:
            return jsonify({'status': 'error', 'message': 'Case number is missing.'})

        try:
            cursor = mysql.connection.cursor()

            # Fetch the case_id using case_number
            query = 'SELECT id FROM cases WHERE case_number = %s'
            cursor.execute(query, (case_number,))
            result = cursor.fetchone()

            if not result:
                return jsonify({'status': 'error', 'message': 'Case number does not exist.'})

            case_id = result[0]  # Extract case_id from the query result

            # Insert the new hearing into the case_hearings table
            insert_query = '''
            INSERT INTO case_hearings (case_id, hearing_date, hearing_description, highlights)
            VALUES (%s, %s, %s, %s)
            '''
            cursor.execute(insert_query, (case_id, hearing_date, hearing_description, highlights))
            mysql.connection.commit()

            cursor.close()

            # Return a success message to be displayed on the form
            return jsonify({'status': 'success', 'message': 'Hearing added successfully.'})
        except Exception as e:
            print("Error adding hearing:", str(e))
            return jsonify({'status': 'error', 'message': str(e)})

    # Render the form for GET requests
    return render_template('add_hearing.html', message=None)



@admin_bp.route('/hearings', methods=['GET'])
def admin_hearings_list():
    # Get case_number from the query parameters
    case_number = request.args.get('case_number', '')  # Adjusted to use 'case_number'

    try:
        cursor = mysql.connection.cursor()

        # If case_number is provided, filter the hearings
        if case_number:
            query = '''
            SELECT ch.id, ch.case_id, c.case_number, ch.hearing_date, ch.hearing_description, ch.highlights, ch.created_at
            FROM case_hearings ch
            JOIN cases c ON ch.case_id = c.id
            WHERE c.case_number = %s
            '''
            cursor.execute(query, (case_number,))
        else:
            query = '''
            SELECT ch.id, ch.case_id, c.case_number, ch.hearing_date, ch.hearing_description, ch.highlights, ch.created_at
            FROM case_hearings ch
            JOIN cases c ON ch.case_id = c.id
            '''
            cursor.execute(query)
        
        # Fetch all hearing data
        columns = [col[0] for col in cursor.description]
        hearings = [dict(zip(columns, row)) for row in cursor.fetchall()]

        cursor.close()
        return render_template('hearings.html', hearings=hearings)
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})



@admin_bp.route('/manage_hearings', methods=['GET'])
def admin_manage_hearings_list():
    case_number = request.args.get('case_number', '')

    try:
        cursor = mysql.connection.cursor()

        if case_number:
            query = '''
            SELECT ch.id, ch.case_id, ch.hearing_date, ch.hearing_description, 
                   ch.highlights, ch.created_at, c.case_number
            FROM case_hearings ch
            JOIN cases c ON ch.case_id = c.id
            WHERE c.case_number = %s
            '''
            cursor.execute(query, (case_number,))
        else:
            query = '''
            SELECT ch.id, ch.case_id, ch.hearing_date, ch.hearing_description, 
                   ch.highlights, ch.created_at, c.case_number
            FROM case_hearings ch
            JOIN cases c ON ch.case_id = c.id
            '''
            cursor.execute(query)

        # Fetch all hearing data
        columns = [col[0] for col in cursor.description]
        hearings = [dict(zip(columns, row)) for row in cursor.fetchall()]

        cursor.close()
        return render_template('manage_hearings.html', hearings=hearings)

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# Route to update a hearing
@admin_bp.route('/update_hearing', methods=['POST'])
def update_hearing():
    try:
        hearing_id = request.form['id']
        hearing_date = request.form['hearing_date']
        hearing_description = request.form['hearing_description']
        highlights = request.form['highlights']

        cursor = mysql.connection.cursor()
        query = '''
        UPDATE case_hearings
        SET hearing_date = %s, hearing_description = %s, highlights = %s
        WHERE id = %s
        '''
        cursor.execute(query, (hearing_date, hearing_description, highlights, hearing_id))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('admin.admin_manage_hearings_list'))

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# Route to delete a hearing
@admin_bp.route('/delete_hearing/<int:hearing_id>', methods=['POST'])
def delete_hearing(hearing_id):
    try:
        cursor = mysql.connection.cursor()
        query = 'DELETE FROM case_hearings WHERE id = %s'
        cursor.execute(query, (hearing_id,))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('admin.admin_manage_hearings_list'))

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


    
@admin_bp.route('/case_documents', methods=['GET'])
def case_documents():
    try:
        cursor = mysql.connection.cursor()
        # Fetch all documents
        cursor.execute('''
            SELECT id, case_id, description, document 
            FROM case_documents
        ''')
        documents = cursor.fetchall()
        cursor.close()

        # Render the template with the documents data
        return render_template('case_documents.html', documents=documents)
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})




@admin_bp.route('/dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@admin_bp.route('/admin_calendar')
def admin_calendar():
    return render_template('admin_calendar.html')

# Render scheduled events page
@admin_bp.route('/scheduled_events_admin')
def scheduled_events_admin():
    return render_template('scheduled_event_admin.html')

# Fetch or create events
@admin_bp.route('/api/events_admin', methods=['GET', 'POST'])
def events_admin():
    db = mysql.connection
    cursor = db.cursor()
    if request.method == 'GET':
        cursor.execute("SELECT * FROM events")
        events = cursor.fetchall()
        # Convert the results to a list of dictionaries and handle timedelta
        columns = [desc[0] for desc in cursor.description]
        events = [dict(zip(columns, row)) for row in events]
        for event in events:
            for key, value in event.items():
                if isinstance(value, timedelta):
                    event[key] = str(value)
        return jsonify(events)
    
    elif request.method == 'POST':
        data = request.json
        title = data.get('title')
        event_date = data.get('event_date')
        event_time = data.get('event_time')
        status = data.get('status', 'scheduled')
        judge_id = data.get('judge_id')
        created_at = updated_at = datetime.now()  # Set timestamps
        
        try:
            cursor.execute(
                "INSERT INTO events (title, event_date, event_time, status, judge_id, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (title, event_date, event_time, status, judge_id, created_at, updated_at)
            )
            db.commit()
            return jsonify({'message': 'Event created successfully'}), 201
        except Exception as e:
            db.rollback()
            return jsonify({'error': str(e)}), 500

# Edit an event
@admin_bp.route('/api/editevents_admin/<int:event_id>', methods=['PUT'])
def edit_event_admin(event_id):
    db = mysql.connection
    cursor = db.cursor()
    data = request.json
    title = data.get('title')
    event_date = data.get('event_date')
    event_time = data.get('event_time')
    
    status = 'scheduled'
    updated_at = datetime.now()  # Update the timestamp
    
    try:
        cursor.execute(
            "UPDATE events SET title = %s, event_date = %s, event_time = %s, status = %s, updated_at = %s WHERE id = %s",
            (title, event_date, event_time, status, updated_at, event_id)
        )
        db.commit()
        return jsonify({'message': 'Event updated successfully'})
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

# Update event status
@admin_bp.route('/api/events_admin/<int:event_id>', methods=['PUT'])
def update_event_admin(event_id):
    db = mysql.connection
    cursor = db.cursor()
    data = request.json
    status = data.get('status')
    updated_at = datetime.now()  # Update the timestamp
    
    try:
        cursor.execute("UPDATE events SET status = %s, updated_at = %s WHERE id = %s", (status, updated_at, event_id))
        db.commit()
        return jsonify({'message': 'Event updated successfully'})
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500


