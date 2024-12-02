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



#user list route
@admin_bp.route('/users_list', methods=['GET'])
def admin_users_list():
    try:
        cursor = mysql.connection.cursor()
        username_filter = request.args.get('username', None)
        
        # Retrieve users with an optional username filter
        if username_filter:
            cursor.execute("SELECT id, fullname, username, role, address, email FROM users WHERE username LIKE %s", ('%' + username_filter + '%',))
        else:
            cursor.execute("SELECT id, fullname, username, role, address, email FROM users")
        
        users = cursor.fetchall()
        cursor.close()

        # Convert query result to a list of dictionaries for template use
        users_list = [
            {
                'id': user[0],
                'fullname': user[1],
                'username': user[2],
                'role': user[3],
                'address': user[4],
                'email': user[5]
            }
            for user in users
        ]

        return render_template('users_list.html', users=users_list)

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})



#get particular user route
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



#edit user route
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




#delete user route
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



# route for fetching all public users
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
    

# route for fetching all judges
@admin_bp.route('/get_judges', methods=['GET'])
def get_judges():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT fullname FROM users WHERE role = "Judge"')
        public_users = cursor.fetchall()
        cursor.close()

        users_list = [{'fullname': user[0]} for user in public_users]
        return jsonify({'status': 'success', 'users': users_list})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


# fetching for all cases
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
    




@admin_bp.route('/view_case/<int:case_id>', methods=['GET'])
def view_case(case_id):
    try:
        cursor = mysql.connection.cursor()

        # Retrieve detailed case information including case_number
        cursor.execute('''
            SELECT 
                c.id AS case_id, 
                c.case_number,  -- Include the case number column
                c.case_title, 
                c.description, 
                c.case_type, 
                c.date, 
                c.plaintiff_name, 
                c.defendant_name
            FROM cases c
            WHERE c.id = %s
        ''', (case_id,))
        case = cursor.fetchone()

        if not case:
            return jsonify({'status': 'error', 'message': 'Case not found'})

        # Retrieve the plaintiff and defendant's lawyer (if any)
        plaintiff_lawyer = get_lawyer_for_case(cursor, case_id, case[5], 'plaintiff')
        defendant_lawyer = get_lawyer_for_case(cursor, case_id, case[6], 'defendant')

        # Return case details to the modal, including the case number
        return jsonify({
            'case_id': case[0],
            'case_number': case[1],  # Include the case number
            'case_title': case[2],
            'description': case[3],
            'case_type': case[4],
            'date': case[5],
            'plaintiff_name': case[6],
            'defendant_name': case[7],
            'plaintiff_lawyer': plaintiff_lawyer,
            'defendant_lawyer': defendant_lawyer
        })
    except Exception as e:
        print("Error:", e)
        return jsonify({'status': 'error', 'message': str(e)})


def get_lawyer_for_case(cursor, case_id, client_name, client_type):
    # Get client ID by username (assuming client_name is the username here)
    cursor.execute('SELECT id FROM users WHERE username = %s AND role = "Public"', (client_name,))
    client_id = cursor.fetchone()
    client_id = client_id[0] if client_id else None
    
    if not client_id:
        return 'N/A'  # No client found, return N/A

    # Fetch the lawyer associated with this client for the case
    cursor.execute('''
        SELECT u.fullname 
        FROM lawyer_notification ln
        JOIN users u ON ln.lawyer_id = u.id
        WHERE ln.case_id = %s AND ln.client_id = %s AND ln.status = 'accepted'
        AND u.role = 'Lawyer'
        LIMIT 1
    ''', (case_id, client_id))
    lawyer = cursor.fetchone()

    return lawyer[0] if lawyer else 'N/A'




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

        # Log the fetched case numbers to the terminal
        print("Fetched cases from the database:")
        for case in cases:
            print(f"Case Number: {case[0]} - Title: {case[2]}")

        # Format the data as a list of dictionaries
        cases_list = [{'case_number': row[0], 'case_type': row[1], 'case_title': row[2]} for row in cases]
        return jsonify({'status': 'success', 'data': cases_list})
    except Exception as e:
        print("Error fetching cases:", str(e))
        return jsonify({'status': 'error', 'message': str(e)})




