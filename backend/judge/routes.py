from flask import Blueprint, render_template, request, jsonify
from extensions import mysql
from datetime import datetime, timedelta

judge_bp = Blueprint('judge', __name__, template_folder='../../frontend/templates/judge')

# Render judge index page
@judge_bp.route('/')
def judge_index():
    return render_template('index_judge.html')

# Render judge calendar page
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

# Delete an event
@judge_bp.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    db = mysql.connection
    cursor = db.cursor()
    
    try:
        cursor.execute("DELETE FROM events WHERE id = %s", (event_id,))
        db.commit()
        return jsonify({'message': 'Event deleted successfully'})
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

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

    

   
