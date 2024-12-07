import os
from flask import Blueprint, render_template, request, jsonify, url_for, session, redirect, flash, send_from_directory
from extensions import mysql
from datetime import timedelta,datetime
import MySQLdb
from werkzeug.security import generate_password_hash,check_password_hash

judge_bp = Blueprint('judge', __name__, template_folder='../../frontend/templates/judge')

@judge_bp.route('/')
def judge_index():
    return render_template('index_judge.html')

@judge_bp.route('/judge_calendar')
def judge_calendar():
    return render_template('judge_calendar.html')

# Render scheduled events page
@judge_bp.route('/scheduled_events')
def scheduled_events():
    return render_template('scheduled_event.html')

# Fetch or create events
@judge_bp.route('/api/events', methods=['GET', 'POST', 'PUT'])
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
        
        
@judge_bp.route('/get_cases', methods=['GET'])
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


# Edit an event
@judge_bp.route('/api/editevents/<int:event_id>', methods=['PUT'])
def edit_event(event_id):
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
@judge_bp.route('/api/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
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



@judge_bp.route('/all_lawyers', methods=['GET'])
def all_lawyers():
    if 'loggedin' in session:
        conn = mysql.connection
        cursor = conn.cursor()

        # Get the search query from the request, if any
        search_query = request.args.get('search', '').strip()

        # Modify the query to fetch lawyers based on search input
        if search_query:
            cursor.execute('''
                SELECT id, fullname, username, role, address, contact, email, nic, gender
                FROM users 
                WHERE role = 'lawyer' AND fullname LIKE %s
            ''', ('%' + search_query + '%',))
        else:
            # Query to fetch all lawyers' details if no search query is provided
            cursor.execute('''
                SELECT id, fullname, username, role, address, contact, email, nic, gender
                FROM users 
                WHERE role = 'lawyer'
            ''')

        lawyers = cursor.fetchall()
        
        # Structure lawyers into a list of dictionaries
        lawyers_list = []
        for lawyer in lawyers:
            lawyers_list.append({
                "id": lawyer[0],
                "fullname": lawyer[1],
                "username": lawyer[2],
                "role": lawyer[3],
                "address": lawyer[4],
                "contact": lawyer[5],
                "email": lawyer[6],
                "nic": lawyer[7],
                "gender": lawyer[8]
            })

        return render_template('/view_lawyers.html', lawyers=lawyers_list, search_query=search_query)

    return redirect(url_for('user.login'))




@judge_bp.route('/all_judges', methods=['GET'])
def all_judges():
    if 'loggedin' in session:
        conn = mysql.connection
        cursor = conn.cursor()

      # Get the search query from the request, if any
        search_query = request.args.get('search', '').strip()

        # Modify the query to fetch judges based on search input
        if search_query:
            cursor.execute('''
                SELECT id, fullname, username, role, address, contact, email, nic, gender
                FROM users 
                WHERE role = 'Judge' AND fullname LIKE %s
            ''', ('%' + search_query + '%',))
        else:
            # Query to fetch all judges' details if no search query is provided
            cursor.execute('''
                SELECT id, fullname, username, role, address, contact, email, nic, gender
                FROM users 
                WHERE role = 'Judge'
            ''')

        judges = cursor.fetchall()
        
        # Structure judges into a list of dictionaries
        judges_list = []
        for judge in judges:
            judges_list.append({
                "id": judge[0],
                "fullname": judge[1],
                "username": judge[2],
                "role": judge[3],
                "address": judge[4],
                "contact": judge[5],
                "email": judge[6],
                "nic": judge[7],
                "gender": judge[8]
            })
            
             # Debug statement to print judge in the terminal
        print("judges fetched from the database:")
        for judge in judges_list:
            print(judge)

        return render_template('/view_judges.html', judges=judges_list)

    return redirect(url_for('user.login'))




@judge_bp.route('/change_password_judge', methods=['GET', 'POST'])
def change_password_judge():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_new_password = request.form['confirm_new_password']

        if not current_password or not new_password or not confirm_new_password:
            flash('All fields are required.', 'error')
            return render_template('change_password_user.html')

        if new_password != confirm_new_password:
            flash('New passwords do not match.', 'error')
            return render_template('change_password_user.html')

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
        return render_template('change_password_judge.html')

    return render_template('change_password_judge.html')



@judge_bp.route('/dashboard')
def judge_dashboard():
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
        
        return render_template('judge_dashboard.html', 
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




# fetching for all cases
@judge_bp.route('/all_cases_judge', methods=['GET'])
def cases_judge():
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
        return render_template('all_cases_judge.html', cases=enriched_cases)
    except Exception as e:
        print("Error:", e)  # Print error details in terminal
        return jsonify({'status': 'error', 'message': str(e)})
    




@judge_bp.route('/view_cases/<int:case_id>', methods=['GET'])
def view_case_judge(case_id):
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



# Specify the folder where uploaded files will be stored
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')  # Define upload path
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'png'}  # Adjust the file types as needed

# Make sure the uploads directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@judge_bp.route('/case_documents_judge', methods=['GET'])
def case_documents_judge():
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
        return render_template('case_documents_judge.html', documents=documents)
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    

@judge_bp.route('/view_document/<int:document_id>')
def view_document_judge(document_id):
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
    
    
@judge_bp.route('/hearings', methods=['GET'])
def judge_hearings_list():
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
        return render_template('hearings_judge.html', hearings=hearings)
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
