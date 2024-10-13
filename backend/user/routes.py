from flask import Blueprint, render_template, session,redirect, url_for,jsonify,request,flash
from extensions import mysql

user_bp = Blueprint('user', __name__, template_folder="../../frontend/templates/user")

@user_bp.route('/')
def user_index():
    return render_template('index_user.html')

from flask import session, jsonify, redirect


@user_bp.route('/all_notifications', methods=['GET'])
def get_notifications():
    if 'loggedin' in session:
        user_id = session['user_id']
        conn = mysql.connection
        cursor = conn.cursor()

        # Select notifications from the database
        cursor.execute("SELECT id, message, created_at, is_read FROM notifications WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
        rows = cursor.fetchall()

        # Convert fetched data into a list of dictionaries
        notifications = []
        for row in rows:
            notification = {
                'id': row[0],  # Notification ID
                'message': row[1],
                'created_at': row[2],
                'is_read': row[3]  # Read status
            }
            notifications.append(notification)

        return render_template('notifications.html', notifications=notifications)

    return {
        'status': 'error',
        'message': 'User not logged in'
    }

@user_bp.route('/mark_as_read/<int:notification_id>', methods=['GET'])
def mark_as_read(notification_id):
    if 'loggedin' in session:
        user_id = session['user_id']
        conn = mysql.connection
        cursor = conn.cursor()

        # Update the notification's read status
        cursor.execute("UPDATE notifications SET is_read = TRUE WHERE id = %s AND user_id = %s", (notification_id, user_id))
        conn.commit()

        return redirect(url_for('user.get_notifications'))

    return {
        'status': 'error',
        'message': 'User not logged in'
    }

@user_bp.route('/check_notifications', methods=['GET'])
def check_notifications():
    if 'loggedin' in session:
        user_id = session['user_id']
        conn = mysql.connection
        cursor = conn.cursor()

        # Query to count unread notifications for the user
        cursor.execute("SELECT COUNT(*) FROM notifications WHERE user_id = %s AND is_read = FALSE", (user_id,))
        unread_count = cursor.fetchone()[0]

        return jsonify({
            'status': 'success',
            'unread_notifications': unread_count
        })

    return jsonify({
        'status': 'error',
        'message': 'User not logged in'
    })
  

@user_bp.route('/my_cases', methods=['GET', 'POST'])
def my_cases():
    if 'loggedin' in session:
        user_id = session['user_id']
        username = session['username']
        conn = mysql.connection
        cursor = conn.cursor()

        # Query to get all cases associated with the user (as plaintiff or defendant)
        cursor.execute(''' 
            SELECT c.case_title, c.case_number, c.date, c.case_type, 
                   p.fullname AS plaintiff_name, d.fullname AS defendant_name, 
                   c.description, c.id AS case_id
            FROM cases c
            LEFT JOIN users p ON p.username = c.plaintiff_name
            LEFT JOIN users d ON d.username = c.defendant_name
            WHERE p.username = %s OR d.username = %s
        ''', (username, username))

        cases = cursor.fetchall()

        # Fetch all lawyers
        cursor.execute(''' 
            SELECT id, fullname FROM users WHERE role = 'Lawyer'
        ''')
        lawyers = cursor.fetchall()

        if request.method == 'POST':
            # Logic to assign a lawyer
            data = request.get_json()  # Parse the JSON data from the request
            selected_lawyer_id = data.get('lawyer_id')
            case_id = data.get('case_id')
            client_id = user_id  # The currently logged-in user

            if selected_lawyer_id and case_id:
                # Insert a record into the lawyer_notification table to assign a lawyer
                message = f'You have been assigned to the case with ID {case_id}.'
                
                cursor.execute(''' 
                    INSERT INTO lawyer_notification (lawyer_id, case_id, client_id, message, status)
                    VALUES (%s, %s, %s, %s, 'pending')
                ''', (selected_lawyer_id, case_id, client_id, message))
                conn.commit()

                return jsonify(success=True)  # Return success response as JSON

        return render_template('my_cases.html', cases=cases, lawyers=lawyers)

    return redirect(url_for('user.login'))



@user_bp.route('/view_case/<case_number>', methods=['GET'])
def view_case(case_number):
    if 'loggedin' in session:
        conn = mysql.connection
        cursor = conn.cursor()

        # Query to get the full details of the case based on the case number
        cursor.execute('''
            SELECT c.case_title, c.case_number, c.date, c.case_type, 
                   c.plaintiff_name, c.defendant_name, c.description
            FROM cases c
            WHERE c.case_number = %s
        ''', (case_number,))
        
        case_details = cursor.fetchone()
        cursor.close()

        if case_details:
            return render_template('view_case.html', case=case_details)
        else:
            return "Case not found", 404

    return redirect(url_for('login'))  

