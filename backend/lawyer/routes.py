
from flask import Blueprint, render_template, session,redirect, url_for,jsonify,request,flash
from extensions import mysql
from datetime import timedelta,datetime
import MySQLdb
from werkzeug.security import generate_password_hash,check_password_hash

lawyer_bp = Blueprint('lawyer', __name__, template_folder="../../frontend/templates/lawyer")

@lawyer_bp.route('/')
def lawyer_index():
    return render_template('index_lawyer.html')



# # Route to display notifications page
# @lawyer_bp.route('/notifications', methods=['GET'])
# def lawyer_notifications():
#     if 'loggedin' in session:
#         user_id = session['user_id']
#         conn = mysql.connection
#         cursor = conn.cursor()

#         # Query to fetch notifications for the logged-in lawyer
#         cursor.execute('''
#             SELECT cn.case_id, cn.message, c.case_title, c.case_number, c.date, c.case_type,
#                    p.fullname AS plaintiff_name, d.fullname AS defendant_name, c.description
#             FROM lawyer_notification cn
#             JOIN cases c ON c.id = cn.case_id
#             LEFT JOIN users p ON p.username = c.plaintiff_name
#             LEFT JOIN users d ON d.username = c.defendant_name
#             WHERE cn.lawyer_id = %s
#         ''', (user_id,))

#         notifications = cursor.fetchall()
        
#         # Structure notifications into a list of dictionaries
#         notifications_list = []
#         for notification in notifications:
#             notifications_list.append({
#                 "case_id": notification[0],
#                 "message": notification[1],
#                 "case_title": notification[2],
#                 "case_number": notification[3],
#                 "date": notification[4],
#                 "type": notification[5],
#                 "plaintiff": notification[6],
#                 "defendant": notification[7],
#                 "description": notification[8]
#             })

#         return render_template('accept_reject_case.html', notifications=notifications_list)

#     return redirect(url_for('user.login'))




# Route to display notifications page
@lawyer_bp.route('/lawyer_notifications', methods=['GET'])
def lawyer_updated_notification():
    if 'loggedin' in session:
        user_id = session['user_id']
        conn = mysql.connection
        cursor = conn.cursor()

        # Query to fetch notifications for the logged-in lawyer
        cursor.execute('''
            SELECT cn.case_id, cn.message, c.case_title, c.case_number, c.date, c.case_type,
                   p.fullname AS plaintiff_name, d.fullname AS defendant_name, c.description
            FROM lawyer_notification cn
            JOIN cases c ON c.id = cn.case_id
            LEFT JOIN users p ON p.username = c.plaintiff_name
            LEFT JOIN users d ON d.username = c.defendant_name
            WHERE cn.lawyer_id = %s
        ''', (user_id,))

        notifications = cursor.fetchall()
        
        # Structure notifications into a list of dictionaries
        notifications_list = []
        for notification in notifications:
            notifications_list.append({
                "case_id": notification[0],
                "message": notification[1],
                "case_title": notification[2],
                "case_number": notification[3],
                "date": notification[4],
                "type": notification[5],
                "plaintiff": notification[6],
                "defendant": notification[7],
                "description": notification[8]
            })

        return render_template('lawyer_notification.html', notifications=notifications_list)

    return redirect(url_for('user.login'))



# Route to display notifications page
@lawyer_bp.route('/accept_reject_cases', methods=['GET'])
def lawyer_notifications():
    if 'loggedin' in session:
        user_id = session['user_id']
        conn = mysql.connection
        cursor = conn.cursor()

        # Query to fetch notifications along with their status for the logged-in lawyer
        cursor.execute('''
            SELECT cn.case_id, cn.message, cn.status, c.case_title, c.case_number, c.date, c.case_type,
                   p.fullname AS plaintiff_name, d.fullname AS defendant_name, c.description
            FROM lawyer_notification cn
            JOIN cases c ON c.id = cn.case_id
            LEFT JOIN users p ON p.username = c.plaintiff_name
            LEFT JOIN users d ON d.username = c.defendant_name
            WHERE cn.lawyer_id = %s
        ''', (user_id,))

        notifications = cursor.fetchall()
        
        # Structure notifications into a list of dictionaries with status
        notifications_list = []
        for notification in notifications:
            notifications_list.append({
                "case_id": notification[0],
                "message": notification[1],
                "status": notification[2],  # Include the status here
                "case_title": notification[3],
                "case_number": notification[4],
                "date": notification[5],
                "type": notification[6],
                "plaintiff": notification[7],
                "defendant": notification[8],
                "description": notification[9]
            })

        return render_template('accept_reject_case.html', notifications=notifications_list)

    return redirect(url_for('user.login'))




