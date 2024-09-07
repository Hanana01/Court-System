from flask import Blueprint, render_template, request, jsonify
from extensions import mysql
from datetime import timedelta

judge_bp = Blueprint('judge', __name__, template_folder='../../frontend/templates/judge')

@judge_bp.route('/')
def judge_index():
    return render_template('index_judge.html')

@judge_bp.route('/calendar')
def judge_calendar():
    return render_template('judge_calendar.html')

@judge_bp.route('/scheduled-events')
def scheduled_events():
    return render_template('scheduled_event.html')

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
        print("Received data:", data)  # Debugging: Log received data
        title = data.get('title')
        event_date = data.get('event_date')
        event_time = data.get('event_time')
        status = data.get('status', 'scheduled')
        judge_id = data.get('judge_id')
        try:
            cursor.execute(
                "INSERT INTO events (title, event_date, event_time, status, judge_id) VALUES (%s, %s, %s, %s, %s)",
                (title, event_date, event_time, status, judge_id)
            )
            db.commit()
            print("Event created successfully")  # Debugging: Log success
            return jsonify({'message': 'Event created successfully'}), 201
        except Exception as e:
            print("Error inserting event:", e)  # Debugging: Log error
            db.rollback()
            return jsonify({'error': str(e)}), 500

@judge_bp.route('/api/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    db = mysql.connection
    cursor = db.cursor()
    data = request.json
    status = data.get('status')
    try:
        cursor.execute("UPDATE events SET status = %s WHERE id = %s", (status, event_id))
        db.commit()
        return jsonify({'message': 'Event updated successfully'})
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    
@judge_bp.route('/api/editevents/<int:event_id>', methods=['PUT'])
def edit_event(event_id):
    db = mysql.connection
    cursor = db.cursor()
    data = request.json
    title = data.get('title')
    event_date = data.get('event_date')
    event_time = data.get('event_time')
    
    # Set the status to 'scheduled' when the event is edited
    status = 'scheduled'
    
    try:
        cursor.execute(
            "UPDATE events SET title = %s, event_date = %s, event_time = %s, status = %s WHERE id = %s",
            (title, event_date, event_time, status, event_id)
        )
        db.commit()
        return jsonify({'message': 'Event updated successfully'})
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

