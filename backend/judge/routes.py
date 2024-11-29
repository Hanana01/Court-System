from flask import Blueprint, render_template, request, jsonify, url_for, session, redirect, flash
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
@judge_bp.route('/scheduled-events')
def scheduled_events():
    return render_template('scheduled_event.html')

# Fetch or create events
@judge_bp.route('/api/events', methods=['GET', 'POST'])
def events():
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