# # Route to handle accept/reject response from the lawyer
# @lawyer_bp.route('/respond_case', methods=['POST'])
# def respond_case():
#     data = request.json
#     case_id = data.get('case_id')
#     response = data.get('response')
#     user_id = session['user_id']  # Assuming you store user ID in the session

#     if not case_id or not response:
#         return jsonify({"success": False, "message": "Case ID and response are required."}), 400

#     conn = mysql.connection
#     cursor = conn.cursor()

#     # Check if the case exists and fetch its current status
#     cursor.execute(''' 
#         SELECT status FROM lawyer_notification 
#         WHERE case_id = %s AND lawyer_id = %s
#     ''', (case_id, user_id))
    
#     case = cursor.fetchone()

#     if not case:
#         return jsonify({"success": False, "message": "Case not found."}), 404

#     current_status = case[0]

#     # Prevent action if the case is already accepted or rejected
#     if current_status in ['accepted', 'rejected']:
#         return jsonify({"success": False, "message": "Action already taken. You cannot modify the response."}), 400

#     if response == "accept":
#         # Update the status of the case to 'accepted'
#         cursor.execute(''' 
#             UPDATE lawyer_notification 
#             SET status = 'accepted' 
#             WHERE case_id = %s AND lawyer_id = %s
#         ''', (case_id, user_id))
        
#         # Optionally, log the acceptance
#         print(f"Case ID {case_id} has been accepted by Lawyer ID {user_id}.")
#         conn.commit()
#         return jsonify({"success": True, "message": "Case accepted."})
        
#     elif response == "reject":
#         # Update the status of the case to 'rejected'
#         cursor.execute(''' 
#             UPDATE lawyer_notification 
#             SET status = 'rejected' 
#             WHERE case_id = %s AND lawyer_id = %s
#         ''', (case_id, user_id))
        
#         # Optionally, log the rejection
#         print(f"Case ID {case_id} has been rejected by Lawyer ID {user_id}.")
#         conn.commit()
#         return jsonify({"success": True, "message": "Case rejected."})

#     else:
#         return jsonify({"success": False, "message": "Invalid response."}), 400




@lawyer_bp.route('/respond_case', methods=['POST'])
def respond_case():
    data = request.json
    case_id = data.get('case_id')
    response = data.get('response')
    user_id = session['user_id']  # Assuming you store user ID in the session

    if not case_id or not response:
        return jsonify({"success": False, "message": "Case ID and response are required."}), 400

    conn = mysql.connection
    cursor = conn.cursor()

    # Check if the case exists and fetch its current status
    cursor.execute(''' 
        SELECT status FROM lawyer_notification 
        WHERE case_id = %s AND lawyer_id = %s
    ''', (case_id, user_id))
    
    case = cursor.fetchone()

    if not case:
        return jsonify({"success": False, "message": "Case not found."}), 404

    current_status = case[0]

    # Prevent action if the case is already accepted or rejected
    if current_status in ['accepted', 'rejected']:
        return jsonify({"success": False, "message": "Action already taken. You cannot modify the response."}), 400

    if response == "accept":
        # Update the status of the case to 'accepted'
        cursor.execute(''' 
            UPDATE lawyer_notification 
            SET status = 'accepted' 
            WHERE case_id = %s AND lawyer_id = %s
        ''', (case_id, user_id))
        
        conn.commit()
        return jsonify({"success": True, "message": "Case accepted."})
        
    elif response == "reject":
        # Update the status of the case to 'rejected'
        cursor.execute(''' 
            UPDATE lawyer_notification 
            SET status = 'rejected' 
            WHERE case_id = %s AND lawyer_id = %s
        ''', (case_id, user_id))
        
        conn.commit()
        return jsonify({"success": True, "message": "Case rejected."})

    else:
        return jsonify({"success": False, "message": "Invalid response."}), 400