@admin_bp.route('/add_hearing', methods=['POST'])
def add_hearing():
    try:
        # Fetch the JSON data from the request body
        data = request.get_json()
        print("Received data:", data)

        event_id = data.get('event_id')
        judge = data.get('judge')
        description = data.get('description')
        highlights = data.get('highlights')

        # Validate the incoming data
        if not event_id or not judge or not description:
            return jsonify({'status': 'error', 'message': 'Missing required fields.'}), 400

        # Connect to the database
        cursor = mysql.connection.cursor()

        # Verify if the event exists
        cursor.execute("SELECT id, case_id FROM events WHERE id = %s", (event_id,))
        event_result = cursor.fetchone()
        if not event_result:
            return jsonify({'status': 'error', 'message': 'Invalid event ID.'}), 404

        event_id_db, case_id_db = event_result

        # Insert the new hearing into the database
        query = '''
        INSERT INTO case_hearings (case_id, event_id, judge, hearing_description, highlights, created_at)
        VALUES (%s, %s, %s, %s, %s, NOW())
        '''
        cursor.execute(query, (case_id_db, event_id_db, judge, description, highlights))
        mysql.connection.commit()

        cursor.close()
        return jsonify({'status': 'success', 'message': 'Hearing added successfully.'}), 201

    except Exception as e:
        print("Error adding hearing:", e)
        return jsonify({'status': 'error', 'message': str(e)}), 500




@admin_bp.route('/admin/get_case_details', methods=['GET'])
def get_case_details():
    """
    Fetch details of a specific case based on the provided event_id.
    """
    event_id = request.args.get('event_id')

    if not event_id:
        return jsonify({'status': 'error', 'message': 'Event ID is required'}), 400

    try:
        cursor = mysql.connection.cursor()
        query = """
            SELECT c.case_number, c.case_type, c.case_title
            FROM cases c
            JOIN events e ON e.case_id = c.id
            WHERE e.id = %s
        """
        cursor.execute(query, (event_id,))
        case_details = cursor.fetchone()
        cursor.close()

        if case_details:
            return jsonify({
                'status': 'success',
                'data': {
                    'case_number': case_details[0],
                    'case_type': case_details[1],
                    'case_title': case_details[2]
                }
            })
        else:
            return jsonify({'status': 'error', 'message': 'No case details found for the given event ID'}), 404
    except Exception as e:
        print("Error fetching case details:", str(e))
        return jsonify({'status': 'error', 'message': str(e)})







@admin_bp.route('/hearings', methods=['GET'])
def admin_hearings_list():
    # Get case_number from the query parameters
    case_number = request.args.get('case_number', '')  # Adjusted to use 'case_number'

    try:
        cursor = mysql.connection.cursor()

        # If case_number is provided, filter the hearings
        if case_number:
            query = '''
            SELECT ch.id, ch.case_id, c.case_number, ch.hearing_description, ch.highlights, e.event_date AS hearing_date, ch.created_at
            FROM case_hearings ch
            JOIN cases c ON ch.case_id = c.id
            JOIN events e ON c.id = e.case_id  -- Assuming there's a case_id column in the events table
            WHERE c.case_number = %s
            '''
            cursor.execute(query, (case_number,))
        else:
            query = '''
            SELECT ch.id, ch.case_id, c.case_number, ch.hearing_description, ch.highlights, e.event_date AS hearing_date, ch.created_at
            FROM case_hearings ch
            JOIN cases c ON ch.case_id = c.id
            JOIN events e ON c.id = e.case_id  -- Assuming there's a case_id column in the events table
            '''
            cursor.execute(query)
        
        # Fetch all hearing data
        columns = [col[0] for col in cursor.description]
        hearings = [dict(zip(columns, row)) for row in cursor.fetchall()]

        cursor.close()
        return render_template('hearings.html', hearings=hearings)
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})



