from flask import Blueprint, render_template, session,redirect, url_for,jsonify
from extensions import mysql

user_bp = Blueprint('user', __name__, template_folder="../../frontend/templates/user")

@user_bp.route('/')
def user_index():
    return render_template('index_user.html')

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