@lawyer_bp.route('/my_cases', methods=['GET'])
def my_cases():
    if 'loggedin' in session:
        user_id = session['user_id']
        conn = mysql.connection
        cursor = conn.cursor()

        # Query to fetch cases assigned to the logged-in lawyer, including the client name
        cursor.execute(''' 
            SELECT cn.case_id, c.case_title, c.case_number, c.date, c.case_type,
                   p.fullname AS plaintiff_name, d.fullname AS defendant_name,
                   u.fullname AS client_name,  -- Added this line to get the client name
                   cn.status, cn.message
            FROM lawyer_notification cn
            JOIN cases c ON c.id = cn.case_id
            LEFT JOIN users p ON p.username = c.plaintiff_name
            LEFT JOIN users d ON d.username = c.defendant_name
            LEFT JOIN users u ON u.id = cn.client_id  -- Joining users table to get client name
            WHERE cn.lawyer_id = %s
        ''', (user_id,))

        cases = cursor.fetchall()
        
        # Structure cases into a list of dictionaries
        cases_list = []
        for case in cases:
            cases_list.append({
                "case_id": case[0],
                "case_title": case[1],
                "case_number": case[2],
                "date": case[3],
                "case_type": case[4],
                "plaintiff": case[5],
                "defendant": case[6],
                "client_name": case[7],  
                "status": case[8],
                "message": case[9]  
            })

        return render_template('lawyer/my_cases.html', cases=cases_list)

    return redirect(url_for('user.login'))


@lawyer_bp.route('/all_lawyers', methods=['GET'])
def display_all_lawyers():
    if 'loggedin' in session:
        conn = mysql.connection
        cursor = conn.cursor()

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

        return render_template('/display_lawyers.html', lawyers=lawyers_list)

    return redirect(url_for('user.login'))



# @lawyer_bp.route('/all_judges', methods=['GET'])
# def display_all_judges():
#     if 'loggedin' in session:
#         conn = mysql.connection
#         cursor = conn.cursor()

#         # Query to fetch all judges' details
#         cursor.execute('''
#             SELECT id, fullname, username, role, address, contact, email, nic, gender
#             FROM users 
#             WHERE role = 'Judge'
#         ''')

#         judges = cursor.fetchall()
        
#         # Structure judges into a list of dictionaries
#         judges_list = []
#         for judge in judges:
#             judges_list.append({
#                 "id": judge[0],
#                 "fullname": judge[1],
#                 "username": judge[2],
#                 "role": judge[3],
#                 "address": judge[4],
#                 "contact": judge[5],
#                 "email": judge[6],
#                 "nic": judge[7],
#                 "gender": judge[8]
#             })
            
#              # Debug statement to print lawyers in the terminal
#         print("Lawyers fetched from the database:")
#         for judge in judges_list:
#             print(judge)

#         return render_template('/display_judges.html', judges=judges_list)

#     return redirect(url_for('user.login'))





@lawyer_bp.route('/all_judges', methods=['GET'])
def display_all_judges():
    if 'loggedin' in session:
        conn = mysql.connection
        cursor = conn.cursor()

        search_query = request.args.get('search', '').strip()

        # Modify the query to fetch Judge based on search input
        if search_query:
            cursor.execute('''
                SELECT id, fullname, username, role, address, contact, email, nic, gender
                FROM users 
                WHERE role = 'Judge' AND fullname LIKE %s
            ''', ('%' + search_query + '%',))
        else:
            # Query to fetch all Judges' details if no search query is provided
            cursor.execute('''
                SELECT id, fullname, username, role, address, contact, email, nic, gender
                FROM users 
                WHERE role = 'Judge'
            ''')

        judges = cursor.fetchall()
        
        # Structure judges into a list of dictionaries
        judges_list = []
        for judges in judges:
            judges_list.append({
                "id": judges[0],
                "fullname": judges[1],
                "username": judges[2],
                "role": judges[3],
                "address": judges[4],
                "contact": judges[5],
                "email": judges[6],
                "nic": judges[7],
                "gender": judges[8]
            })

        return render_template('/display_judges.html', judges=judges_list)

    return redirect(url_for('user.login'))