# # Route to list and manage hearings
# @admin_bp.route('/manage_hearings', methods=['GET'])
# def admin_manage_hearings_list():
#     case_number = request.args.get('case_number', '')

#     try:
#         cursor = mysql.connection.cursor()

#         if case_number:
#             query = '''
#             SELECT ch.id, ch.case_id, e.event_date AS hearing_date, ch.hearing_description, 
#                    ch.highlights, ch.created_at, c.case_number
#             FROM case_hearings ch
#             JOIN cases c ON ch.case_id = c.id
#             JOIN events e ON c.id = e.case_id  -- Assuming there is a case_id in the events table
#             WHERE c.case_number = %s
#             '''
#             cursor.execute(query, (case_number,))
#         else:
#             query = '''
#             SELECT ch.id, ch.case_id, e.event_date AS hearing_date, ch.hearing_description, 
#                    ch.highlights, ch.created_at, c.case_number
#             FROM case_hearings ch
#             JOIN cases c ON ch.case_id = c.id
#             JOIN events e ON c.id = e.case_id  -- Assuming there is a case_id in the events table
#             '''
#             cursor.execute(query)

#         # Fetch all hearing data
#         columns = [col[0] for col in cursor.description]
#         hearings = [dict(zip(columns, row)) for row in cursor.fetchall()]

#         cursor.close()
#         return render_template('manage_hearings.html', hearings=hearings)

#     except Exception as e:
#         return jsonify({'status': 'error', 'message': str(e)})




@admin_bp.route('/manage_hearings', methods=['GET'])
def admin_manage_hearings_list():
    case_number = request.args.get('case_number', '')

    try:
        cursor = mysql.connection.cursor()

        if case_number:
            query = '''
            SELECT ch.id, ch.case_id, e.event_date AS hearing_date, ch.hearing_description, 
                   ch.highlights, ch.created_at, c.case_number
            FROM case_hearings ch
            JOIN cases c ON ch.case_id = c.id
            JOIN events e ON c.id = e.case_id
            WHERE c.case_number = %s
            '''
            cursor.execute(query, (case_number,))
        else:
            query = '''
            SELECT ch.id, ch.case_id, e.event_date AS hearing_date, ch.hearing_description, 
                   ch.highlights, ch.created_at, c.case_number
            FROM case_hearings ch
            JOIN cases c ON ch.case_id = c.id
            JOIN events e ON c.id = e.case_id
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
        
        # Update hearing data
        query = '''
        UPDATE case_hearings
        SET hearing_description = %s, highlights = %s
        WHERE id = %s
        '''
        cursor.execute(query, (hearing_description, highlights, hearing_id))
        
        # Update the hearing date in the events table (assuming there's only one event per case)
        event_query = '''
        UPDATE events
        SET event_date = %s
        WHERE case_id = (SELECT case_id FROM case_hearings WHERE id = %s)
        '''
        cursor.execute(event_query, (hearing_date, hearing_id))
        
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

    
# @admin_bp.route('/case_documents', methods=['GET'])
# def case_documents():
#     try:
#         cursor = mysql.connection.cursor()
#         # Fetch all documents
#         cursor.execute('''
#             SELECT id, case_id, description, document 
#             FROM case_documents
#         ''')
#         documents = cursor.fetchall()
#         cursor.close()

#         # Render the template with the documents data
#         return render_template('case_documents.html', documents=documents)
    
#     except Exception as e:
#         return jsonify({'status': 'error', 'message': str(e)})


