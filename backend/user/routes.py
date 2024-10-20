from flask import Blueprint, render_template, session,redirect, url_for,jsonify,request,flash
from extensions import mysql

user_bp = Blueprint('user', __name__, template_folder="../../frontend/templates/user")

@user_bp.route('/')
def user_index():
    return render_template('index_user.html')

from flask import session, jsonify, redirect


@user_bp.route('/lawyers', methods=['GET'])
def display_lawyers():
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

        return render_template('/lawyers.html', lawyers=lawyers_list, search_query=search_query)

    return redirect(url_for('user.login'))




@user_bp.route('/judges', methods=['GET'])
def display_judges():
    if 'loggedin' in session:
        conn = mysql.connection
        cursor = conn.cursor()

        # Query to fetch all judges' details
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
            
             # Debug statement to print lawyers in the terminal
        print("Lawyers fetched from the database:")
        for judge in judges_list:
            print(judge)

        return render_template('/judges.html', judges=judges_list)

    return redirect(url_for('user.login'))


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
  

# @user_bp.route('/my_cases', methods=['GET', 'POST'])
# def my_cases():
#     if 'loggedin' in session:
#         user_id = session['user_id']
#         username = session['username']
#         conn = mysql.connection
#         cursor = conn.cursor()

#         # Query to get distinct cases associated with the user (as plaintiff or defendant)
#         cursor.execute(''' 
#             SELECT DISTINCT c.case_title, c.case_number, c.date, c.case_type, 
#                    p.fullname AS plaintiff_name, d.fullname AS defendant_name, 
#                    c.description, c.id AS case_id, ln.status AS lawyer_status
#             FROM cases c
#             LEFT JOIN users p ON p.username = c.plaintiff_name
#             LEFT JOIN users d ON d.username = c.defendant_name
#             LEFT JOIN (
#                 SELECT case_id, MAX(id) AS latest_notification_id
#                 FROM lawyer_notification
#                 WHERE client_id = %s
#                 GROUP BY case_id
#             ) ln_sub ON ln_sub.case_id = c.id
#             LEFT JOIN lawyer_notification ln ON ln.id = ln_sub.latest_notification_id
#             WHERE p.username = %s OR d.username = %s
#         ''', (user_id, username, username))

#         cases = cursor.fetchall()

#         # Fetch all lawyers
#         cursor.execute(''' 
#             SELECT id, fullname FROM users WHERE role = 'Lawyer'
#         ''')
#         lawyers = cursor.fetchall()

#         if request.method == 'POST':
#             # Logic to assign a lawyer
#             data = request.get_json()  # Parse the JSON data from the request
#             selected_lawyer_id = data.get('lawyer_id')
#             case_id = data.get('case_id')

#             if selected_lawyer_id and case_id:
#                 # Check if the case has been rejected or has no status yet
#                 cursor.execute(''' 
#                     SELECT status FROM lawyer_notification 
#                     WHERE case_id = %s AND client_id = %s
#                 ''', (case_id, user_id))
#                 case_status = cursor.fetchone()

#                 # Only allow selecting a lawyer if the case is rejected or has no status
#                 if not case_status or case_status[0] == 'rejected':
#                     message = f'You have been assigned to the case with ID {case_id}.'
                    
#                     # Insert a record into the lawyer_notification table to assign a lawyer
#                     cursor.execute(''' 
#                         INSERT INTO lawyer_notification (lawyer_id, case_id, client_id, message, status)
#                         VALUES (%s, %s, %s, %s, 'pending')
#                     ''', (selected_lawyer_id, case_id, user_id, message))
#                     conn.commit()

#                     return jsonify(success=True)  # Return success response as JSON

#         return render_template('my_cases.html', cases=cases, lawyers=lawyers)

#     return redirect(url_for('user.login'))





@user_bp.route('/my_cases', methods=['GET', 'POST'])
def my_cases():
    if 'loggedin' in session:
        user_id = session['user_id']
        username = session['username']
        conn = mysql.connection
        cursor = conn.cursor()

        # Query to get distinct cases associated with the user (as plaintiff or defendant)
        cursor.execute(''' 
            SELECT DISTINCT c.case_title, c.case_number, c.date, c.case_type, 
                   p.fullname AS plaintiff_name, d.fullname AS defendant_name, 
                   c.description, c.id AS case_id, ln.status AS lawyer_status
            FROM cases c
            LEFT JOIN users p ON p.username = c.plaintiff_name
            LEFT JOIN users d ON d.username = c.defendant_name
            LEFT JOIN (
                SELECT case_id, MAX(id) AS latest_notification_id
                FROM lawyer_notification
                WHERE client_id = %s
                GROUP BY case_id
            ) ln_sub ON ln_sub.case_id = c.id
            LEFT JOIN lawyer_notification ln ON ln.id = ln_sub.latest_notification_id
            WHERE p.username = %s OR d.username = %s
        ''', (user_id, username, username))

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

            if selected_lawyer_id and case_id:
                # Check the status of the lawyer notification
                cursor.execute(''' 
                    SELECT status FROM lawyer_notification 
                    WHERE case_id = %s AND client_id = %s
                ''', (case_id, user_id))
                case_status = cursor.fetchone()

                # Only allow selecting a lawyer if the case is rejected or has no status
                if not case_status or case_status[0] == 'rejected':
                    message = f'You have been assigned to the case with ID {case_id}.'
                    
                    # Insert a record into the lawyer_notification table to assign a lawyer
                    cursor.execute(''' 
                        INSERT INTO lawyer_notification (lawyer_id, case_id, client_id, message, status)
                        VALUES (%s, %s, %s, %s, 'pending')
                    ''', (selected_lawyer_id, case_id, user_id, message))
                    conn.commit()

                    return jsonify(success=True)  # Return success response as JSON
                elif case_status[0] == 'pending':
                    # Handle case where the status is already pending
                    return jsonify(success=False, message="Lawyer assignment is pending.")  # Return pending status

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