@lawyer_bp.route('/change_password_lawyer', methods=['GET', 'POST'])
def change_password_user():
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
        return render_template('change_password_lawyer.html')

    return render_template('change_password_lawyer.html')


@lawyer_bp.route('/dashboard', methods=['GET'])
def lawyer_dashboard():
    if 'loggedin' in session and session['role'] == 'Lawyer':
        lawyer_id = session['user_id']
        cursor = None
        try:
            cursor = mysql.connection.cursor()

            # General statistics
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'Public'")
            total_users = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'Judge'")
            total_judges = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'Lawyer'")
            total_lawyers = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'Admin'")
            total_admins = cursor.fetchone()[0]

            # Lawyer-specific case count
            cursor.execute("""
                SELECT COUNT(*) AS case_count 
                FROM lawyer_notification 
                WHERE lawyer_id = %s
            """, (lawyer_id,))
            case_count = cursor.fetchone()[0]

            # Lawyer-specific unique client count
            cursor.execute("""
                SELECT COUNT(DISTINCT client_id) AS client_count 
                FROM lawyer_notification 
                WHERE lawyer_id = %s
            """, (lawyer_id,))
            client_count = cursor.fetchone()[0]

            return render_template(
                'lawyer_dashboard.html',
                total_users=total_users,
                total_judges=total_judges,
                total_lawyers=total_lawyers,
                total_admins=total_admins,
                case_count=case_count,
                client_count=client_count
            )
        
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
        
        finally:
            if cursor:
                cursor.close()

    return jsonify({'status': 'error', 'message': 'Unauthorized access'}), 401

@lawyer_bp.route('/case_status_counts', methods=['GET'])
def case_status_counts():
    if 'loggedin' in session and session['role'] == 'Lawyer':
        lawyer_id = session['user_id']
        conn = mysql.connection
        cursor = conn.cursor()

        # Query to count cases by their status
        cursor.execute("""
            SELECT 
                status, 
                COUNT(*) 
            FROM 
                lawyer_notification 
            WHERE 
                lawyer_id = %s 
            GROUP BY 
                status
        """, (lawyer_id,))

        status_counts = cursor.fetchall()

        # Structure the data
        status_data = {row[0]: row[1] for row in status_counts}

        # Ensure all statuses are included (default to 0 if missing)
        all_statuses = ['accepted', 'rejected', 'pending']
        response_data = {status: status_data.get(status, 0) for status in all_statuses}

        return jsonify(response_data)

    return jsonify({'status': 'error', 'message': 'Unauthorized access'}), 401

@lawyer_bp.route('/case_type_counts', methods=['GET'])
def get_case_type_counts():
    if 'loggedin' in session and session['role'] == 'Lawyer':
        lawyer_id = session['user_id']
        conn = mysql.connection
        cursor = conn.cursor()  # No need for DictCursor here

        # Query to fetch the case types and their counts for the logged-in lawyer
        cursor.execute("""
            SELECT c.case_type AS case_type, COUNT(*) AS case_count
            FROM cases c
            JOIN lawyer_notification ln ON c.id = ln.case_id
            WHERE ln.lawyer_id = %s
            GROUP BY c.case_type;
        """, (lawyer_id,))

        results = cursor.fetchall()
        cursor.close()

        # Check if results are empty
        if not results:
            return jsonify({'error': 'No case types found for this lawyer'}), 404

        # Prepare the data for JSON response
        case_data = {}
        for row in results:
            case_type = row[0]  # The first element in the tuple is case_type
            case_count = row[1]  # The second element in the tuple is case_count
            case_data[case_type] = case_count

        return jsonify(case_data)

    return jsonify({'error': 'Unauthorized access'}), 401