@admin_bp.route('/case_documents', methods=['GET'])
def case_documents():
    try:
        cursor = mysql.connection.cursor()
        # Fetch all documents along with case details
        cursor.execute('''
            SELECT cd.id, cd.case_id, c.case_number, c.case_title, cd.description, cd.document
            FROM case_documents cd
            JOIN cases c ON cd.case_id = c.id
        ''')
        documents = cursor.fetchall()
        cursor.close()

        # Render the template with the documents data
        return render_template('case_documents.html', documents=documents)
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})



@admin_bp.route('/dashboard')
def admin_dashboard():
    try:
        cursor = mysql.connection.cursor()
        
        # Query to count all users
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'Public'")
        total_users = cursor.fetchone()[0]
        
        # Query to count judges
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'Judge'")
        total_judges = cursor.fetchone()[0]
        
        # Query to count lawyers
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'Lawyer'")
        total_lawyers = cursor.fetchone()[0]

        # Query to count admins
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'Admin'")
        total_admins = cursor.fetchone()[0]

         # Query to count cases
        cursor.execute("SELECT COUNT(*) FROM cases")
        total_cases = cursor.fetchone()[0]

        # Query to count pending events
        cursor.execute("SELECT COUNT(*) FROM events")
        total_pending_events = cursor.fetchone()[0]
        
        # Query for event status distribution
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN status = 'scheduled' THEN 1 ELSE 0 END) AS scheduled,
                SUM(CASE WHEN status = 'finished' THEN 1 ELSE 0 END) AS finished
            FROM events
        """)
        event_status = cursor.fetchone()

        # Query to count cases by type
        query = """
        SELECT 
            SUM(CASE WHEN case_type = 'family' THEN 1 ELSE 0 END) AS family,
            SUM(CASE WHEN case_type = 'labor' THEN 1 ELSE 0 END) AS labor,
            SUM(CASE WHEN case_type = 'civil' THEN 1 ELSE 0 END) AS civil,
            SUM(CASE WHEN case_type = 'criminal' THEN 1 ELSE 0 END) AS criminal
        FROM cases
        """
        cursor.execute(query)
        case_counts = cursor.fetchone()  # (family, labor, civil, criminal)
        cursor.close()
        
        return render_template('admin_dashboard.html', 
                               total_users=total_users, 
                               total_judges=total_judges, 
                               total_lawyers=total_lawyers,
                               total_admins=total_admins,
                               total_cases=total_cases,
                               total_pending_events=total_pending_events,
                               event_status=event_status,
                               case_counts=case_counts)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@admin_bp.route('/admin_calendar')
def admin_calendar():
    return render_template('admin_calendar.html')

# Render scheduled events page
@admin_bp.route('/scheduled_events_admin')
def scheduled_events_admin():
    return render_template('scheduled_event_admin.html')


@admin_bp.route('/api/events_admin', methods=['GET', 'POST', 'PUT'])
def events_admin():
    db = mysql.connection
    cursor = db.cursor()
    
    if request.method == 'GET':
        # Fetching events with associated case details
        cursor.execute('''SELECT events.id, events.title, events.event_date, events.event_time, events.status, cases.case_number
                           FROM events
                           LEFT JOIN cases ON events.case_id = cases.id''')
        events = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        events = [dict(zip(columns, row)) for row in events]

        # Convert timedelta to string
        for event in events:
            for key, value in event.items():
                if isinstance(value, timedelta):
                    event[key] = str(value)
                    
        return jsonify(events)
    
    elif request.method == 'POST':
        # Creating a new event
        data = request.json
        title = data.get('title')
        case_number = data.get('case_number')
        event_date = data.get('event_date')
        event_time = data.get('event_time')
        status = data.get('status', 'scheduled')
        created_at = updated_at = datetime.now()
        
        try:
            # Validate the case number
            cursor.execute("SELECT id FROM cases WHERE case_number = %s", (case_number,))
            case = cursor.fetchone()
            if not case:
                return jsonify({'error': 'Invalid case number'}), 400
            
            case_id = case[0]  # Case ID for the provided case_number
            
            # Insert the event
            cursor.execute(
                "INSERT INTO events (title, event_date, event_time, status, case_id, created_at, updated_at) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (title, event_date, event_time, status, case_id, created_at, updated_at)
            )
            db.commit()
            return jsonify({'message': 'Event created successfully'}), 201
        except Exception as e:
            db.rollback()
            return jsonify({'error': str(e)}), 500

    elif request.method == 'PUT':
        # Updating the event status to 'finished'
        data = request.json
        event_id = data.get('id')
        status = data.get('status', 'finished')
        updated_at = datetime.now()
        
        try:
            # Update the event status
            cursor.execute(
                "UPDATE events SET status = %s, updated_at = %s WHERE id = %s",
                (status, updated_at, event_id)
            )
            db.commit()
            return jsonify({'message': 'Event updated successfully'}), 200
        except Exception as e:
            db.rollback()
            return jsonify({'error': str(e)}), 500



@admin_bp.route('/api/check_hearing_details/<int:event_id>', methods=['GET'])
def check_hearing_details(event_id):
    try:
        cursor = mysql.connection.cursor()
        
        # Query to check if hearing details exist for the given event ID
        query = '''
        SELECT id 
        FROM case_hearings
        WHERE id = %s
        '''
        cursor.execute(query, (event_id,))
        
        # Check if a record is found
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            return jsonify({"status": "success", "hearingSaved": True})
        else:
            return jsonify({"status": "success", "hearingSaved": False})
    
    except Exception as e:
        # Handle errors and return a JSON response
        return jsonify({"status": "error", "message": str(e)})

    
@admin_bp.route('/api/editevents_admin/<int:event_id>', methods=['PUT'])
def edit_event_admin(event_id):
    db = mysql.connection
    cursor = db.cursor()
    data = request.json
    title = data.get('title')
    case_number = data.get('case_number')  # Case number should be provided
    event_date = data.get('event_date')
    event_time = data.get('event_time')

    updated_at = datetime.now()

    try:
        # Fetch the case_id using the case_number
        cursor.execute("SELECT id FROM cases WHERE case_number = %s", (case_number,))
        case = cursor.fetchone()
        if not case:
            return jsonify({'error': 'Invalid case number'}), 400
        
        case_id = case[0]

        # Update the event
        cursor.execute(
            """
            UPDATE events 
            SET title = %s, case_id = %s, event_date = %s, event_time = %s, status = %s, updated_at = %s 
            WHERE id = %s
            """,
            (title, case_id, event_date, event_time, 'scheduled', updated_at, event_id)
        )
        db.commit()
        return jsonify({'message': 'Event updated successfully'})

    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/deleteevent_admin/<int:event_id>', methods=['DELETE'])
def delete_event_admin(event_id):
    db = mysql.connection
    cursor = db.cursor()
    
    try:
        # Delete the event by event_id
        cursor.execute("DELETE FROM events WHERE id = %s", (event_id,))
        db.commit()
        
        # Check if any row was affected (event found)
        if cursor.rowcount == 0:
            return jsonify({'error': 'Event not found'}), 404
        
        return jsonify({'message': 'Event deleted successfully'}), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

    

# # Update event status
# @admin_bp.route('/api/events_admin/<int:event_id>', methods=['PUT'])
# def update_event_admin(event_id):
#     db = mysql.connection
#     cursor = db.cursor()
#     data = request.json
#     status = data.get('status')
#     updated_at = datetime.now()  # Update the timestamp
    
#     try:
#         cursor.execute("UPDATE events SET status = %s, updated_at = %s WHERE id = %s", (status, updated_at, event_id))
#         db.commit()
#         return jsonify({'message': 'Event updated successfully'})
#     except Exception as e:
#         db.rollback()
#         return jsonify({'error': str(e)}), 500





