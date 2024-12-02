import os
from werkzeug.utils import secure_filename
from extensions import mysql
from werkzeug.security import generate_password_hash
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, send_from_directory



admin_bp = Blueprint('admin', __name__, template_folder="../../frontend/templates/admin")

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
    

@admin_bp.route('/all_cases', methods=['GET'])
def cases():
    try:
        cursor = mysql.connection.cursor()
        # Query to get case title, plaintiff name, and defendant name
        cursor.execute('''
            SELECT id, plaintiff_name, defendant_name 
            FROM cases
        ''')
        cases = cursor.fetchall()
        cursor.close()

        # Pass the cases data to the template
        return render_template('all_cases.html', cases=cases)
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


@admin_bp.route('/calendar')
def admin_calendar():
    return render_template('admin_calendar.html')

@admin_bp.route('/all_cases')
def all_cases():
    return render_template('all_cases.html')




